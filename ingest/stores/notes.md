# Document and summary storage

Document registration and summary storage are independent:

- `prepare_document(path, metadata, tenant_id=...)` prepares an original file.
- `store_document(document)` commits its row with `has_summary=false`, or returns
  the existing tenant/hash match without rewriting metadata or completion.
- `prepare_summaries(summaries_directory)` reads RAPTOR level files only.
- `store_summaries(nodes, tenant_id=...)` validates registered document IDs and
  complete provenance, replaces the affected catalogs, and marks their documents
  complete in the same transaction. Other catalogs remain intact.

The upload API coordinates these operations automatically. See
[the ingestion API guide](../../ingest/README.md).

For importing already generated summaries against registered documents:

```bash
POSTGRES_HOST=localhost python -m stores.main_ingestion --data-dir PATH_TO_TENANT_ROOT
```

The directory must contain `summaries/level_*.json`. The command never registers
or deletes documents. `--rebuild` has been removed. Each import must include the
complete hierarchy for each affected catalog, including documents already stored
in that catalog. Upload new documents through the API before importing summaries.

Schema initialization runs at API/CLI startup and creates the current tables
and indexes if missing. The schema includes tenant ownership, a tenant/hash
uniqueness constraint, `has_summary`, and the summary columns `createdDateTime`
and `modifiedDateTime`. During summary storage, dates are copied from the
registered document's metadata for every non-catalog level; catalog dates stay
null. Repeated initialization preserves existing rows. `index_status` tracks
vector indexing separately.

Run the focused checks from the RAG project root:

```bash
RUN_POSTGRES_TESTS=1 .venv/bin/python -m unittest \
  tests.test_stores_raptor tests.test_stores_postgres tests.test_store_metrics \
  tests.test_ingest_api tests.test_ingest_processing tests.test_ingest_integration
```

Database tests use unique isolated schemas. They never migrate or clear the
application's existing tables. OCR, chunking, embeddings, and generation are
mocked in integration tests.
