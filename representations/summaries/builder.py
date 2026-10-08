from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

from fastembed import TextEmbedding
from langchain_ollama import ChatOllama
from qdrant_client import QdrantClient

from raptor_clustering import perform_clustering


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")
#QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
PASSAGE_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "documents_embeddings_live",
)
QDRANT_SCROLL_SIZE = 256

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")

# Use the exact FastEmbed model used to create the passage collection so that
# passage, summary, and future query vectors share one embedding space.
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)

MIN_NODES_FOR_NEXT_LEVEL = 10
CLUSTER_THRESHOLD = 0.2
REDUCTION_DIMENSION = 10

# The documented Qdrant payload has no catalog_id. For this POC, all documents
# without one are assigned to this catalog. Add catalog_id to the payload later,
# or fill this mapping when a collection contains more than one catalog.
DEFAULT_CATALOG_ID = os.getenv("CATALOG_ID", "default_catalog")
DOCUMENT_CATALOG_IDS: dict[str, str] = {}

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "summaries"


# -----------------------------------------------------------------------------
# Clients and prompt
# -----------------------------------------------------------------------------

qdrant = QdrantClient(url=QDRANT_URL)
llm = ChatOllama(
    model=GENERATION_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.1,
)
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)

SYSTEM_PROMPT = """You summarize scientific information for a hierarchical
retrieval system. Preserve major claims, methods, findings, important entities,
relationships, experimental conditions, limitations, and uncertainty. The summary should be direct and clear.

Use only information in the provided source content. Do not add external facts,
assumptions, explanations, or conclusions. If sources conflict or are uncertain,
preserve that conflict or uncertainty. Return only the summary."""


# -----------------------------------------------------------------------------
# Qdrant input
# -----------------------------------------------------------------------------

def _point_vector(vector: Any) -> list[float]:
    """Return a dense vector from either unnamed or single-named Qdrant data."""

    if isinstance(vector, dict):
        if len(vector) != 1:
            raise ValueError(
                "Expected one dense vector per Qdrant point, "
                f"but found vector names {sorted(vector)}"
            )
        vector = next(iter(vector.values()))

    if not isinstance(vector, (list, tuple)) or not vector:
        raise ValueError("A Qdrant point is missing its dense passage vector")

    return [float(value) for value in vector]


def _catalog_id(payload: dict[str, Any]) -> str:
    document_id = str(payload["document_id"])
    return str(
        payload.get("catalog_id")
        or DOCUMENT_CATALOG_IDS.get(document_id)
        or DEFAULT_CATALOG_ID
    )


def load_documents() -> list[dict[str, Any]]:
    """Scroll the live alias once and group existing chunks by document."""

    documents: dict[str, dict[str, Any]] = {}
    offset = None

    while True:
        points, offset = qdrant.scroll(
            collection_name=PASSAGE_COLLECTION,
            limit=QDRANT_SCROLL_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=True,
        )

        for point in points:
            payload = point.payload or {}
            required = ("chunk_id", "document_id", "content", "chunk_index")
            missing = [key for key in required if key not in payload]
            if missing:
                raise ValueError(
                    f"Qdrant point {point.id} is missing payload fields: {missing}"
                )

            document_id = str(payload["document_id"])
            catalog_id = _catalog_id(payload)
            document = documents.setdefault(
                document_id,
                {
                    "document_id": document_id,
                    "catalog_id": catalog_id,
                    "chunks": [],
                },
            )
            if document["catalog_id"] != catalog_id:
                raise ValueError(
                    f"Document {document_id} has chunks in multiple catalogs"
                )

            document["chunks"].append(
                {
                    "chunk_id": str(payload["chunk_id"]),
                    "content": str(payload["content"]),
                    "chunk_index": int(payload["chunk_index"]),
                    # Use the vector already stored in Qdrant. Original passages
                    # are never re-chunked or re-embedded by this program.
                    "embedding": _point_vector(point.vector),
                }
            )

        if offset is None:
            break

    for document in documents.values():
        document["chunks"].sort(
            key=lambda chunk: (chunk["chunk_index"], chunk["chunk_id"])
        )

    return sorted(documents.values(), key=lambda item: item["document_id"])


def load_document_nodes(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert Qdrant chunks to internal level-zero RAPTOR nodes."""

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
    response = llm.invoke(
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
    embedding = next(embedding_model.embed([text])).tolist()

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


def save_levels(levels: dict[int, list[dict[str, Any]]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for level, nodes in sorted(levels.items()):
        output_path = OUTPUT_DIR / f"level_{level}.json"
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                {
                    "level": level,
                    "nodes": [clean_node(node) for node in nodes],
                },
                file,
                indent=2,
                ensure_ascii=False,
            )
        print(f"Saved {output_path}")


def main() -> None:
    documents = load_documents()
    if not documents:
        raise RuntimeError(f"No chunks found in {PASSAGE_COLLECTION}")

    all_levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    catalog_documents: dict[str, list[dict[str, Any]]] = defaultdict(list)
    max_document_level = 0

    for document in documents:
        levels, document_summary = build_document(document)
        for level, nodes in levels.items():
            all_levels[level].extend(nodes)
            max_document_level = max(max_document_level, level)
        catalog_documents[document["catalog_id"]].append(document_summary)

    # Catalog summaries are intentionally placed together at one final level,
    # after the deepest per-document hierarchy.
    catalog_level = max_document_level + 1
    for catalog_id, document_summaries in sorted(catalog_documents.items()):
        all_levels[catalog_level].append(
            build_catalog_summary(
                catalog_id=catalog_id,
                document_summaries=document_summaries,
                level=catalog_level,
            )
        )

    save_levels(all_levels)


if __name__ == "__main__":
    main()
