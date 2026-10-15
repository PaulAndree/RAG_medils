"""Build the Neo4j entity graph from PostgreSQL."""

from __future__ import annotations

import json
import os
from time import perf_counter
from typing import Any

from neo4j import GraphDatabase

from metrics import ProcessMetricSample, push_process_metrics
from stores.database_postgres import get_indexable_entity_relations


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ragpassword")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")


CONSTRAINTS = (
    """
    CREATE CONSTRAINT rag_document_id IF NOT EXISTS
    FOR (node:RagDocument) REQUIRE node.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT rag_chunk_id IF NOT EXISTS
    FOR (node:RagChunk) REQUIRE node.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT rag_entity_id IF NOT EXISTS
    FOR (node:RagEntity) REQUIRE node.id IS UNIQUE
    """,
)


def entity_id(chunk_id: str, local_id: str) -> str:
    """Make a source-local entity ID unique across the graph."""

    return f"{chunk_id}:{local_id}"


def build_graph_snapshot(
    bundles: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Convert bundles into rows containing only connected entities."""

    documents: dict[str, dict[str, Any]] = {}
    chunks: dict[str, dict[str, Any]] = {}
    entity_rows: list[dict[str, Any]] = []
    relation_rows: list[dict[str, Any]] = []

    for bundle in bundles:
        relations = bundle["relations"]
        if not relations:
            continue

        document_id = bundle["document_id"]
        chunk_id = bundle["chunk_id"]
        local_entities: dict[str, tuple[str, dict[str, Any]]] = {}
        for entity in bundle["entities"]:
            local_id = entity["id"]
            graph_id = entity_id(chunk_id, local_id)
            if local_id in local_entities:
                raise ValueError(
                    f"chunk {chunk_id}: duplicate entity ID {local_id!r}"
                )
            local_entities[local_id] = (graph_id, entity)

        connected_relations: list[tuple[int, dict[str, Any]]] = []
        connected_entity_ids: set[str] = set()
        for position, relation in enumerate(relations):
            subject_id = relation["subject_id"]
            object_id = relation["object_id"]
            if subject_id not in local_entities:
                raise ValueError(
                    f"chunk {chunk_id}: relation subject "
                    f"{subject_id!r} does not exist"
                )
            if object_id not in local_entities:
                raise ValueError(
                    f"chunk {chunk_id}: relation object "
                    f"{object_id!r} does not exist"
                )
            if subject_id == object_id:
                continue
            connected_relations.append((position, relation))
            connected_entity_ids.update((subject_id, object_id))

        if not connected_relations:
            continue

        documents[document_id] = {
            "id": document_id,
            "name": bundle["doc_name"],
            "title": bundle["document_title"],
            "version": bundle["document_version"],
        }
        chunks[chunk_id] = {
            "id": chunk_id,
            "bundle_id": bundle["bundle_id"],
            "document_id": document_id,
            "index": bundle["chunk_index"],
            "title": bundle["chunk_title"],
            "content": bundle["chunk_content"],
        }

        for local_id, (graph_id, entity) in local_entities.items():
            if local_id not in connected_entity_ids:
                continue
            entity_rows.append(
                {
                    "id": graph_id,
                    "local_id": local_id,
                    "name": entity["name"],
                    "type": entity["type"],
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                }
            )

        for position, relation in connected_relations:
            subject_id = relation["subject_id"]
            object_id = relation["object_id"]
            relation_rows.append(
                {
                    "id": f"{chunk_id}:{position}",
                    "subject_id": local_entities[subject_id][0],
                    "object_id": local_entities[object_id][0],
                    "relation": relation["relation"],
                    "evidence": relation.get("evidence"),
                    "confidence": relation.get("confidence"),
                    "negated": relation.get("negated", False),
                    "certainty": relation.get("certainty"),
                    "qualifiers_json": json.dumps(
                        relation.get("qualifiers", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                }
            )

    return {
        "documents": list(documents.values()),
        "chunks": list(chunks.values()),
        "entities": entity_rows,
        "relations": relation_rows,
    }


def create_constraints(session: Any) -> None:
    for query in CONSTRAINTS:
        session.run(query).consume()


def _replace_graph(transaction: Any, snapshot: dict[str, Any]) -> None:
    transaction.run(
        """
        MATCH (node)
        WHERE node:RagDocument OR node:RagChunk OR node:RagEntity
        DETACH DELETE node
        """
    ).consume()

    transaction.run(
        """
        UNWIND $rows AS row
        CREATE (document:RagDocument {
            id: row.id,
            name: row.name,
            title: row.title,
            version: row.version
        })
        """,
        rows=snapshot["documents"],
    ).consume()

    transaction.run(
        """
        UNWIND $rows AS row
        MATCH (document:RagDocument {id: row.document_id})
        CREATE (chunk:RagChunk {
            id: row.id,
            bundle_id: row.bundle_id,
            chunk_index: row.index,
            title: row.title,
            content: row.content
        })
        CREATE (document)-[:HAS_CHUNK]->(chunk)
        """,
        rows=snapshot["chunks"],
    ).consume()

    transaction.run(
        """
        UNWIND $rows AS row
        MATCH (chunk:RagChunk {id: row.chunk_id})
        CREATE (entity:RagEntity {
            id: row.id,
            local_id: row.local_id,
            name: row.name,
            type: row.type,
            chunk_id: row.chunk_id,
            document_id: row.document_id
        })
        CREATE (chunk)-[:MENTIONS]->(entity)
        """,
        rows=snapshot["entities"],
    ).consume()

    transaction.run(
        """
        UNWIND $rows AS row
        MATCH (subject:RagEntity {id: row.subject_id})
        MATCH (object:RagEntity {id: row.object_id})
        CREATE (subject)-[edge:RELATES_TO {
            id: row.id,
            relation: row.relation,
            evidence: row.evidence,
            confidence: row.confidence,
            negated: row.negated,
            certainty: row.certainty,
            qualifiers_json: row.qualifiers_json,
            chunk_id: row.chunk_id,
            document_id: row.document_id
        }]->(object)
        """,
        rows=snapshot["relations"],
    ).consume()


def replace_graph(session: Any, snapshot: dict[str, Any]) -> None:
    """Atomically replace only the graph managed by this indexer."""

    session.execute_write(_replace_graph, snapshot)


def get_graph_counts(session: Any) -> dict[str, int]:
    record = session.run(
        """
        CALL () { MATCH (node:RagDocument) RETURN count(node) AS documents }
        CALL () { MATCH (node:RagChunk) RETURN count(node) AS chunks }
        CALL () { MATCH (node:RagEntity) RETURN count(node) AS entities }
        CALL () {
            MATCH ()-[edge:RELATES_TO]->()
            RETURN count(edge) AS relations
        }
        RETURN documents, chunks, entities, relations
        """
    ).single(strict=True)
    return dict(record)


def validate_graph(session: Any, snapshot: dict[str, Any]) -> dict[str, int]:
    expected = {
        name: len(snapshot[name])
        for name in ("documents", "chunks", "entities", "relations")
    }
    actual = get_graph_counts(session)
    if actual != expected:
        raise RuntimeError(
            f"Neo4j validation failed: expected {expected}, found {actual}"
        )
    return actual


def main() -> None:
    started = perf_counter()
    bundles = get_indexable_entity_relations()
    if not bundles:
        raise RuntimeError(
            "No PostgreSQL entity bundles with relations were found; "
            "refusing to replace the graph"
        )

    snapshot = build_graph_snapshot(bundles)
    if not snapshot["relations"]:
        raise RuntimeError("No graph relations were prepared")

    with GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
    ) as driver:
        driver.verify_connectivity()
        with driver.session(database=NEO4J_DATABASE) as session:
            create_constraints(session)
            replace_graph(session, snapshot)
            counts = validate_graph(session, snapshot)

    print(
        "Indexed Neo4j graph: "
        f"{counts['documents']} documents, "
        f"{counts['chunks']} chunks, "
        f"{counts['entities']} entities, "
        f"{counts['relations']} relations"
    )

    try:
        push_process_metrics(
            process="indexing",
            samples=[ProcessMetricSample(
                representation="graph",
                document_count=counts["documents"],
                item_counts={
                    "chunks": counts["chunks"],
                    "entities": counts["entities"],
                    "relations": counts["relations"],
                },
                duration_seconds=perf_counter() - started,
            )],
            pushgateway_url=PUSHGATEWAY_URL,
            job="indexing_graph",
        )
    except Exception as exc:
        print(f"[indexing] warning: could not publish metrics: {exc}")


if __name__ == "__main__":
    main()
