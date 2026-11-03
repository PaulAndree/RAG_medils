"""Create the PostgreSQL table used to authorize ingestion API keys.

Run this script from the host with::

    /home/peyzaguirre/learning/RAG_medils/.venv/bin/python create_table.py

Connection settings can be supplied with ``DATABASE_URL`` or with the
``POSTGRES_HOST``, ``POSTGRES_PORT``, ``POSTGRES_DB``, ``POSTGRES_USER``, and
``POSTGRES_PASSWORD`` environment variables.
"""

from __future__ import annotations

import hashlib
import os
import secrets
from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg import Connection


CREATE_API_KEYS_TABLE = """
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE
        CHECK (key_hash ~ '^[0-9a-f]{64}$'),
    name TEXT NOT NULL
        CHECK (btrim(name) <> ''),
    permission TEXT NOT NULL DEFAULT 'ingest'
        CHECK (permission IN ('ingest', 'read', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT api_keys_tenant_name_key UNIQUE (tenant_id, name)
)
"""


@contextmanager
def database_connection() -> Iterator[Connection]:
    """Open a connection using a URL or individual PostgreSQL settings."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        with psycopg.connect(database_url) as connection:
            yield connection
        return

    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    with psycopg.connect(
        host=host,
        port=int(os.getenv("POSTGRES_PORT", "5432" if host == "postgres" else "5433")),
        dbname=os.getenv("POSTGRES_DB", "ragdb"),
        user=os.getenv("POSTGRES_USER", "raguser"),
        password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
    ) as connection:
        yield connection


def create_api_keys_table(connection: Connection | None = None) -> None:
    """Create the table and supporting index; safe to call repeatedly."""
    if connection is not None:
        connection.execute(CREATE_API_KEYS_TABLE)
        return

    with database_connection() as new_connection:
        new_connection.execute(CREATE_API_KEYS_TABLE)


def add_client(tenant_name: str, connection: Connection | None = None) -> None:
    tenant_id = tenant_name

    # This is the secret given to the client.
    api_key = secrets.token_urlsafe(32)

    # Only this hash is stored.
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def insert_client(active_connection: Connection):
        return active_connection.execute(
            """
            INSERT INTO api_keys (
                tenant_id,
                key_hash,
                name,
                permission
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tenant_id, name) DO NOTHING
            RETURNING id
            """,
            (
                tenant_id,
                key_hash,
                tenant_id,
                "ingest",
            ),
        ).fetchone()

    if connection is not None:
        inserted_row = insert_client(connection)
    else:
        with database_connection() as new_connection:
            inserted_row = insert_client(new_connection)

    if inserted_row is None:
        print(f"Client '{tenant_id}' already exists; no new API key created.")
        return

    print("Tenant ID:", tenant_id)
    print("API key:", api_key)
    print("Save the API key now; it is not stored in PostgreSQL.")


def main() -> None:
    create_api_keys_table()
    print("PostgreSQL table 'api_keys' is ready.")
    add_client(tenant_name="Company_OEG")


if __name__ == "__main__":
    main()
