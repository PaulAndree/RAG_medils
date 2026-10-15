from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from fastembed import TextEmbedding
from langchain_ollama import ChatOllama

from representations.common import StageResult
from representations.summaries.raptor_clustering import perform_clustering


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PASSAGES_DIR = Path(
    os.getenv(
        "PASSAGES_DIR",
        str(PROJECT_ROOT / "data" / "passages_chunk"),
    )
)

# This must match stores.ingestion so summary provenance points at the passage
# IDs that will be created when a fresh input snapshot is ingested.
DOCUMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/sql-rag/documents",
)
DOCUMENT_VERSION = int(os.getenv("DOCUMENT_VERSION", "1"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")

# Use the exact FastEmbed model used by the passage indexer so passage,
# summary, and future query vectors share one embedding space.
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)

MIN_NODES_FOR_NEXT_LEVEL = 10
CLUSTER_THRESHOLD = 0.2
REDUCTION_DIMENSION = 10

# Chunk files without a catalog_id are assigned to this default catalog. Fill
# this mapping when the input directory contains more than one catalog.
DEFAULT_CATALOG_ID = os.getenv("CATALOG_ID", "default_catalog")
DOCUMENT_CATALOG_IDS: dict[str, str] = {}

OUTPUT_DIR = PROJECT_ROOT / "data" / "summaries"


# -----------------------------------------------------------------------------
# Clients and prompt
# -----------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _llm() -> ChatOllama:
    return ChatOllama(
        model=GENERATION_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )


@lru_cache(maxsize=1)
def _embedding_model() -> TextEmbedding:
    return TextEmbedding(model_name=EMBEDDING_MODEL)

SYSTEM_PROMPT = """You summarize scientific information for a hierarchical
retrieval system. Preserve major claims, methods, findings, important entities,
relationships, experimental conditions, limitations, and uncertainty. The
summary should be direct and clear.

Use only information in the provided source content. Do not add external facts,
assumptions, explanations, or conclusions. If sources conflict or are uncertain,
preserve that conflict or uncertainty. Return only the summary."""


# -----------------------------------------------------------------------------
# Passage-file input
# -----------------------------------------------------------------------------

def _catalog_id(document_id: str, data: dict[str, Any]) -> str:
    return str(
        data.get("catalog_id")
        or DOCUMENT_CATALOG_IDS.get(document_id)
        or DEFAULT_CATALOG_ID
    )


def _source_key(path: Path, passages_dir: Path) -> str:
    relative = path.relative_to(passages_dir)
    name = relative.name.removesuffix("_chunks.json")
    if not name or name == relative.name:
        raise ValueError(f"Invalid passage chunk filename: {path}")
    return (relative.parent / name).as_posix()


def _chunk_id(
    document_id: UUID,
    chunk_index: int,
    content: str,
) -> str:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    identity = f"{DOCUMENT_VERSION}:{chunk_index}:{content_hash}"
    return str(uuid5(document_id, identity))


def _load_chunk_data(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Cannot read passage chunks from {path}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level value must be an object")
    return data


def load_documents(
    passages_dir: Path = PASSAGES_DIR,
    *,
    skip_document_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Discover passage files and embed chunks needed for new summaries."""

    if not passages_dir.is_dir():
        raise RuntimeError(
            f"Passage chunks directory not found: {passages_dir}"
        )

    documents: list[dict[str, Any]] = []
    for path in sorted(passages_dir.rglob("*_chunks.json")):
        data = _load_chunk_data(path)
        source_key = _source_key(path, passages_dir)
        document_uuid = uuid5(DOCUMENT_NAMESPACE, source_key)
        document_id = str(document_uuid)
        catalog_id = _catalog_id(document_id, data)
        if skip_document_ids and document_id in skip_document_ids:
            documents.append(
                {
                    "document_id": document_id,
                    "catalog_id": catalog_id,
                    "chunks": [],
                }
            )
            continue

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

        embedding_inputs: list[str] = []
        normalized_chunks: list[tuple[str, str | None]] = []

        for index, (raw_content, raw_title) in enumerate(
            zip(contents, titles, strict=True)
        ):
            if not isinstance(raw_content, str) or not raw_content.strip():
                raise ValueError(
                    f"{path}: chunk_list[{index}] must be a non-blank string"
                )
            if raw_title is not None and not isinstance(raw_title, str):
                raise ValueError(
                    f"{path}: chunk_title[{index}] must be a string or null"
                )

            content = raw_content.strip()
            title = raw_title.strip() if raw_title else None
            normalized_chunks.append((content, title))
            embedding_inputs.append(
                f"{title}\n\n{content}" if title else content
            )

        embeddings = [
            embedding.tolist()
            for embedding in _embedding_model().embed(embedding_inputs)
        ]
        if len(embeddings) != len(normalized_chunks):
            raise RuntimeError(
                f"Embedding model returned {len(embeddings)} vectors for "
                f"{len(normalized_chunks)} chunks in {path}"
            )

        documents.append(
            {
                "document_id": document_id,
                "catalog_id": catalog_id,
                "chunks": [
                    {
                        "chunk_id": _chunk_id(document_uuid, index, content),
                        "content": content,
                        "chunk_index": index,
                        "embedding": embedding,
                    }
                    for index, ((content, _), embedding) in enumerate(
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
    return [
        {
            "node_id": chunk["chunk_id"],
            "text": chunk["content"],
            "embedding": chunk["embedding"],
            "level": 0,
            "scope": "passage",
            "document_id": document_id,
            "catalog_id": catalog_id,
            "source_node_ids": [],
            "source_chunk_ids": [chunk["chunk_id"]],
            "source_document_ids": [document_id],
        }
        for chunk in document["chunks"]
    ]


# -----------------------------------------------------------------------------
# Summary creation and provenance
# -----------------------------------------------------------------------------

def summarize(nodes: list[dict[str, Any]], summary_type: str) -> str:
    context = "\n\n".join(
        f"[source node: {node['node_id']}]\n{node['text']}" for node in nodes
    )
    response = _llm().invoke(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                f"Create a {summary_type} summary from the scientific "
                f"content below.\n\nCONTENT:\n{context}",
            ),
        ]
    )
    if not isinstance(response.content, str):
        raise TypeError("The summarization model returned non-text content")
    return response.content.strip()


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
    embedding = next(_embedding_model().embed([text])).tolist()

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

    return [
        create_summary_node(
            nodes=cluster_nodes,
            node_id=f"{document_id}_L{level}_C{cluster_id}",
            level=level,
            scope="document_cluster",
            document_id=document_id,
            catalog_id=catalog_id,
            summary_type="semantic-cluster",
        )
        for cluster_id, cluster_nodes in sorted(clusters.items())
    ]


def build_document(
    document: dict[str, Any],
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any]]:
    document_id = document["document_id"]
    catalog_id = document["catalog_id"]
    current_nodes = load_document_nodes(document)
    if not current_nodes:
        raise ValueError(f"Document {document_id} has no chunks")

    levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    level = 1

    # RAPTOR stopping rule: cluster levels with at least five nodes. Once fewer
    # than five remain, combine them into one final document-level summary.
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
    restored["embedding"] = next(
        _embedding_model().embed([node["text"]])
    ).tolist()
    return restored


def run(
    data_root: Path = PROJECT_ROOT / "data",
    *,
    skip_existing: bool = False,
) -> StageResult:
    """Build hierarchical summaries for all passage representations."""

    started = perf_counter()
    data_root = data_root.resolve()
    passages_dir = data_root / "passages_chunk"
    output_dir = data_root / "summaries"
    existing_levels = (
        load_existing_levels(output_dir) if skip_existing else {}
    )
    existing_nodes_by_document: dict[str, list[dict[str, Any]]] = defaultdict(list)
    existing_document_summaries: dict[str, dict[str, Any]] = {}
    existing_catalog_summaries: dict[str, dict[str, Any]] = {}
    for nodes in existing_levels.values():
        for node in nodes:
            scope = node.get("scope")
            document_id = node.get("document_id")
            catalog_id = node.get("catalog_id")
            if isinstance(document_id, str):
                existing_nodes_by_document[document_id].append(node)
                if scope == "document":
                    existing_document_summaries[document_id] = node
            elif scope == "catalog" and isinstance(catalog_id, str):
                existing_catalog_summaries[catalog_id] = node

    documents = load_documents(
        passages_dir,
        skip_document_ids=set(existing_document_summaries),
    )
    if not documents:
        raise RuntimeError(f"No *_chunks.json files found in {passages_dir}")

    all_levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    catalog_documents: dict[str, list[dict[str, Any]]] = defaultdict(list)
    max_document_level = 0

    for document in documents:
        document_id = document["document_id"]
        document_summary = existing_document_summaries.get(document_id)
        existing_nodes = existing_nodes_by_document.get(document_id, [])
        if document_summary is not None and existing_nodes:
            levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
            for node in existing_nodes:
                levels[node["level"]].append(node)
            print(f"{document_id}: reusing summary hierarchy")
        else:
            levels, document_summary = build_document(document)
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
        stage="summaries",
        duration_seconds=perf_counter() - started,
        counts={
            "documents": len(documents),
            "levels": len(all_levels),
            "summaries": sum(len(nodes) for nodes in all_levels.values()),
        },
    )


def main() -> None:
    result = run()
    print(
        f"Summaries complete in {result.duration_seconds:.2f}s: "
        f"{result.counts}"
    )


if __name__ == "__main__":
    main()
