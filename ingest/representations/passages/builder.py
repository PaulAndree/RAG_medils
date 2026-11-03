"""Build passage chunks from existing Markdown documents."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import requests

from RAG_medils.ingest.representations.common import StageResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "ingest" / "data"
CHUNKING_URL = os.getenv("CHUNKING_URL", "http://localhost:8085")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "16384"))
SHORT_DOCUMENT_TOKEN_LIMIT = 500
SHORT_DOCUMENT_SUMMARY_MAX_TOKENS = 450

SHORT_DOCUMENT_SUMMARY_PROMPT = """Summarize the source content so it fits in
fewer than 500 tokens. Preserve the important facts, participants, dates,
decisions, relationships, conditions, limitations, and uncertainty. Write in
the same language as the source. Use only the source content and return only
the summary."""


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


def _summarize_short_document(content: str, source: Path) -> tuple[str, int]:
    response = requests.post(
        f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat",
        json={
            "model": OLLAMA_GENERATION_MODEL,
            "messages": [
                {"role": "system", "content": SHORT_DOCUMENT_SUMMARY_PROMPT},
                {"role": "user", "content": content},
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "num_ctx": OLLAMA_NUM_CTX,
                "num_predict": SHORT_DOCUMENT_SUMMARY_MAX_TOKENS,
            },
        },
        timeout=(10, 600),
    )
    response.raise_for_status()
    result = response.json()
    message = result.get("message")
    summary = message.get("content") if isinstance(message, dict) else None
    if not isinstance(summary, str) or not summary.strip():
        raise RuntimeError(f"Ollama returned an empty summary for {source}")

    summary = summary.strip()
    output_tokens = result.get("eval_count")
    if not isinstance(output_tokens, int) or isinstance(output_tokens, bool):
        output_tokens = len(summary.split())
    if output_tokens >= SHORT_DOCUMENT_TOKEN_LIMIT:
        raise RuntimeError(
            f"Ollama summary for {source} has {output_tokens} tokens; "
            f"expected fewer than {SHORT_DOCUMENT_TOKEN_LIMIT}"
        )
    return summary, output_tokens


def chunk_document(markdown_file: Path) -> dict[str, Any]:
    """Chunk one Markdown document and return the validated API payload."""

    content = markdown_file.read_text(encoding="utf-8")
    if markdown_file.stem.startswith(
        ("chat-", "email-", "event-", "note-")
    ):
        token_count = len(content.split())
        if token_count >= SHORT_DOCUMENT_TOKEN_LIMIT:
            content, token_count = _summarize_short_document(
                content,
                markdown_file,
            )
        return {
            "chunk_list": [content],
            "chunk_size": 1,
            "chunk_title": [markdown_file.stem],
            "token_count": [token_count],
        }

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
    return _validate_chunk_data(chunk_response.json(), markdown_file)


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

        if skip_existing and chunks_path.is_file():
            chunk_data = json.loads(chunks_path.read_text(encoding="utf-8"))
            print(f"{markdown_file.name}: reusing passage chunks")
        else:
            chunk_data = chunk_document(markdown_file)
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
