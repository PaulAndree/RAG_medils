# Automatic document ingestion

Start the API from the `learning` directory using the RAG virtual environment:

```bash
cd /home/peyzaguirre/learning
RAG_medils/.venv/bin/python -m uvicorn ingest.api:app --host 127.0.0.1 --port 8009 --workers 1
```

The service uses one API worker. Each upload saves its original file and commits
its document row before responding. OCR, RAPTOR representation, and summary
storage then run automatically in the background, followed by indexing through
`indexing.main.run_pipeline()`. No processing command is needed.
Processing is serialized within each tenant; other requests can continue.
Indexing rebuilds the shared Qdrant collection from all stored summaries.
API-triggered indexing runs are serialized across tenants in the single worker.
The indexer also uses a PostgreSQL lock to coordinate API and command-line runs.
After validating and activating a replacement, it deletes obsolete generated
collections instead of retaining rollback copies. Failed builds are cleaned up
without deleting the live index. The live and replacement collections coexist
temporarily during a rebuild.

The existing `api_keys` table authorizes requests. Configure the same PostgreSQL
database for the API and RAG stores through `DATABASE_URL` or `POSTGRES_HOST`,
`POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`. Host
connections default to `127.0.0.1:5433`; the Docker hostname `postgres` defaults
to port 5432. On a fresh database, startup creates the current document and
summary tables and indexes. Repeated startup preserves existing rows.
The `api_keys` table and an ingestion key must be provisioned separately.

## Upload and check completion

Set `INGEST_API_KEY` to an existing ingestion/admin key, then send one file and
an optional JSON metadata object:

```bash
curl http://127.0.0.1:8009/ingest \
  -H "Authorization: Bearer $INGEST_API_KEY" \
  -F 'file=@paper.pdf' \
  -F 'metadata={"title":"Paper title","author":"Ada","repository_id":"papers"}'
```

Only `.pdf` and UTF-8 `.md` files are accepted. Metadata may include custom or
nested JSON values. The authenticated key supplies tenant ownership.

Document metadata may include `createdDateTime` and `modifiedDateTime` as
ISO 8601 timestamps with a timezone, such as `2026-10-29T14:30:00Z`.
When summaries are stored, these source-document dates are copied into the
`"createdDateTime"` and `"modifiedDateTime"` columns (`TIMESTAMPTZ`) of
`summaries` for passages, document clusters, and document summaries.
Catalog summaries and missing, null, or empty dates remain `NULL`.
Both columns are included when `summaries` is created. Dates are copied from
`documents.metadata` during each summary-storage transaction, starting with
the first document ingestion.

Each passage, document cluster, and document summary carries `document_title`
from the registered `documents.title`, through the generated JSON, PostgreSQL,
and Qdrant payload. Uploads without a metadata title use the original filename
stem; standalone Markdown builds also use the filename stem. The existing
`title` field remains the passage's section title. Catalog summaries have a
null `document_title` because they combine documents. Titles need not be unique;
`document_id` is the foreign key. Every level retains its `catalog_id`, which is
`tenant:<tenant_id>` for API ingestion.

New/pending documents return HTTP 202:

```json
{"document_id":"<uuid>","tenant_id":"Company_OEG","has_summary":false}
```

Query completion using a key for the same tenant:

```bash
curl http://127.0.0.1:8009/ingest/DOCUMENT_UUID \
  -H "Authorization: Bearer $INGEST_API_KEY"
```

`has_summary=true` means the complete representation was committed to PostgreSQL.
A false value means processing has not completed, including failed attempts;
processing errors are recorded in the server log. Indexing runs after summary
storage, so `has_summary=true` does not confirm that indexing has finished.
This indexing entry point does not currently update `index_status`.

An identical file uploaded within the same tenant reuses the existing document
and preserves its original metadata. Completed duplicates return HTTP 200 and
schedule an indexing run without regenerating summaries;
pending duplicates schedule another processing attempt. Different tenants have
independent documents and catalogs.

The example client also accepts directories and sends one request per file:

```bash
RAG_medils/.venv/bin/python python_client/ingestion_client.py ./papers \
  --metadata '{"repository_id":"papers"}'
```

## Storage and recovery

`INGEST_DATA_ROOT` defaults to `RAG_medils/data`. Files are organized under
`tenants/<sha256-of-tenant>/` with `documents/` for originals,
`pdf_parsed_output/` for Markdown, and `summaries/` for RAPTOR output. Source keys
preserve the original filename stem beneath a unique document directory.

Configure PDF conversion with `OCR_URL` (default
`http://127.0.0.1:8084/services/ocr`). Existing chunking, model, embedding, and
Pushgateway environment settings continue to apply.

Original files and metadata survive processing failures. Summary writes and
completion flags commit together. Startup automatically schedules tenants with
unfinished documents. A later new or pending upload for that tenant also retries
unfinished work. Completed hierarchies are reused; uncommitted cached outputs
are rebuilt. Background tasks run inside the API service and resume on its next
startup if the service stops.

Indexing stages stop on the first failure and log the error. Stored summaries
remain available; reupload a completed document to retry indexing. Configure
`QDRANT_URL` (host default `http://127.0.0.1:6337`) and the embedding service
for access from the API host. Docker Compose sets `QDRANT_URL` to
`http://qdrant:6333` inside its network. Restart
recovery currently handles unfinished summarization; an indexing-only failure
requires a retry upload or a manual `python -m indexing.main` run.
