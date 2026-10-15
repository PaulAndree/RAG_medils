"""Extract and normalize document-level entity graphs with Ollama."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import requests

from representations.common import StageResult
from representations.graph.normalizer import normalize_document_graph


MODEL = os.getenv("GRAPH_MODEL", "qwen3:14b")
OLLAMA_URL = os.getenv(
    "GRAPH_OLLAMA_URL",
    os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = Path(__file__).resolve().parent / "prompts"
CHUNKS_DIR = PROJECT_ROOT / "data" / "arguments" / "chunks_for_arguments"
ENTITIES_DIR = PROJECT_ROOT / "data" / "entities"


def extract_triplets(
    chunk: str,
    title: str,
    chunk_id: int,
    document_id: str,
) -> dict[str, Any]:
    user_template = (PROMPT_DIR / "entity_extraction_usr.txt").read_text(
        encoding="utf-8"
    )
    system_prompt = (PROMPT_DIR / "entity_extraction_sys.txt").read_text(
        encoding="utf-8"
    )
    user_prompt = user_template.format(
        document_id=document_id,
        chunk_id=chunk_id,
        document_title=title,
        chunk_text=chunk,
    )

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
            "think": False,
            "options": {"temperature": 0},
        },
        timeout=(10, 900),
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("entity extraction response must be an object")
    return data


def _load_chunks(path: Path) -> tuple[list[str], list[str | None]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path}: top-level value must be an object")

    chunks = document.get("chunk_list")
    titles = document.get("chunk_title")
    if not isinstance(chunks, list) or not all(
        isinstance(chunk, str) and chunk.strip() for chunk in chunks
    ):
        raise ValueError(f"{path}: chunk_list must contain nonblank strings")
    if titles is None:
        titles = [None] * len(chunks)
    if not isinstance(titles, list) or len(titles) != len(chunks):
        raise ValueError(
            f"{path}: chunk_title must match the number of chunks"
        )
    if not all(title is None or isinstance(title, str) for title in titles):
        raise ValueError(f"{path}: chunk titles must be strings or null")
    return chunks, titles


def _save_results(path: Path, results: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(path)


def run(
    data_root: Path = PROJECT_ROOT / "data",
    *,
    skip_existing: bool = False,
) -> StageResult:
    """Build normalized graph representations for argument chunks."""

    started = perf_counter()
    data_root = data_root.resolve()
    chunks_dir = data_root / "arguments" / "chunks_for_arguments"
    entities_dir = data_root / "entities"
    chunk_files = (
        sorted(chunks_dir.glob("*_chunks.json"))
        if chunks_dir.is_dir()
        else []
    )
    if not chunk_files:
        raise RuntimeError(f"No argument chunk files found in {chunks_dir}")

    total_entities = 0
    total_relations = 0
    skipped_documents = 0
    for chunk_json_file in chunk_files:
        output_path = entities_dir / f"{chunk_json_file.stem}_entities.json"
        if skip_existing and output_path.is_file():
            skipped_documents += 1
            print(f"{chunk_json_file.name}: reusing graph")
            continue

        chunks, titles = _load_chunks(chunk_json_file)
        results: list[dict[str, Any]] = []

        for chunk_id, (chunk, title) in enumerate(
            zip(chunks, titles, strict=True)
        ):
            extraction = extract_triplets(
                chunk=chunk,
                title=title or "Unknown Title",
                chunk_id=chunk_id,
                document_id=chunk_json_file.stem,
            )
            results.append({**extraction, "chunk_id": chunk_id})

        extracted_entity_count = sum(
            len(result.get("entities", []))
            for result in results
        )
        extracted_relation_count = sum(
            len(result.get("relations", []))
            for result in results
        )
        normalized_results = normalize_document_graph(
            results=results,
            chunk_texts=chunks,
            document_id=chunk_json_file.stem,
        )
        _save_results(output_path, normalized_results)
        entity_count = sum(
            len(result["entities"])
            for result in normalized_results
        )
        relation_count = sum(
            len(result["relations"])
            for result in normalized_results
        )
        total_entities += entity_count
        total_relations += relation_count
        print(
            f"{chunk_json_file.name}: saved {entity_count} entities and "
            f"{relation_count} relations; filtered "
            f"{extracted_entity_count - entity_count} entities and "
            f"{extracted_relation_count - relation_count} relations"
        )

    if total_entities == 0 and skipped_documents == 0:
        raise RuntimeError("Graph extraction produced no entities")

    return StageResult(
        stage="graph",
        duration_seconds=perf_counter() - started,
        counts={
            "documents": len(chunk_files),
            "entities": total_entities,
            "relations": total_relations,
        },
    )


def main() -> None:
    result = run()
    print(
        f"Graph complete in {result.duration_seconds:.2f}s: "
        f"{result.counts}"
    )


if __name__ == "__main__":
    main()
