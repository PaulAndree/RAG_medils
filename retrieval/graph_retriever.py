"""Retrieve graph context for chunks found by vector search."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from neo4j import GraphDatabase
from qdrant_client import QdrantClient, models

from metrics import RETRIEVAL_DURATION


QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
QDRANT_COLLECTION = os.getenv(
    "GRAPH_QDRANT_COLLECTION",
    "arguments_embeddings_live",
)
QDRANT_CHUNK_ID_FIELD = "source_chunk_id"
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "bm25"
DENSE_MODEL = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL = "Qdrant/bm25"

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
UNWIND $matches AS match
WITH
    match.chunk_id AS chunk_id,
    match.rank AS rank,
    match.score AS score,
    match.point_ids AS point_ids

MATCH (chunk:RagChunk {id: chunk_id})
MATCH (chunk)-[:MENTIONS]->(entity:RagEntity)
MATCH (entity)-[relation:RELATES_TO]->(other:RagEntity)

RETURN
    rank,
    score,
    point_ids,
    chunk {.*} AS chunk,
    entity {.*} AS entity,
    relation {.*, type: type(relation)} AS relation,
    other {.*} AS connected_entity

ORDER BY rank, entity.id, connected_entity.id
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

    A custom Cypher query can use ``$matches`` and ``$chunk_ids``.
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
        query_arguments = {
            "prefetch": [
                models.Prefetch(
                    query=models.Document(text=query, model=DENSE_MODEL),
                    using=DENSE_VECTOR,
                    limit=candidate_limit,
                ),
                models.Prefetch(
                    query=models.Document(text=query, model=SPARSE_MODEL),
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

    matches_by_chunk = {}
    for rank, point in enumerate(points, start=1):
        payload = point.payload or {}
        chunk_id = payload.get(QDRANT_CHUNK_ID_FIELD)
        if not chunk_id:
            raise ValueError(
                f"Qdrant point {point.id!s} has no payload "
                f"{QDRANT_CHUNK_ID_FIELD}"
            )
        chunk_id = str(chunk_id)
        point_id = str(point.id)
        if chunk_id not in matches_by_chunk:
            matches_by_chunk[chunk_id] = {
                "rank": rank,
                "score": point.score,
                "point_id": point_id,
                "point_ids": [point_id],
                "chunk_id": chunk_id,
            }
        else:
            matches_by_chunk[chunk_id]["point_ids"].append(point_id)

    matches = list(matches_by_chunk.values())

    if not matches:
        return {"matches": [], "records": []}

    parameters = dict(cypher_parameters or {})
    parameters["matches"] = matches
    parameters["chunk_ids"] = [match["chunk_id"] for match in matches]

    with driver.session(database=NEO4J_DATABASE) as session:
        records = [
            dict(record)
            for record in session.run(cypher_query, parameters)
        ]

    return {"matches": matches, "records": records}
