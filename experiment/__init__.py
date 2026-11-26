"""CLI experiment over the JSON company corpus: ingest, index, evaluate."""

# Puts the RAG_medils root on sys.path (retrieval imports top-level `metrics`).
import RAG_medils.ingest  # noqa: F401

TENANT_ID = "company_benchmark"
