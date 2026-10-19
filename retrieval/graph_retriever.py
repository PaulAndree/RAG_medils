"""Retrieve graph context for chunks found by vector search."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from neo4j import GraphDatabase
from qdrant_client import QdrantClient, models

from indexing.embedding_api import DENSE_MODEL, SPARSE_MODEL, embed_texts
from metrics import RETRIEVAL_DURATION


QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv(
    "GRAPH_QDRANT_COLLECTION",
    "arguments_embeddings_live",
)
QDRANT_CHUNK_ID_FIELD = "source_chunk_id"
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ragpassword")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

qdrant = QdrantClient(url=QDRANT_URL)
neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
)


DEFAULT_CYPHER_QUERY = """
UNWIND $chunk_ids AS chunk_id
MATCH (chunk:RagChunk {id: chunk_id})
MATCH (chunk)-[:MENTIONS]->(entity:RagEntity)
MATCH (entity)-[relation:RELATES_TO]->(other:RagEntity)

RETURN
    chunk_id AS source_chunk_id,
    chunk {.*} AS chunk,
    entity {.*} AS entity,
    relation {.*, type: type(relation)} AS relation,
    other {.*} AS connected_entity

ORDER BY source_chunk_id, entity.id, connected_entity.id
"""


@RETRIEVAL_DURATION.labels(retrieval_type="graph").time()
def retrieve_graph(
    *,
    query: str | None = None,
    embedding: Sequence[float] | None = None,
    limit: int = 5,
    cypher_query: str = DEFAULT_CYPHER_QUERY,
    cypher_parameters: dict[str, Any] | None = None,
    qdrant_client: Any = qdrant,
    driver: Any = neo4j_driver,
) -> dict[str, list[dict[str, Any]]]:
    """Run vector search, map payload chunk IDs, and query Neo4j.

    A custom Cypher query can use ``$results`` and ``$chunk_ids``.
    """

    if (query is None) == (embedding is None):
        raise ValueError("Provide exactly one of query or embedding")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    if embedding is not None:
        vector_query = list(embedding)
        if not vector_query:
            raise ValueError("embedding must not be empty")
        query_arguments = {
            "query": vector_query,
            "using": DENSE_VECTOR,
        }
    else:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        candidate_limit = max(20, limit * 5)
        dense_query = embed_texts([query], DENSE_MODEL, "query")[0]
        sparse_query = embed_texts([query], SPARSE_MODEL, "query")[0]
        query_arguments = {
            "prefetch": [
                models.Prefetch(
                    query=dense_query,
                    using=DENSE_VECTOR,
                    limit=candidate_limit,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_query["indices"],
                        values=sparse_query["values"],
                    ),
                    using=SPARSE_VECTOR,
                    limit=candidate_limit,
                ),
            ],
            "query": models.FusionQuery(fusion=models.Fusion.RRF),
        }

    points = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION,
        **query_arguments,
        limit=limit,
        with_payload=True,
    ).points

    results = []
    for rank, point in enumerate(points, start=1):
        payload = point.payload or {}
        chunk_id = payload.get(QDRANT_CHUNK_ID_FIELD)
        if not chunk_id:
            raise ValueError(
                f"Qdrant point {point.id!s} has no payload "
                f"{QDRANT_CHUNK_ID_FIELD}"
            )
        evidence = payload.get("evidence", [])
        if evidence is None:
            evidence = []
        elif not isinstance(evidence, list):
            evidence = [evidence]
        point_id = str(point.id)
        results.append(
            {
                "result_id": point_id,
                "rank": rank,
                "score": point.score,
                "argument_id": payload.get("argument_id", point_id),
                "claim": payload.get("claim"),
                "evidence": evidence,
                "source_chunk_id": str(chunk_id),
                "source_content": payload.get("source_content"),
                "graph_expansion": {"entities": [], "relations": []},
            }
        )

    if not results:
        return {"results": []}

    parameters = dict(cypher_parameters or {})
    parameters["results"] = results
    parameters["chunk_ids"] = list(
        dict.fromkeys(result["source_chunk_id"] for result in results)
    )

    with driver.session(database=NEO4J_DATABASE) as session:
        records = [dict(record) for record in session.run(cypher_query, parameters)]

    records_by_chunk: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        chunk_id = record.get("source_chunk_id")
        if chunk_id is None:
            chunk = record.get("chunk")
            if isinstance(chunk, dict):
                chunk_id = chunk.get("id")
        if chunk_id is not None:
            records_by_chunk.setdefault(str(chunk_id), []).append(record)

    for result in results:
        entities: list[dict[str, Any]] = []
        relations: list[dict[str, Any]] = []
        entity_keys: set[str] = set()
        relation_keys: set[str] = set()
        for record in records_by_chunk.get(result["source_chunk_id"], []):
            source = record.get("entity")
            target = record.get("connected_entity")
            for entity in (source, target):
                if not isinstance(entity, dict):
                    continue
                key = str(entity.get("id") or sorted(entity.items()))
                if key not in entity_keys:
                    entity_keys.add(key)
                    entities.append(entity)

            relation = record.get("relation")
            if not isinstance(relation, dict):
                continue
            expanded_relation = {
                **relation,
                "source": source if isinstance(source, dict) else None,
                "target": target if isinstance(target, dict) else None,
            }
            key = str(relation.get("id") or sorted(relation.items()))
            if key not in relation_keys:
                relation_keys.add(key)
                relations.append(expanded_relation)

        result["graph_expansion"] = {
            "entities": entities,
            "relations": relations,
        }

    return {"results": results}
