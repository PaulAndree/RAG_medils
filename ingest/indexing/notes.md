
POSTGRES_HOST=127.0.0.1 \
POSTGRES_PORT=5433 \
QDRANT_URL=http://127.0.0.1:6337 \
EMBEDDING_URL=http://127.0.0.1:8089/embed \
PUSHGATEWAY_URL=http://127.0.0.1:9093 \
python -m indexing.main

- The pipeline builds only the summaries collection.
- That collection contains the complete RAPTOR hierarchy: level-zero passages
  and all higher summary levels.
- It stores named dense and sparse vectors for hybrid retrieval.
- Because there is currently one corpus, retrieval does not need catalog
  filtering.
- `summaries_embeddings_live` is the stable alias used by retrieval. A rebuild
  creates and validates a replacement collection, then moves the alias
  atomically. After activation is verified, obsolete generated collections are
  deleted. Failed builds are also deleted unless an alias already points to
  them. Collections referenced by any alias and unrelated collections are
  preserved. No rollback copies are kept.
- Rebuilds and cleanup share a PostgreSQL advisory lock across API and CLI runs.
  During a rebuild the live and replacement collections temporarily coexist;
  after successful cleanup only the live generated collection remains under
  normal operation. Cleanup errors are logged and retried on the next successful
  rebuild; an abrupt process termination may also leave a temporary collection.

ACTIVE_ALIAS = "summaries_embeddings_live"




Qdrant Embedding requirement
BM25 requires Qdrant’s IDF modifier:
models.SparseVectorParams(
    modifier=models.Modifier.IDF,
)
MILCO must not use that modifier. Therefore, if you switch the indexing pipeline from MILCO to BM25, change:
SPARSE_MODEL = "bm25"
SPARSE_VECTOR = "bm25"
in both indexing and retrieval, restore Modifier.IDF, and fully rebuild the collections. FastEmbed explicitly requires Qdrant-side IDF for its BM25 vectors.
