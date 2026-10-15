"""Build argument chunks and extract claim/evidence arguments with Ollama."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import perf_counter, sleep
from typing import Any

import requests

from representations.arguments.chunk_builder import chunker
from representations.common import StageResult


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
OLLAMA_URL = os.getenv("ARGUMENT_OLLAMA_URL", "http://localhost:11435")
MODEL = os.getenv("ARGUMENT_MODEL", "qwen3:14b")


def extract_arguments(
    chunk_list: list[str],
    document_id: str,
    output_path: Path,
    *,
    ollama_url: str = OLLAMA_URL,
    model: str = MODEL,
) -> list[dict[str, Any]]:
    """Extract arguments from chunks and save them as JSON."""

    user_template = (PROMPT_DIR / "user_extraction_prompt.txt").read_text(
        encoding="utf-8"
    )
    system_prompt = (PROMPT_DIR / "system_extraction_prompt.txt").read_text(
        encoding="utf-8"
    )

    if not chunk_list:
        raise ValueError(f"{document_id}: argument chunk list is empty")

    arguments: list[dict[str, Any]] = []

    # Argument IDs are one-based because stores.ingestion maps chunk N to
    # zero-based chunk index N - 1.
    for chunk_number, chunk_text in enumerate(chunk_list, start=1):
        chunk_id = f"{document_id}_chunk_{chunk_number}"
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            print(
                f"{document_id}: chunk {chunk_number}/{len(chunk_list)}, "
                f"attempt {attempt}/{max_attempts}"
            )

            try:
                response = requests.post(
                    f"{ollama_url.rstrip('/')}/api/generate",
                    json={
                        "model": model,
                        "prompt": user_template.format(
                            section_id=chunk_id,
                            chunk_text=chunk_text,
                        ),
                        "system": system_prompt,
                        "format": "json",
                        "stream": False,
                        "think": False,
                        "options": {
                            "temperature": 0,
                            "num_predict": 2048,
                        },
                    },
                    timeout=(10, 600),
                )
                response.raise_for_status()

                ollama_result = response.json()
                generated = json.loads(ollama_result["response"])
                extracted = generated.get("arguments")

                if not isinstance(extracted, list):
                    raise ValueError("response has no arguments array")

                break

            except (
                requests.exceptions.RequestException,
                json.JSONDecodeError,
                KeyError,
                ValueError,
            ) as exc:
                if attempt == max_attempts:
                    raise RuntimeError(
                        f"{chunk_id}: failed after {max_attempts} attempts"
                    ) from exc

                delay = 5 * attempt
                print(
                    f"{chunk_id}: invalid response: {exc}; "
                    f"retrying in {delay}s"
                )
                sleep(delay)

        for number, argument in enumerate(extracted, start=1):
            if not isinstance(argument, dict):
                raise ValueError(f"{chunk_id}: argument {number} is not an object")
            normalized = dict(argument)
            normalized["id"] = f"{chunk_id}_arg_{number}"
            arguments.append(normalized)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(arguments, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return arguments


def run(
    data_root: Path = DEFAULT_DATA_ROOT,
    *,
    skip_existing: bool = False,
) -> StageResult:
    """Build argument representations for every parsed Markdown document."""

    started = perf_counter()
    data_root = data_root.resolve()
    input_dir = data_root / "pdf_parsed_output"
    chunks_dir = data_root / "arguments" / "chunks_for_arguments"
    arguments_dir = data_root / "arguments" / "arguments_extracted"

    markdown_files = sorted(input_dir.glob("*.md")) if input_dir.is_dir() else []
    if not markdown_files:
        raise RuntimeError(f"No parsed Markdown files found in {input_dir}")

    chunk_count = 0
    argument_count = 0
    for markdown_file in markdown_files:
        chunks_path = chunks_dir / f"{markdown_file.stem}_chunks.json"
        output_path = arguments_dir / f"{markdown_file.stem}_arguments.json"

        if skip_existing and chunks_path.is_file():
            chunk_data = json.loads(chunks_path.read_text(encoding="utf-8"))
            print(f"{markdown_file.name}: reusing argument chunks")
        else:
            chunk_data = chunker(markdown_file, chunks_dir)
        chunks = chunk_data.get("chunk_list")
        if not isinstance(chunks, list) or not chunks:
            raise ValueError(f"{markdown_file}: argument chunker returned no chunks")
        if skip_existing and output_path.is_file():
            arguments = json.loads(output_path.read_text(encoding="utf-8"))
            print(f"{markdown_file.name}: reusing extracted arguments")
        else:
            arguments = extract_arguments(
                chunks,
                markdown_file.stem,
                output_path,
            )
        chunk_count += len(chunks)
        argument_count += len(arguments)
        print(f"{markdown_file.name}: {len(arguments)} arguments")

    if argument_count == 0:
        raise RuntimeError("Argument extraction produced no arguments")

    return StageResult(
        stage="arguments",
        duration_seconds=perf_counter() - started,
        counts={
            "documents": len(markdown_files),
            "chunks": chunk_count,
            "arguments": argument_count,
        },
    )


def main() -> None:
    result = run()
    print(
        f"Arguments complete in {result.duration_seconds:.2f}s: "
        f"{result.counts}"
    )


if __name__ == "__main__":
    main()
