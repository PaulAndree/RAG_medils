from prometheus_client import Histogram


INDEX_DURATION = Histogram(
    "rag_index_duration_seconds",
    "Time spent embedding and indexing documents",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)


RETRIEVAL_DURATION = Histogram(
    "rag_retrieval_duration_seconds",
    "Time spent embedding a query and retrieving documents",
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)