"""Build passage chunks from existing Markdown documents."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import requests

from representations.common import StageResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
CHUNKING_URL = os.getenv("CHUNKING_URL", "http://localhost:8085")


def _validate_chunk_data(data: Any, source: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{source}: chunk response must be an object")
    chunks = data.get("chunk_list")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError(f"{source}: chunk_list must be a non-empty array")
    if not all(isinstance(chunk, str) and chunk.strip() for chunk in chunks):
        raise ValueError(f"{source}: chunk_list must contain non-blank strings")

    count = len(chunks)
    declared_count = data.get("chunk_size")
    if declared_count is not None and declared_count != count:
        raise ValueError(f"{source}: chunk_size must equal {count}")
    for field in ("chunk_title", "token_count"):
        values = data.get(field)
        if values is not None and (
            not isinstance(values, list) or len(values) != count
        ):
            raise ValueError(f"{source}: {field} must contain {count} items")
    return data


def _atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def run(
    data_root: Path = DEFAULT_DATA_ROOT,
    *,
    skip_existing: bool = False,
) -> StageResult:
    """Build passage representations for every parsed Markdown document."""

    started = perf_counter()
    data_root = data_root.resolve()
    chunks_dir = data_root / "passages_chunk"
    markdown_dir = data_root / "pdf_parsed_output"

    markdown_files = (
        sorted(markdown_dir.glob("*.md")) if markdown_dir.is_dir() else []
    )
    if not markdown_files:
        raise RuntimeError(f"No parsed Markdown files found in {markdown_dir}")
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunk_count = 0
    for markdown_file in markdown_files:
        chunks_path = chunks_dir / f"{markdown_file.stem}_chunks.json"
        content = markdown_file.read_text(encoding="utf-8")

        if skip_existing and chunks_path.is_file():
            chunk_data = json.loads(chunks_path.read_text(encoding="utf-8"))
            print(f"{markdown_file.name}: reusing passage chunks")
        elif markdown_file.stem.startswith(
            ("chat-", "email-", "event-", "note-")
        ):
            # These are short enough that we don't need to chunk them.
            chunk_data = {
                "chunk_list": [content],
                "chunk_size": 1,
                "chunk_title": [markdown_file.stem],
                "token_count": [len(content.split())],
            }
            _atomic_write_json(chunks_path, chunk_data)
        else:
            chunk_response = requests.post(
                f"{CHUNKING_URL.rstrip('/')}/services/chunking/doc",
                data={
                    "content_parsed": content,
                    "min_split_tokens": 200,
                    "max_split_tokens": 500,
                    "split_tokens_tolerance": 50,
                    "window_size": 5,
                },
                timeout=(10, 300),
            )
            chunk_response.raise_for_status()
            chunk_data = _validate_chunk_data(
                chunk_response.json(),
                markdown_file,
            )
            _atomic_write_json(chunks_path, chunk_data)
        chunk_count += len(chunk_data["chunk_list"])
        print(
            f"{markdown_file.name}: "
            f"{len(chunk_data['chunk_list'])} passage chunks"
        )

    return StageResult(
        stage="passages",
        duration_seconds=perf_counter() - started,
        counts={"documents": len(markdown_files), "chunks": chunk_count},
    )


def main() -> None:
    result = run()
    print(
        f"Passages complete in {result.duration_seconds:.2f}s: "
        f"{result.counts}"
    )


if __name__ == "__main__":
    main()
