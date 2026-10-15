"""PostgreSQL schema and persistence for document representations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from time import perf_counter
from typing import Any
from uuid import UUID

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from stores.ingestion import (
    PreparedDataset,
    PreparedDocument,
    build_chunk_id,
    build_entity_bundle_id,
    validate_summary_references,
)


def get_connection() -> psycopg.Connection:
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ragdb"),
        user=os.getenv("POSTGRES_USER", "raguser"),
        password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
    )


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY,
        source_key TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL CHECK (btrim(name) <> ''),
        title TEXT NOT NULL CHECK (btrim(title) <> ''),
        json_path TEXT NOT NULL CHECK (btrim(json_path) <> ''),
        pdf_path TEXT,
        language TEXT,
        json_hash TEXT NOT NULL
            CHECK (json_hash ~ '^[0-9a-f]{64}$'),
        pdf_hash TEXT
            CHECK (pdf_hash IS NULL OR pdf_hash ~ '^[0-9a-f]{64}$'),
        version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
        index_status TEXT NOT NULL DEFAULT 'pending'
            CHECK (index_status IN ('pending', 'indexing', 'indexed', 'failed')),
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb
            CHECK (jsonb_typeof(metadata) = 'object'),
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (id, version)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chunks (
        id UUID PRIMARY KEY,
        document_id UUID NOT NULL,
        document_version INTEGER NOT NULL CHECK (document_version > 0),
        chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
        title TEXT,
        content TEXT NOT NULL CHECK (btrim(content) <> ''),
        token_count INTEGER CHECK (token_count IS NULL OR token_count >= 0),
        content_hash TEXT NOT NULL
            CHECK (content_hash ~ '^[0-9a-f]{64}$'),
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id, document_version)
            REFERENCES documents (id, version) ON DELETE CASCADE,
        UNIQUE (document_id, document_version, chunk_index)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chunks_for_arguments (
        id UUID PRIMARY KEY,
        document_id UUID NOT NULL,
        document_version INTEGER NOT NULL CHECK (document_version > 0),
        chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
        title TEXT,
        content TEXT NOT NULL CHECK (btrim(content) <> ''),
        token_count INTEGER CHECK (token_count IS NULL OR token_count >= 0),
        content_hash TEXT NOT NULL
            CHECK (content_hash ~ '^[0-9a-f]{64}$'),
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (document_id, document_version)
            REFERENCES documents (id, version) ON DELETE CASCADE,
        UNIQUE (document_id, document_version, chunk_index)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS arguments (
        id TEXT PRIMARY KEY CHECK (btrim(id) <> ''),
        chunk_id UUID NOT NULL
            REFERENCES chunks_for_arguments (id) ON DELETE CASCADE,
        claim TEXT NOT NULL CHECK (btrim(claim) <> ''),
        evidence JSONB NOT NULL DEFAULT '[]'::jsonb
            CHECK (jsonb_typeof(evidence) = 'array')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS entities (
        id UUID PRIMARY KEY,
        chunk_id UUID NOT NULL UNIQUE
            REFERENCES chunks_for_arguments (id) ON DELETE CASCADE,
        entities JSONB NOT NULL DEFAULT '[]'::jsonb
            CHECK (jsonb_typeof(entities) = 'array'),
        relations JSONB NOT NULL DEFAULT '[]'::jsonb
            CHECK (jsonb_typeof(relations) = 'array')
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS summaries (
        node_id TEXT PRIMARY KEY CHECK (btrim(node_id) <> ''),
        summary_text TEXT NOT NULL CHECK (btrim(summary_text) <> ''),
        level INTEGER NOT NULL CHECK (level > 0),
        scope TEXT NOT NULL
            CHECK (scope IN ('document_cluster', 'document', 'catalog')),
        document_id UUID,
        catalog_id TEXT NOT NULL CHECK (btrim(catalog_id) <> ''),
        source_node_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_node_ids) = 'array'),
        source_chunk_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_chunk_ids) = 'array'),
        source_document_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_document_ids) = 'array'),
        CHECK (
            (scope = 'catalog' AND document_id IS NULL)
            OR (scope <> 'catalog' AND document_id IS NOT NULL)
        )
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS documents_index_status_idx
    ON documents (index_status)
    """,
    """
    CREATE INDEX IF NOT EXISTS chunks_document_idx
    ON chunks (document_id, chunk_index)
    """,
    """
    CREATE INDEX IF NOT EXISTS argument_chunks_document_idx
    ON chunks_for_arguments (document_id, chunk_index)
    """,
    """
    CREATE INDEX IF NOT EXISTS arguments_chunk_idx
    ON arguments (chunk_id)
    """,
    """
    CREATE INDEX IF NOT EXISTS summaries_level_scope_idx
    ON summaries (level, scope)
    """,
)

DROP_STATEMENT = """
    DROP TABLE IF EXISTS
        summaries,
        entities,
        arguments,
        chunks_for_arguments,
        chunks,
        documents
    CASCADE
"""


@dataclass(frozen=True, slots=True)
class IngestionResult:
    documents: int
    chunks: int
    argument_chunks: int
    arguments: int
    entities: int
    summaries: int
    stale_source_keys: tuple[str, ...]
    durations: dict[str, float]


def _create_tables(conn: psycopg.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        conn.execute(statement)


def create_tables(
    connection: psycopg.Connection | None = None,
) -> None:
    if connection is not None:
        _create_tables(connection)
        return
    with get_connection() as conn:
        _create_tables(conn)


def _documents_table_exists(conn: psycopg.Connection) -> bool:
    return conn.execute(
        "SELECT to_regclass('documents') IS NOT NULL"
    ).fetchone()[0]


def _existing_document_states(
    conn: psycopg.Connection,
) -> dict[str, dict[str, Any]]:
    if not _documents_table_exists(conn):
        return {}

    rows = conn.execute(
        """
        SELECT id, source_key, json_hash, pdf_hash, version
        FROM documents
        FOR UPDATE
        """
    ).fetchall()
    return {
        source_key: {
            "id": document_id,
            "json_hash": json_hash,
            "pdf_hash": pdf_hash,
            "version": version,
        }
        for document_id, source_key, json_hash, pdf_hash, version in rows
    }


def _document_versions(
    dataset: PreparedDataset,
    existing: dict[str, dict[str, Any]],
) -> dict[str, int]:
    versions: dict[str, int] = {}
    for document in dataset.documents:
        state = existing.get(document.source_key)
        if state is None:
            versions[document.source_key] = 1
            continue
        if state["id"] != document.id:
            raise RuntimeError(
                f"{document.source_key}: stored UUID does not match "
                "the deterministic UUID"
            )
        changed = (
            state["json_hash"] != document.json_hash
            or state["pdf_hash"] != document.pdf_hash
        )
        versions[document.source_key] = (
            state["version"] + 1 if changed else state["version"]
        )
    return versions


def _chunk_rows(
    document: PreparedDocument,
    version: int,
    representation: str,
) -> tuple[list[tuple[Any, ...]], dict[int, UUID]]:
    source_chunks = (
        document.chunks
        if representation == "passage"
        else document.argument_chunks
    )
    rows: list[tuple[Any, ...]] = []
    ids: dict[int, UUID] = {}
    for chunk in source_chunks:
        chunk_id = build_chunk_id(
            document.id,
            version,
            chunk.chunk_index,
            chunk.content_hash,
            representation=representation,
        )
        ids[chunk.chunk_index] = chunk_id
        rows.append(
            (
                chunk_id,
                document.id,
                version,
                chunk.chunk_index,
                chunk.title,
                chunk.content,
                chunk.token_count,
                chunk.content_hash,
            )
        )
    return rows, ids


CHUNK_INSERT = """
    INSERT INTO {table} (
        id,
        document_id,
        document_version,
        chunk_index,
        title,
        content,
        token_count,
        content_hash
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""


def _replace_document(
    conn: psycopg.Connection,
    document: PreparedDocument,
    version: int,
    exists: bool,
) -> dict[str, float]:
    durations = {
        "passages": 0.0,
        "arguments": 0.0,
        "graph": 0.0,
    }
    started = perf_counter()
    if exists:
        conn.execute(
            "DELETE FROM chunks WHERE document_id = %s",
            (document.id,),
        )
        durations["passages"] += perf_counter() - started

        started = perf_counter()
        conn.execute(
            "DELETE FROM chunks_for_arguments WHERE document_id = %s",
            (document.id,),
        )
        durations["arguments"] += perf_counter() - started

        started = perf_counter()
        conn.execute(
            """
            UPDATE documents
            SET
                name = %s,
                title = %s,
                json_path = %s,
                pdf_path = %s,
                language = %s,
                json_hash = %s,
                pdf_hash = %s,
                version = %s,
                index_status = 'pending',
                metadata = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                document.name,
                document.title,
                document.json_path,
                document.pdf_path,
                document.language,
                document.json_hash,
                document.pdf_hash,
                version,
                Jsonb(document.metadata),
                document.id,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO documents (
                id,
                source_key,
                name,
                title,
                json_path,
                pdf_path,
                language,
                json_hash,
                pdf_hash,
                version,
                index_status,
                metadata
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, 'pending', %s
            )
            """,
            (
                document.id,
                document.source_key,
                document.name,
                document.title,
                document.json_path,
                document.pdf_path,
                document.language,
                document.json_hash,
                document.pdf_hash,
                version,
                Jsonb(document.metadata),
            ),
        )
    durations["passages"] += perf_counter() - started

    started = perf_counter()
    passage_rows, _ = _chunk_rows(
        document,
        version,
        "passage",
    )
    durations["passages"] += perf_counter() - started

    started = perf_counter()
    argument_chunk_rows, argument_chunk_ids = _chunk_rows(
        document,
        version,
        "argument",
    )
    durations["arguments"] += perf_counter() - started

    with conn.cursor() as cursor:
        started = perf_counter()
        if passage_rows:
            cursor.executemany(
                CHUNK_INSERT.format(table="chunks"),
                passage_rows,
            )
        durations["passages"] += perf_counter() - started

        started = perf_counter()
        if argument_chunk_rows:
            cursor.executemany(
                CHUNK_INSERT.format(table="chunks_for_arguments"),
                argument_chunk_rows,
            )
        if document.arguments:
            cursor.executemany(
                """
                INSERT INTO arguments (id, chunk_id, claim, evidence)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (
                        argument.id,
                        argument_chunk_ids[argument.chunk_index],
                        argument.claim,
                        Jsonb(list(argument.evidence)),
                    )
                    for argument in document.arguments
                ],
            )
        durations["arguments"] += perf_counter() - started

        started = perf_counter()
        if document.entity_bundles:
            cursor.executemany(
                """
                INSERT INTO entities (
                    id,
                    chunk_id,
                    entities,
                    relations
                )
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (
                        build_entity_bundle_id(
                            argument_chunk_ids[bundle.chunk_index]
                        ),
                        argument_chunk_ids[bundle.chunk_index],
                        Jsonb(list(bundle.entities)),
                        Jsonb(list(bundle.relations)),
                    )
                    for bundle in document.entity_bundles
                ],
            )
        durations["graph"] += perf_counter() - started

    return durations


def _replace_summaries(
    conn: psycopg.Connection,
    dataset: PreparedDataset,
) -> None:
    conn.execute("DELETE FROM summaries")
    if not dataset.summaries:
        return
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO summaries (
                node_id,
                summary_text,
                level,
                scope,
                document_id,
                catalog_id,
                source_node_ids,
                source_chunk_ids,
                source_document_ids
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    summary.node_id,
                    summary.summary_text,
                    summary.level,
                    summary.scope,
                    summary.document_id,
                    summary.catalog_id,
                    Jsonb(list(summary.source_node_ids)),
                    Jsonb(list(summary.source_chunk_ids)),
                    Jsonb(list(summary.source_document_ids)),
                )
                for summary in dataset.summaries
            ],
        )


def _persist_dataset(
    conn: psycopg.Connection,
    dataset: PreparedDataset,
    rebuild: bool,
) -> IngestionResult:
    existing = (
        {}
        if rebuild
        else _existing_document_states(conn)
    )
    versions = _document_versions(dataset, existing)

    # This is the last validation that depends on database state. It runs
    # before any DDL or data mutation.
    validate_summary_references(dataset, versions)

    if rebuild:
        conn.execute(DROP_STATEMENT)
    _create_tables(conn)

    durations = {
        "passages": 0.0,
        "arguments": 0.0,
        "summaries": 0.0,
        "graph": 0.0,
    }
    for document in dataset.documents:
        document_durations = _replace_document(
            conn,
            document,
            versions[document.source_key],
            document.source_key in existing,
        )
        for representation, duration in document_durations.items():
            durations[representation] += duration

    started = perf_counter()
    _replace_summaries(conn, dataset)
    durations["summaries"] = perf_counter() - started

    source_keys = {
        document.source_key
        for document in dataset.documents
    }
    stale_source_keys = tuple(sorted(set(existing) - source_keys))

    return IngestionResult(
        documents=len(dataset.documents),
        chunks=sum(
            len(document.chunks)
            for document in dataset.documents
        ),
        argument_chunks=sum(
            len(document.argument_chunks)
            for document in dataset.documents
        ),
        arguments=sum(
            len(document.arguments)
            for document in dataset.documents
        ),
        entities=sum(
            len(document.entity_bundles)
            for document in dataset.documents
        ),
        summaries=len(dataset.summaries),
        stale_source_keys=stale_source_keys,
        durations=durations,
    )


def persist_dataset(
    dataset: PreparedDataset,
    *,
    rebuild: bool = False,
    connection: psycopg.Connection | None = None,
) -> IngestionResult:
    """Atomically replace all discovered representation rows."""

    if connection is not None:
        return _persist_dataset(
            connection,
            dataset,
            rebuild,
        )

    with get_connection() as conn:
        return _persist_dataset(
            conn,
            dataset,
            rebuild,
        )


def get_indexable_chunks() -> list[dict[str, Any]]:
    """Return one passage row per future Qdrant point."""

    query = """
        SELECT
            c.id::text AS chunk_id,
            d.id::text AS document_id,
            d.name AS doc_name,
            d.title AS document_title,
            c.title AS chunk_title,
            c.content,
            c.chunk_index,
            c.token_count,
            d.language,
            d.version AS document_version
        FROM chunks AS c
        JOIN documents AS d
          ON d.id = c.document_id
         AND d.version = c.document_version
        ORDER BY d.source_key, c.chunk_index
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

def get_indexable_arguments() -> list[dict[str, Any]]:
    """Return one extracted argument per Qdrant point."""

    query = """
        SELECT
            a.id::text AS argument_id,
            a.claim,
            a.evidence,
            c.id::text AS source_chunk_id,
            c.document_id::text AS document_id,
            d.name AS doc_name,
            d.title AS document_title,
            c.title AS chunk_title,
            c.content AS source_content,
            c.chunk_index,
            c.token_count,
            d.language,
            d.version AS document_version
        FROM arguments AS a
        JOIN chunks_for_arguments AS c
            ON c.id = a.chunk_id
        JOIN documents AS d
            ON d.id = c.document_id
            AND d.version = c.document_version
        ORDER BY d.source_key, c.chunk_index
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()

def get_indexable_summaries() -> list[dict[str, Any]]:
    """Return one summary node per Qdrant point."""

    query = """
        SELECT
            s.node_id,
            s.summary_text,
            s.level,
            s.scope,
            s.document_id::text AS document_id,
            s.catalog_id,
            s.source_node_ids,
            s.source_chunk_ids,
            s.source_document_ids
        FROM summaries AS s
        ORDER BY s.level, s.node_id
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_indexable_entity_relations() -> list[dict[str, Any]]:
    """Return entity bundles that contain at least one relation."""

    query = """
        SELECT
            e.id::text AS bundle_id,
            e.chunk_id::text AS chunk_id,
            e.entities,
            e.relations,
            c.document_id::text AS document_id,
            c.document_version,
            c.chunk_index,
            c.title AS chunk_title,
            c.content AS chunk_content,
            d.name AS doc_name,
            d.title AS document_title
        FROM entities AS e
        JOIN chunks_for_arguments AS c
          ON c.id = e.chunk_id
        JOIN documents AS d
          ON d.id = c.document_id
         AND d.version = c.document_version
        WHERE jsonb_array_length(e.relations) > 0
        ORDER BY d.source_key, c.chunk_index
    """

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
