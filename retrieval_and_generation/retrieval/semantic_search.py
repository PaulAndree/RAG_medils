import os
from datetime import date, datetime, timedelta
from time import time

from qdrant_client import QdrantClient, models

from RAG_medils.ingest.indexing.embedding_api import DENSE_MODEL, SPARSE_MODEL, embed_texts

from metrics import RETRIEVAL_DURATION


QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6337")
SUMMARIES_COLLECTION = os.getenv(
    "SUMMARIES_QDRANT_COLLECTION",
    "summaries_embeddings_live",
)

DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"

client = QdrantClient(url=QDRANT_URL)



def rerank_by_recency(points, reference_ts, max_bonus=0.05, half_life_days=90):
    def final_score(point):
        raw_date = (point.payload or {}).get("modifiedDateTime")
    
        if not raw_date:
            return point.score  # Sin bonus para fechas ausentes o futuras.
        try:
            parsed = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return point.score
            event_ts = parsed.timestamp()
        except (TypeError, ValueError):
            return point.score
        if event_ts > reference_ts:
            return point.score
        age_days = (reference_ts - event_ts) / 86_400
        bonus = max_bonus * 2 ** (-age_days / half_life_days)
        return point.score + bonus

    return sorted(points, key=final_score, reverse=True)


def search_summaries(
    question,
    limit,
    tenant_id: str,
    qdrant_client=client,
    createdDate_greater_than=None,
    createdDate_less_than=None
):
    if not tenant_id:
        raise ValueError("tenant_id is required")
    tenant_condition = models.FieldCondition(
        key="catalog_id", match=models.MatchValue(value=f"tenant:{tenant_id}"),
    )
    query_filter = models.Filter(must=[tenant_condition])
    if createdDate_greater_than is not None or createdDate_less_than is not None:
        # Include both calendar dates, using the +00:00 offset of stored dates.
        start = f"{createdDate_greater_than}T00:00:00Z" if createdDate_greater_than else None
        end = (
            f"{date.fromisoformat(createdDate_less_than) + timedelta(days=1)}T00:00:00Z"
            if createdDate_less_than else None
        )
        #for Undated summaries, they remain eligible for search,
        query_filter = models.Filter(must=[tenant_condition], should=[
            models.FieldCondition(
                key="createdDateTime",
                range=models.DatetimeRange(gte=start, lt=end),
            ),
            models.IsEmptyCondition(is_empty=models.PayloadField(key="createdDateTime")),
        ])

    with RETRIEVAL_DURATION.labels(
        retrieval_type="summaries",
    ).time():
        candidate_limit = max(50, limit * 2)
        dense_query = embed_texts([question], DENSE_MODEL, "query")[0]
        sparse_query = embed_texts([question], SPARSE_MODEL, "query")[0]

        result = qdrant_client.query_points(
            collection_name=SUMMARIES_COLLECTION,
            prefetch=[
                models.Prefetch(
                    query=dense_query,
                    using=DENSE_VECTOR,
                    limit=candidate_limit,
                    filter=query_filter,
                ),
                models.Prefetch(
                    query=models.SparseVector(
                        indices=sparse_query["indices"],
                        values=sparse_query["values"],
                    ),
                    using=SPARSE_VECTOR,
                    limit=candidate_limit,
                    filter=query_filter,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            query_filter=query_filter,
            limit=candidate_limit,
            with_payload=True,
        )

        return rerank_by_recency(
            result.points,
            reference_ts=time(),
            max_bonus=0.05,
            half_life_days=90,
        )[:limit]
