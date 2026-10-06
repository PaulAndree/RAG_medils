import os
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from sql_rag.ingestion import PreparedDocument, build_chunk_id

def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ragdb"),
        user=os.getenv("POSTGRES_USER", "raguser"),
        password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
    )

def create_tables():
    documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY,
            source_key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            json_path TEXT NOT NULL,
            pdf_path TEXT,
            language TEXT,
            json_hash TEXT NOT NULL,
            pdf_hash TEXT,
            version INTEGER NOT NULL DEFAULT 1,
            index_status TEXT NOT NULL DEFAULT 'pending',
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT documents_source_key_not_blank
                CHECK (btrim(source_key) <> ''),

            CONSTRAINT documents_name_not_blank
                CHECK (btrim(name) <> ''),

            CONSTRAINT documents_title_not_blank
                CHECK (btrim(title) <> ''),

            CONSTRAINT documents_json_path_not_blank
                CHECK (btrim(json_path) <> ''),

            CONSTRAINT documents_json_hash_valid
                CHECK (json_hash ~ '^[0-9a-f]{64}$'),

            CONSTRAINT documents_pdf_hash_valid
                CHECK (
                    pdf_hash IS NULL
                    OR pdf_hash ~ '^[0-9a-f]{64}$'
                ),

            CONSTRAINT documents_version_positive
                CHECK (version > 0),

            CONSTRAINT documents_index_status_valid
                CHECK (
                    index_status IN (
                        'pending',
                        'indexing',
                        'indexed',
                        'failed'
                    )
                ),

            CONSTRAINT documents_metadata_is_object
                CHECK (jsonb_typeof(metadata) = 'object'),

            CONSTRAINT documents_id_version_unique
                UNIQUE (id, version)
        )
    """

    chunks_table = """
        CREATE TABLE IF NOT EXISTS chunks (
            id UUID PRIMARY KEY,
            document_id UUID NOT NULL,
            document_version INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            token_count INTEGER,
            page_start INTEGER,
            page_end INTEGER,
            content_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT chunks_document_version_fk
                FOREIGN KEY (document_id, document_version)
                REFERENCES documents (id, version)
                ON DELETE CASCADE,

            CONSTRAINT chunks_document_index_unique
                UNIQUE (document_id, chunk_index),

            CONSTRAINT chunks_document_version_positive
                CHECK (document_version > 0),

            CONSTRAINT chunks_index_nonnegative
                CHECK (chunk_index >= 0),

            CONSTRAINT chunks_content_not_blank
                CHECK (btrim(content) <> ''),

            CONSTRAINT chunks_token_count_nonnegative
                CHECK (
                    token_count IS NULL
                    OR token_count >= 0
                ),

            CONSTRAINT chunks_page_start_positive
                CHECK (
                    page_start IS NULL
                    OR page_start > 0
                ),

            CONSTRAINT chunks_page_end_positive
                CHECK (
                    page_end IS NULL
                    OR page_end > 0
                ),

            CONSTRAINT chunks_page_range_valid
                CHECK (
                    page_start IS NULL
                    OR page_end IS NULL
                    OR page_end >= page_start
                ),

            CONSTRAINT chunks_content_hash_valid
                CHECK (content_hash ~ '^[0-9a-f]{64}$')
        )
    """

    index_statement = """
        CREATE INDEX IF NOT EXISTS documents_index_status_idx
        ON documents (index_status)
    """

    with get_connection() as conn:
        conn.execute(documents_table)
        conn.execute(chunks_table)
        conn.execute(index_statement)


class PdfSourceDriftError(RuntimeError):
    """The PDF changed without corresponding JSON changes."""


@dataclass(frozen=True, slots=True)
class PersistenceResult:
    action: Literal["inserted", "updated", "skipped"]
    source_key: str
    document_id: UUID
    version: int
    chunk_count: int
    pdf_attached: bool = False


def _insert_chunks(
    conn: psycopg.Connection,
    document: PreparedDocument,
    document_version: int,
) -> None:
    rows = []

    for chunk in document.chunks:
        chunk_id = build_chunk_id(
            document_id=document.id,
            document_version=document_version,
            chunk_index=chunk.chunk_index,
            content_hash=chunk.content_hash,
        )

        rows.append(
            (
                chunk_id,
                document.id,
                document_version,
                chunk.chunk_index,
                chunk.title,
                chunk.content,
                chunk.token_count,
                chunk.page_start,
                chunk.page_end,
                chunk.content_hash,
            )
        )

    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO chunks (
                id,
                document_id,
                document_version,
                chunk_index,
                title,
                content,
                token_count,
                page_start,
                page_end,
                content_hash
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            )
            """,
            rows,
        )


def _insert_new_document(
    conn: psycopg.Connection,
    document: PreparedDocument,
) -> PersistenceResult:
    document_version = 1

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
            document_version,
            Jsonb(document.metadata),
        ),
    )

    _insert_chunks(
        conn,
        document,
        document_version,
    )

    return PersistenceResult(
        action="inserted",
        source_key=document.source_key,
        document_id=document.id,
        version=document_version,
        chunk_count=len(document.chunks),
    )



def persist_document(
    document: PreparedDocument,
) -> PersistenceResult:
    with get_connection() as conn:
        existing = conn.execute(
            """
            SELECT
                id,
                json_hash,
                pdf_hash,
                json_path,
                pdf_path,
                version
            FROM documents
            WHERE source_key = %s
            FOR UPDATE
            """,
            (document.source_key,),
        ).fetchone()

        if existing is None:
            return _insert_new_document(
                conn,
                document,
            )

        (
            stored_id,
            stored_json_hash,
            stored_pdf_hash,
            stored_version,
        ) = existing

        if stored_id != document.id:
            raise RuntimeError(
                f"{document.source_key}: stored UUID "
                "does not match deterministic UUID"
            )

        if (
            stored_json_hash != document.json_hash
            or stored_pdf_hash != document.pdf_hash
        ):
            raise PdfSourceDriftError(
                f"{document.source_key}: the source already exists "
                "with different content"
            )

        return PersistenceResult(
            action="skipped",
            source_key=document.source_key,
            document_id=document.id,
            version=stored_version,
            chunk_count=len(document.chunks),
        )

#detects database documents whose source JSON file is no longer present.
def find_stale_source_keys(
    discovered_source_keys: set[str],
) -> tuple[str, ...]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT source_key
            FROM documents
            ORDER BY source_key
            """
        ).fetchall()

    return tuple(
        source_key
        for (source_key,) in rows
        if source_key not in discovered_source_keys
    )


def get_documents():
    raise RuntimeError(
        "The legacy document reader is disabled. "
        "The Qdrant indexer will be updated in Milestone 2."
    )