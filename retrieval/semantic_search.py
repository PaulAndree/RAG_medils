import os

from qdrant_client import QdrantClient, models

from indexing.embedding_api import DENSE_MODEL, SPARSE_MODEL, embed_texts
from metrics import RETRIEVAL_DURATION


QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
PASSAGES_COLLECTION = os.getenv(
    "PASSAGES_QDRANT_COLLECTION",
    "passages_embeddings_live",
)
SUMMARIES_COLLECTION = os.getenv(
    "SUMMARIES_QDRANT_COLLECTION",
    "summaries_embeddings_live",
)

DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"

client = QdrantClient(url=QDRANT_URL)


def search_documents(
    question,
    limit,
    collection=PASSAGES_COLLECTION,
    qdrant_client=client,
):
    candidate_limit = max(20, limit * 5)
    dense_query = embed_texts([question], DENSE_MODEL, "query")[0]
    sparse_query = embed_texts([question], SPARSE_MODEL, "query")[0]

    result = qdrant_client.query_points(
        collection_name=collection,
        prefetch=[
            models.Prefetch(
                query=dense_query,
                using=DENSE_VECTOR,
                limit=candidate_limit,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_query["indices"],
                    values=sparse_query["values"],
                ),
                using=SPARSE_VECTOR,
                limit=candidate_limit,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
        with_payload=True,
    )

    return result.points


def search_passages(question, limit, qdrant_client=client):
    with RETRIEVAL_DURATION.labels(
        retrieval_type="documents",
    ).time():
        return search_documents(
            question,
            limit,
            collection=PASSAGES_COLLECTION,
            qdrant_client=qdrant_client,
        )


def search_summaries(question, limit, qdrant_client=client):
    with RETRIEVAL_DURATION.labels(
        retrieval_type="summaries",
    ).time():
        return search_documents(
            question,
            limit,
            collection=SUMMARIES_COLLECTION,
            qdrant_client=qdrant_client,
        )
