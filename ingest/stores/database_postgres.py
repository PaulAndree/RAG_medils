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

from RAG_medils.ingest.stores.ingestion import (
    InputValidationError,
    PreparedSummary,
    catalog_id_for_tenant,
    PreparedDocument,
    validate_summary_references,
)


def get_connection() -> psycopg.Connection:
    if database_url := os.getenv("DATABASE_URL"):
        return psycopg.connect(database_url)
    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    return psycopg.connect(
        host=host,
        port=int(os.getenv("POSTGRES_PORT", "5432" if host == "postgres" else "5433")),
        dbname=os.getenv("POSTGRES_DB", "ragdb"),
        user=os.getenv("POSTGRES_USER", "raguser"),
        password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
    )


SCHEMA_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY,
        source_key TEXT NOT NULL UNIQUE,
        tenant_id TEXT,
        has_summary BOOLEAN NOT NULL DEFAULT FALSE,
        name TEXT NOT NULL CHECK (btrim(name) <> ''),
        title TEXT NOT NULL CHECK (btrim(title) <> ''),
        doc_path TEXT,
        language TEXT,
        doc_hash TEXT
            CHECK (doc_hash IS NULL OR doc_hash ~ '^[0-9a-f]{64}$'),
        index_status TEXT NOT NULL DEFAULT 'pending'
            CHECK (index_status IN ('pending', 'indexing', 'indexed', 'failed')),
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb
            CHECK (jsonb_typeof(metadata) = 'object'),
        CONSTRAINT documents_tenant_hash_key UNIQUE (tenant_id, doc_hash)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS summaries (
        node_id TEXT PRIMARY KEY CHECK (btrim(node_id) <> ''),
        summary_text TEXT NOT NULL CHECK (btrim(summary_text) <> ''),
        level INTEGER NOT NULL CHECK (level >= 0),
        scope TEXT NOT NULL
            CHECK (scope IN (
                'passage', 'document_cluster', 'document', 'catalog'
            )),
        document_id UUID
            REFERENCES documents (id) ON DELETE CASCADE,
        document_title TEXT CHECK (btrim(document_title) <> ''),
        catalog_id TEXT NOT NULL CHECK (btrim(catalog_id) <> ''),
        source_key TEXT,
        chunk_index INTEGER
            CHECK (chunk_index IS NULL OR chunk_index >= 0),
        title TEXT,
        token_count INTEGER
            CHECK (token_count IS NULL OR token_count >= 0),
        "createdDateTime" TIMESTAMPTZ,
        "modifiedDateTime" TIMESTAMPTZ,
        source_node_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_node_ids) = 'array'),
        source_chunk_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_chunk_ids) = 'array'),
        source_document_ids JSONB NOT NULL
            CHECK (jsonb_typeof(source_document_ids) = 'array'),
        CHECK (
            (scope = 'catalog' AND document_id IS NULL AND document_title IS NULL)
            OR (scope <> 'catalog' AND document_id IS NOT NULL AND document_title IS NOT NULL)
        )
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS documents_index_status_idx
    ON documents (index_status)
    """,
    """
    CREATE INDEX IF NOT EXISTS summaries_level_scope_idx
    ON summaries (level, scope)
    """,
    """
    CREATE INDEX IF NOT EXISTS summaries_document_level_idx
    ON summaries (document_id, level)
    """,
)

@dataclass(frozen=True, slots=True)
class DocumentRegistration:
    document_id: UUID
    tenant_id: str | None
    has_summary: bool
    created: bool


@dataclass(frozen=True, slots=True)
class IngestionResult:
    documents: int
    summaries: int
    durations: dict[str, float]


def initialize_database(connection: psycopg.Connection | None = None) -> None:
    """Create current storage tables and indexes if missing."""
    if connection is None:
        with get_connection() as conn:
            initialize_database(conn)
        return
    with connection.transaction():
        # Startup and CLI initialization may overlap within the same schema.
        connection.execute("SELECT pg_advisory_xact_lock(hashtextextended(current_schema() || ':document_schema', 0))")
        for statement in SCHEMA_STATEMENTS:
            connection.execute(statement)


def _copy_document_timestamps(
    connection: psycopg.Connection, catalog_ids: list[str],
) -> None:
    """Copy document metadata dates to every non-catalog summary level."""
    connection.execute(
        """
        UPDATE summaries AS s
        SET "createdDateTime" = NULLIF(d.metadata ->> 'createdDateTime', '')::timestamptz,
            "modifiedDateTime" = NULLIF(d.metadata ->> 'modifiedDateTime', '')::timestamptz
        FROM documents AS d
        WHERE s.document_id = d.id AND s.scope <> 'catalog'
          AND s.catalog_id = ANY(%s)
        """,
        (catalog_ids,),
    )


def store_document(
    document: PreparedDocument,
    *,
    connection: psycopg.Connection | None = None,
) -> DocumentRegistration:
    """Register an original file, preserving any existing tenant/hash match."""
    if connection is None:
        with get_connection() as conn:
            return store_document(document, connection=conn)
    with connection.transaction():
        row = connection.execute(
            """
            INSERT INTO documents (id, source_key, tenant_id, name, title,
                                   doc_path, language, doc_hash, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tenant_id, doc_hash) DO NOTHING
            RETURNING id, tenant_id, has_summary
            """,
            (document.id, document.source_key, document.tenant_id, document.name,
             document.title, document.doc_path, document.language, document.doc_hash,
             Jsonb(document.metadata)),
        ).fetchone()
        created = row is not None
        if not created:
            row = connection.execute(
                "SELECT id, tenant_id, has_summary FROM documents WHERE tenant_id = %s AND doc_hash = %s",
                (document.tenant_id, document.doc_hash),
            ).fetchone()
        return DocumentRegistration(*row, created=created)


def get_document(document_id: UUID, tenant_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT id, tenant_id, has_summary FROM documents WHERE id = %s AND tenant_id = %s",
                (document_id, tenant_id),
            )
            return cursor.fetchone()


def get_tenant_documents(tenant_id: str) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("SELECT * FROM documents WHERE tenant_id = %s ORDER BY source_key", (tenant_id,))
            return cursor.fetchall()


def get_pending_tenants() -> list[str]:
    with get_connection() as conn:
        return [row[0] for row in conn.execute(
            "SELECT DISTINCT tenant_id FROM documents "
            "WHERE NOT has_summary AND tenant_id IS NOT NULL ORDER BY tenant_id"
        ).fetchall()]


def _insert_summaries(conn: psycopg.Connection, summaries: tuple[PreparedSummary, ...]) -> None:
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO summaries (
                node_id,
                summary_text,
                level,
                scope,
                document_id,
                document_title,
                catalog_id,
                source_key,
                chunk_index,
                title,
                token_count,
                source_node_ids,
                source_chunk_ids,
                source_document_ids
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
            """,
            [
                (
                    summary.node_id,
                    summary.summary_text,
                    summary.level,
                    summary.scope,
                    summary.document_id,
                    summary.document_title,
                    summary.catalog_id,
                    summary.source_key,
                    summary.chunk_index,
                    summary.title,
                    summary.token_count,
                    Jsonb(list(summary.source_node_ids)),
                    Jsonb(list(summary.source_chunk_ids)),
                    Jsonb(list(summary.source_document_ids)),
                )
                for summary in summaries
            ],
        )


def store_summaries(
    summaries: tuple[PreparedSummary, ...],
    *,
    tenant_id: str | None = None,
    connection: psycopg.Connection | None = None,
) -> IngestionResult:
    """Replace complete affected catalogs and mark their documents atomically.

    Original document metadata is never rewritten. When a caller supplies a
    connection, the operation uses a savepoint inside any existing transaction.
    """
    if connection is None:
        with get_connection() as conn:
            return store_summaries(summaries, tenant_id=tenant_id, connection=conn)
    started = perf_counter()
    with connection.transaction():
        catalog_ids = sorted({node.catalog_id for node in summaries})
        for catalog_id in catalog_ids:
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended(current_schema() || ':catalog:' || %s, 0))",
                (catalog_id,),
            )
        document_ids = sorted({node.document_id for node in summaries if node.document_id is not None})
        rows = connection.execute(
            "SELECT id, source_key, tenant_id FROM documents WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
            (document_ids,),
        ).fetchall()
        registered = {row[0]: row[1] for row in rows}
        owners = {row[0]: row[2] for row in rows}
        validate_summary_references(summaries, registered)
        for node in summaries:
            if node.document_id is None:
                continue
            owner = owners[node.document_id]
            if tenant_id is not None and owner != tenant_id:
                raise InputValidationError("summary references a document outside the requested tenant")
            if owner is not None and node.catalog_id != catalog_id_for_tenant(owner):
                raise InputValidationError("summary catalog does not match document tenant")
        existing = connection.execute(
            "SELECT DISTINCT document_id FROM summaries WHERE catalog_id = ANY(%s) AND document_id IS NOT NULL",
            (catalog_ids,),
        ).fetchall()
        if {row[0] for row in existing} - set(document_ids):
            raise InputValidationError("replacement must include all existing documents in each affected catalog")
        outside = connection.execute(
            "SELECT 1 FROM summaries WHERE document_id = ANY(%s) AND NOT (catalog_id = ANY(%s)) LIMIT 1",
            (document_ids, catalog_ids),
        ).fetchone()
        if outside:
            raise InputValidationError("document already belongs to a different catalog")
        connection.execute("DELETE FROM summaries WHERE catalog_id = ANY(%s)", (catalog_ids,))
        _insert_summaries(connection, summaries)
        _copy_document_timestamps(connection, catalog_ids)
        connection.execute(
            "UPDATE documents SET has_summary = TRUE, index_status = 'pending' WHERE id = ANY(%s)",
            (document_ids,),
        )
    return IngestionResult(len(document_ids), len(summaries), {"summaries": perf_counter() - started})


def get_indexable_summaries() -> list[dict[str, Any]]:
    """Return one summary node per Qdrant point."""

    query = """
        SELECT
            s.node_id,
            s.summary_text,
            s.level,
            s.scope,
            s."createdDateTime",
            s."modifiedDateTime",
            s.document_id::text AS document_id,
            s.document_title,
            s.catalog_id,
            s.source_key,
            s.chunk_index,
            s.title,
            s.token_count,
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
