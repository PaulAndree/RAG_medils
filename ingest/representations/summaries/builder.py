from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
from threading import BoundedSemaphore
from time import perf_counter
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import requests
from langchain_ollama import ChatOllama

from RAG_medils.ingest.representations.common import DocumentInput, StageResult
from RAG_medils.ingest.representations.passages.builder import chunk_document
from RAG_medils.ingest.representations.summaries.raptor_clustering import perform_clustering


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# This must match stores.ingestion so summary provenance points at the passage
# IDs that will be created when a fresh input snapshot is ingested.
DOCUMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/sql-rag/documents",
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11436")
GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "16384"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "2024"))
SUMMARY_INPUT_TOKEN_LIMIT = int(
    os.getenv("SUMMARY_INPUT_TOKEN_LIMIT", "13500")
)

if SUMMARY_INPUT_TOKEN_LIMIT + OLLAMA_NUM_PREDICT > OLLAMA_NUM_CTX:
    raise ValueError(
        "SUMMARY_INPUT_TOKEN_LIMIT + OLLAMA_NUM_PREDICT must not exceed "
        "OLLAMA_NUM_CTX"
    )

#external embedding service for RAPTOR summaries
EMBEDDING_URL = os.getenv(
    "EMBEDDING_URL",
    "http://127.0.0.1:8089/embed",
)
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "bge-m3",
)

MIN_NODES_FOR_NEXT_LEVEL = 10
CLUSTER_THRESHOLD = 0.3
REDUCTION_DIMENSION = 10
RAPTOR_MAX_WORKERS = int(os.getenv("RAPTOR_MAX_WORKERS", "2"))

if RAPTOR_MAX_WORKERS < 1:
    raise ValueError("RAPTOR_MAX_WORKERS must be at least 1")

_LLM_SEMAPHORE = BoundedSemaphore(RAPTOR_MAX_WORKERS)

# Chunk files without a catalog_id are assigned to this default catalog. Fill
# this mapping when the input directory contains more than one catalog.
DEFAULT_CATALOG_ID = os.getenv("CATALOG_ID", "default_catalog")
DOCUMENT_CATALOG_IDS: dict[str, str] = {}

OUTPUT_DIR = PROJECT_ROOT / "ingest" / "data" / "summaries"


# -----------------------------------------------------------------------------
# Clients and prompt
# -----------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _llm() -> ChatOllama:
    return ChatOllama(
        model=GENERATION_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
        num_ctx=OLLAMA_NUM_CTX,
        num_predict=OLLAMA_NUM_PREDICT,
    )


def _embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = requests.post(
        EMBEDDING_URL,
        json={
            "texts": texts,
            "model": EMBEDDING_MODEL,
            "input_type": "passage",
            "normalize": True,
        },
        timeout=(10, 600),
    )
    response.raise_for_status()
    result = response.json()
    embeddings = result.get("embeddings")

    if result.get("kind") != "dense" or not isinstance(embeddings, list):
        raise RuntimeError("Embedding API did not return dense embeddings")
    if len(embeddings) != len(texts):
        raise RuntimeError(
            f"Embedding API returned {len(embeddings)} vectors for "
            f"{len(texts)} texts"
        )

    return embeddings

SYSTEM_PROMPT = """You summarize scientific information for a hierarchical
retrieval system. Preserve major claims, methods, findings, important entities,
relationships, experimental conditions, limitations, and uncertainty. The
summary should be short, direct and clear.
Write the summary in the same language as the source content.
Use only information in the provided source content. Do not add external facts,
assumptions, explanations, or conclusions. If sources conflict or are uncertain,
preserve that conflict or uncertainty. Return only the summary."""


# -----------------------------------------------------------------------------
# Markdown and chunk-API input
# -----------------------------------------------------------------------------

def _catalog_id(document_id: str, data: dict[str, Any]) -> str:
    return str(
        data.get("catalog_id")
        or DOCUMENT_CATALOG_IDS.get(document_id)
        or DEFAULT_CATALOG_ID
    )


def _source_key(path: Path, markdown_dir: Path) -> str:
    return path.relative_to(markdown_dir).with_suffix("").as_posix()


def _chunk_id(
    document_id: UUID,
    chunk_index: int,
    content: str,
) -> str:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    identity = f"{chunk_index}:{content_hash}"
    return str(uuid5(document_id, identity))


def load_documents(
    markdown_dir: Path,
    *,
    skip_document_ids: set[str] | None = None,
    registered_documents: Sequence[DocumentInput] | None = None,
) -> list[dict[str, Any]]:
    """Chunk Markdown documents and embed their level-zero RAPTOR nodes."""

    if not markdown_dir.is_dir():
        raise RuntimeError(
            f"Parsed Markdown directory not found: {markdown_dir}"
        )

    if registered_documents is None:
        inputs = []
        for path in sorted(markdown_dir.rglob("*.md")):
            source_key = _source_key(path, markdown_dir)
            document_uuid = uuid5(DOCUMENT_NAMESPACE, source_key)
            inputs.append(DocumentInput(
                document_uuid, source_key, path,
                _catalog_id(str(document_uuid), {}),
                title=path.stem,
            ))
    else:
        inputs = list(registered_documents)

    documents: list[dict[str, Any]] = []
    for document in inputs:
        path = document.markdown_path
        source_key = document.source_key
        document_uuid = document.id
        document_id = str(document_uuid)
        document_title = document.title
        catalog_id = document.catalog_id
        if skip_document_ids and document_id in skip_document_ids:
            documents.append(
                {
                    "document_id": document_id,
                    "catalog_id": catalog_id,
                    "document_title": document_title,
                    "source_key": source_key,
                    "chunks": [],
                }
            )
            continue

        data = chunk_document(path)
        if registered_documents is None:
            catalog_id = _catalog_id(document_id, data)
        contents = data.get("chunk_list")
        if not isinstance(contents, list) or not contents:
            raise ValueError(f"{path}: chunk_list must be a non-empty array")

        titles = data.get("chunk_title")
        if titles is None:
            titles = [None] * len(contents)
        if not isinstance(titles, list) or len(titles) != len(contents):
            raise ValueError(
                f"{path}: chunk_title must contain {len(contents)} items"
            )

        token_counts = data.get("token_count")
        if token_counts is None:
            token_counts = [None] * len(contents)
        if (
            not isinstance(token_counts, list)
            or len(token_counts) != len(contents)
        ):
            raise ValueError(
                f"{path}: token_count must contain {len(contents)} items"
            )

        embedding_inputs: list[str] = []
        normalized_chunks: list[tuple[str, str | None, int | None]] = []

        for index, (raw_content, raw_title, raw_token_count) in enumerate(
            zip(contents, titles, token_counts, strict=True)
        ):
            if not isinstance(raw_content, str) or not raw_content.strip():
                raise ValueError(
                    f"{path}: chunk_list[{index}] must be a non-blank string"
                )
            if raw_title is not None and not isinstance(raw_title, str):
                raise ValueError(
                    f"{path}: chunk_title[{index}] must be a string or null"
                )
            if raw_token_count is not None and (
                not isinstance(raw_token_count, int)
                or isinstance(raw_token_count, bool)
                or raw_token_count < 0
            ):
                raise ValueError(
                    f"{path}: token_count[{index}] must be a nonnegative "
                    "integer or null"
                )

            content = raw_content.strip()
            title = raw_title.strip() if raw_title else None
            normalized_chunks.append((content, title, raw_token_count))
            embedding_inputs.append(
                f"{title}\n\n{content}" if title else content
            )

        embeddings = _embed_texts(embedding_inputs)
        if len(embeddings) != len(normalized_chunks):
            raise RuntimeError(
                f"Embedding model returned {len(embeddings)} vectors for "
                f"{len(normalized_chunks)} chunks from {path}"
            )

        documents.append(
            {
                "document_id": document_id,
                "catalog_id": catalog_id,
                "source_key": source_key,
                "document_title": document_title,
                "chunks": [
                    {
                        "chunk_id": _chunk_id(document_uuid, index, content),
                        "content": content,
                        "chunk_index": index,
                        "title": title,
                        "token_count": token_count,
                        "embedding": embedding,
                    }
                    for index, (
                        (content, title, token_count),
                        embedding,
                    ) in enumerate(
                        zip(normalized_chunks, embeddings, strict=True)
                    )
                ],
            }
        )

    return documents


def load_document_nodes(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert passage chunks to internal level-zero RAPTOR nodes."""

    document_id = document["document_id"]
    catalog_id = document["catalog_id"]
    source_key = document["source_key"]
    document_title = document["document_title"]
    return [
        {
            "node_id": chunk["chunk_id"],
            "text": chunk["content"],
            "embedding": chunk["embedding"],
            "level": 0,
            "scope": "passage",
            "document_id": document_id,
            "catalog_id": catalog_id,
            "source_key": source_key,
            "chunk_index": chunk["chunk_index"],
            "title": chunk["title"],
            "token_count": chunk["token_count"],
            "source_node_ids": [],
            "source_chunk_ids": [chunk["chunk_id"]],
            "source_document_ids": [document_id],
            "document_title": document_title,
        }
        for chunk in document["chunks"]
    ]


# -----------------------------------------------------------------------------
# Summary creation and provenance
# -----------------------------------------------------------------------------

def _summary_prompt(
    nodes: list[dict[str, Any]],
    summary_type: str,
) -> str:
    context = "\n\n".join(
        f"[source node: {node['node_id']}]\n{node['text']}" for node in nodes
    )
    return (
        f"Create a {summary_type} summary from the scientific "
        f"content below. Write the summary in the same language as the source content. \n\nCONTENT:\n{context}"
    )


def _estimate_tokens(text: str) -> int:
    """Conservatively estimate mixed Spanish-English token usage."""

    return max(1, (len(text.encode("utf-8")) + 2) // 3)


def _prompt_token_count(
    nodes: list[dict[str, Any]],
    summary_type: str,
) -> int:
    return _estimate_tokens(
        f"{SYSTEM_PROMPT}\n{_summary_prompt(nodes, summary_type)}"
    )


def _batch_nodes(
    nodes: list[dict[str, Any]],
    summary_type: str,
) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for node in nodes:
        if _prompt_token_count([node], summary_type) > SUMMARY_INPUT_TOKEN_LIMIT:
            raise ValueError(
                f"RAPTOR node {node['node_id']} exceeds the summary input "
                "limit; reduce the upstream passage chunk size"
            )
        candidate = [*current, node]
        if (
            current
            and _prompt_token_count(candidate, summary_type)
            > SUMMARY_INPUT_TOKEN_LIMIT
        ):
            batches.append(current)
            current = [node]
        else:
            current = candidate
    if current:
        batches.append(current)
    return batches


def _invoke_summary(
    nodes: list[dict[str, Any]],
    summary_type: str,
) -> str:
    with _LLM_SEMAPHORE:
        response = _llm().invoke(
            [
                ("system", SYSTEM_PROMPT),
                ("human", _summary_prompt(nodes, summary_type)),
            ]
        )
    if not isinstance(response.content, str):
        raise TypeError("The summarization model returned non-text content")
    return response.content.strip()


def summarize(
    nodes: list[dict[str, Any]],
    summary_type: str,
    *,
    _depth: int = 0,
) -> str:
    if not nodes:
        raise ValueError("Cannot summarize an empty list of nodes")
    if _depth > 10:
        raise RuntimeError("Summary batching did not converge after 10 levels")
    if _prompt_token_count(nodes, summary_type) <= SUMMARY_INPUT_TOKEN_LIMIT:
        return _invoke_summary(nodes, summary_type)

    partial_type = f"partial {summary_type}"
    batches = _batch_nodes(nodes, partial_type)
    print(
        f"RAPTOR {summary_type}: batching {len(nodes)} nodes into "
        f"{len(batches)} prompts"
    )
    partial_nodes = [
        {
            "node_id": f"{summary_type}_batch_{index}",
            "text": _invoke_summary(batch, partial_type),
        }
        for index, batch in enumerate(batches, start=1)
    ]
    return summarize(partial_nodes, summary_type, _depth=_depth + 1)


def _combined_values(nodes: list[dict[str, Any]], key: str) -> list[str]:
    return sorted({value for node in nodes for value in node[key]})


def create_summary_node(
    nodes: list[dict[str, Any]],
    node_id: str,
    level: int,
    scope: str,
    document_id: str | None,
    catalog_id: str,
    summary_type: str,
) -> dict[str, Any]:
    if not nodes:
        raise ValueError("Cannot summarize an empty list of nodes")

    text = summarize(nodes, summary_type)
    embedding = _embed_texts([text])[0]

    expected_dimension = len(nodes[0]["embedding"])
    if len(embedding) != expected_dimension:
        raise ValueError(
            f"Summary embedding has dimension {len(embedding)}, but source "
            f"nodes have dimension {expected_dimension}. Configure "
            "EMBEDDING_MODEL to match the passage collection."
        )

    return {
        "node_id": node_id,
        "text": text,
        "embedding": embedding,
        "level": level,
        "scope": scope,
        "document_id": document_id,
        "document_title": nodes[0]["document_title"] if document_id is not None else None,
        "catalog_id": catalog_id,
        "source_node_ids": [node["node_id"] for node in nodes],
        "source_chunk_ids": _combined_values(nodes, "source_chunk_ids"),
        "source_document_ids": _combined_values(
            nodes,
            "source_document_ids",
        ),
    }


# -----------------------------------------------------------------------------
# RAPTOR hierarchy
# -----------------------------------------------------------------------------

def create_cluster_summaries(
    nodes: list[dict[str, Any]],
    document_id: str,
    catalog_id: str,
    level: int,
) -> list[dict[str, Any]]:
    memberships = perform_clustering(
        embeddings=[node["embedding"] for node in nodes],
        dim=REDUCTION_DIMENSION,
        threshold=CLUSTER_THRESHOLD,
    )

    clusters: dict[int, list[dict[str, Any]]] = defaultdict(list)
    # RAPTOR uses soft membership: one node may feed several summaries.
    for node, cluster_ids in zip(nodes, memberships, strict=True):
        for cluster_id in cluster_ids:
            clusters[cluster_id].append(node)

    cluster_items = sorted(clusters.items())

    def create_cluster_summary(
        item: tuple[int, list[dict[str, Any]]],
    ) -> dict[str, Any]:
        cluster_id, cluster_nodes = item
        return create_summary_node(
            nodes=cluster_nodes,
            node_id=f"{document_id}_L{level}_C{cluster_id}",
            level=level,
            scope="document_cluster",
            document_id=document_id,
            catalog_id=catalog_id,
            summary_type="semantic-cluster",
        )

    if len(cluster_items) <= 1 or RAPTOR_MAX_WORKERS == 1:
        return [create_cluster_summary(item) for item in cluster_items]

    with ThreadPoolExecutor(
        max_workers=min(RAPTOR_MAX_WORKERS, len(cluster_items)),
        thread_name_prefix="raptor-cluster",
    ) as executor:
        return list(executor.map(create_cluster_summary, cluster_items))


def build_document(
    document: dict[str, Any],
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any]]:
    document_id = document["document_id"]
    catalog_id = document["catalog_id"]
    current_nodes = load_document_nodes(document)
    if not current_nodes:
        raise ValueError(f"Document {document_id} has no chunks")

    levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    levels[0].extend(current_nodes)
    level = 1

    # RAPTOR stopping rule: cluster while the configured minimum is met. Once
    # fewer nodes remain, combine them into one final document-level summary.
    while len(current_nodes) >= MIN_NODES_FOR_NEXT_LEVEL:
        print(f"{document_id} | level {level} | {len(current_nodes)} nodes")
        summaries = create_cluster_summaries(
            nodes=current_nodes,
            document_id=document_id,
            catalog_id=catalog_id,
            level=level,
        )
        levels[level].extend(summaries)

        # A pathological soft-clustering result can fail to reduce the level.
        # Stop here rather than loop forever; the nodes still receive a final
        # document summary on the following level.
        if len(summaries) >= len(current_nodes):
            print(
                f"{document_id} | clustering did not reduce "
                f"({len(current_nodes)} -> {len(summaries)}); finalizing"
            )
            current_nodes = summaries
            level += 1
            break

        current_nodes = summaries
        level += 1

    document_summary = create_summary_node(
        nodes=current_nodes,
        node_id=f"{document_id}_L{level}_document",
        level=level,
        scope="document",
        document_id=document_id,
        catalog_id=catalog_id,
        summary_type="document-level",
    )
    levels[level].append(document_summary)
    return levels, document_summary


def build_catalog_summary(
    catalog_id: str,
    document_summaries: list[dict[str, Any]],
    level: int,
) -> dict[str, Any]:
    return create_summary_node(
        nodes=document_summaries,
        node_id=f"{catalog_id}_L{level}_catalog",
        level=level,
        scope="catalog",
        document_id=None,
        catalog_id=catalog_id,
        summary_type="cross-document catalog-level",
    )


# -----------------------------------------------------------------------------
# JSON output
# -----------------------------------------------------------------------------

def clean_node(node: dict[str, Any]) -> dict[str, Any]:
    """Embeddings are internal only and are deliberately omitted from JSON."""

    return {key: value for key, value in node.items() if key != "embedding"}


def save_levels(
    levels: dict[int, list[dict[str, Any]]],
    output_dir: Path = OUTPUT_DIR,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    current_paths = {
        output_dir / f"level_{level}.json"
        for level in levels
    }

    for level, nodes in sorted(levels.items()):
        output_path = output_dir / f"level_{level}.json"
        temporary_path = output_path.with_suffix(".json.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                {
                    "level": level,
                    "nodes": [clean_node(node) for node in nodes],
                },
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")
        temporary_path.replace(output_path)
        print(f"Saved {output_path}")

    for stale_path in sorted(output_dir.glob("level_*.json")):
        if stale_path not in current_paths:
            stale_path.unlink()
            print(f"Removed stale {stale_path}")


def load_existing_levels(
    output_dir: Path,
) -> dict[int, list[dict[str, Any]]]:
    """Load saved summary nodes so completed documents can be reused."""

    levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    if not output_dir.is_dir():
        return levels

    for path in sorted(output_dir.glob("level_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        levels[data["level"]].extend(data["nodes"])
    return levels


def _restore_embedding(node: dict[str, Any]) -> dict[str, Any]:
    """Restore the internal embedding omitted from persisted summary JSON."""

    restored = dict(node)
    restored["embedding"] = _embed_texts([node["text"]])[0]
    return restored


def run(
    data_root: Path = PROJECT_ROOT / "data",
    *,
    skip_existing: bool = False,
    registered_documents: Sequence[DocumentInput] | None = None,
) -> StageResult:
    """Build the unified RAPTOR hierarchy from parsed Markdown documents."""

    started = perf_counter()
    data_root = data_root.resolve()
    markdown_dir = data_root / "pdf_parsed_output"
    output_dir = data_root / "summaries"
    try:
        existing_levels = load_existing_levels(output_dir) if skip_existing else {}
    except (ValueError, KeyError, TypeError):
        if registered_documents is None:
            raise
        # Generated files are a cache; rebuild after interrupted/corrupt output.
        existing_levels = {}
    completed_ids = (
        {str(document.id) for document in registered_documents if document.has_summary}
        if registered_documents is not None else None
    )
    existing_nodes_by_document: dict[str, list[dict[str, Any]]] = defaultdict(list)
    existing_document_summaries: dict[str, dict[str, Any]] = {}
    existing_catalog_summaries: dict[str, dict[str, Any]] = {}
    documents_with_level_zero: set[str] = set()
    for nodes in existing_levels.values():
        for node in nodes:
            scope = node.get("scope")
            document_id = node.get("document_id")
            catalog_id = node.get("catalog_id")
            if isinstance(document_id, str):
                if completed_ids is not None and document_id not in completed_ids:
                    continue
                existing_nodes_by_document[document_id].append(node)
                if scope == "document":
                    existing_document_summaries[document_id] = node
                elif scope == "passage" and node.get("level") == 0:
                    documents_with_level_zero.add(document_id)
            elif scope == "catalog" and isinstance(catalog_id, str):
                existing_catalog_summaries[catalog_id] = node

    documents = load_documents(
        markdown_dir,
        registered_documents=registered_documents,
        skip_document_ids=(
            set(existing_document_summaries) & documents_with_level_zero
        ),
    )
    if not documents:
        raise RuntimeError(f"No Markdown files found in {markdown_dir}")

    all_levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    catalog_documents: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rebuilt_catalog_ids: set[str] = set()
    max_document_level = 0

    def process_document(
        document: dict[str, Any],
    ) -> tuple[
        dict[str, Any],
        dict[int, list[dict[str, Any]]],
        dict[str, Any],
        bool,
    ]:
        document_id = document["document_id"]
        document_summary = existing_document_summaries.get(document_id)
        existing_nodes = existing_nodes_by_document.get(document_id, [])
        if (
            document_summary is not None
            and existing_nodes
            and document_id in documents_with_level_zero
        ):
            levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
            for node in existing_nodes:
                levels[node["level"]].append(node)
            print(f"{document_id}: reusing summary hierarchy")
            rebuilt = False
        else:
            levels, document_summary = build_document(document)
            rebuilt = True

        return document, levels, document_summary, rebuilt

    if len(documents) <= 1 or RAPTOR_MAX_WORKERS == 1:
        processed_documents = [
            process_document(document) for document in documents
        ]
    else:
        with ThreadPoolExecutor(
            max_workers=min(RAPTOR_MAX_WORKERS, len(documents)),
            thread_name_prefix="raptor-document",
        ) as executor:
            processed_documents = list(
                executor.map(process_document, documents)
            )

    for document, levels, document_summary, rebuilt in processed_documents:
        if rebuilt:
            rebuilt_catalog_ids.add(document["catalog_id"])
        for level, nodes in levels.items():
            all_levels[level].extend(nodes)
            max_document_level = max(max_document_level, level)
        catalog_documents[document["catalog_id"]].append(document_summary)

    # Catalog summaries are intentionally placed together at one final level,
    # after the deepest per-document hierarchy.
    catalog_level = max_document_level + 1
    for catalog_id, document_summaries in sorted(catalog_documents.items()):
        document_ids = {
            summary["document_id"] for summary in document_summaries
        }
        existing_catalog = existing_catalog_summaries.get(catalog_id)
        existing_source_ids = (
            set(existing_catalog.get("source_document_ids", []))
            if existing_catalog is not None
            else set()
        )
        if (
            existing_catalog is not None
            and catalog_id not in rebuilt_catalog_ids
            and existing_catalog.get("level") == catalog_level
            and existing_source_ids == document_ids
        ):
            catalog_summary = existing_catalog
            print(f"{catalog_id}: reusing catalog summary")
        else:
            document_summaries = [
                summary
                if "embedding" in summary
                else _restore_embedding(summary)
                for summary in document_summaries
            ]
            catalog_summary = build_catalog_summary(
                catalog_id=catalog_id,
                document_summaries=document_summaries,
                level=catalog_level,
            )
        all_levels[catalog_level].append(catalog_summary)

    save_levels(all_levels, output_dir)
    return StageResult(
        stage="raptor",
        duration_seconds=perf_counter() - started,
        counts={
            "documents": len(documents),
            "levels": len(all_levels),
            "chunks": len(all_levels.get(0, [])),
            "summaries": sum(
                len(nodes)
                for level, nodes in all_levels.items()
                if level > 0
            ),
        },
    )


def main() -> None:
    result = run()
    print(
        f"RAPTOR representation complete in {result.duration_seconds:.2f}s: "
        f"{result.counts}"
    )


if __name__ == "__main__":
    main()
