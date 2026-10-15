import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import NAMESPACE_URL, uuid4, uuid5

from qdrant_client import QdrantClient, models

from metrics import ProcessMetricSample, push_process_metrics
from stores.database_postgres import get_indexable_summaries

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

ACTIVE_ALIAS = "summaries_embeddings_live"
COLLECTION_PREFIX = "summaries_embeddings"
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "bm25"
DENSE_MODEL = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL = "Qdrant/bm25"

client = QdrantClient(url=QDRANT_URL)
POINT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/qdrant/summaries",
)


def build_collection_name():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = uuid4().hex[:8]
    return f"{COLLECTION_PREFIX}_{timestamp}_{suffix}"


def get_alias_target():
    for alias in client.get_aliases().aliases:
        if alias.alias_name == ACTIVE_ALIAS:
            return alias.collection_name

    return None


def create_collection(collection_name):
    vector_size = client.get_embedding_size(DENSE_MODEL)

    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            DENSE_VECTOR: models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        },
        sparse_vectors_config={
            SPARSE_VECTOR: models.SparseVectorParams(
                modifier=models.Modifier.IDF,
            ),
        },
    )

    print(
        f"Created collection {collection_name} "
        f"with vector size {vector_size}"
    )


def index_summaries(collection_name, summaries):
    ids = []
    vectors = []
    payloads = []

    for each_summary in summaries:
        embedding_text = each_summary["summary_text"]

        ids.append(str(uuid5(
            POINT_NAMESPACE,
            each_summary["node_id"],
        )))

        vectors.append({
            DENSE_VECTOR: models.Document(
                text=embedding_text,
                model=DENSE_MODEL,
            ),
            SPARSE_VECTOR: models.Document(
                text=embedding_text,
                model=SPARSE_MODEL,
            ),
        })

        payloads.append(
            {
                "node_id": each_summary["node_id"],
                "summary_text": each_summary["summary_text"],
                "level": each_summary["level"],
                "scope": each_summary["scope"],
                "document_id": each_summary["document_id"],
                "catalog_id": each_summary["catalog_id"],
                "source_node_ids": each_summary["source_node_ids"],
                "source_chunk_ids": each_summary["source_chunk_ids"],
                "source_document_ids": each_summary["source_document_ids"],
            }
        )

    client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=ids,
        wait=True,
    )

    print(f"Indexed {len(summaries)} summaries into {collection_name}")


def validate_collection(collection_name, summary_node):
    indexed_count = client.count(
        collection_name=collection_name,
        exact=True,
    ).count

    if indexed_count != len(summary_node):
        raise RuntimeError(
            f"Validation failed for {collection_name}: "
            f"expected {len(summary_node)} points, "
            f"found {indexed_count}"
        )

    smoke_result = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=models.Document(
                    text=summary_node[0]["summary_text"],
                    model=DENSE_MODEL,
                ),
                using=DENSE_VECTOR,
                limit=10,
            ),
            models.Prefetch(
                query=models.Document(
                    text=summary_node[0]["summary_text"],
                    model=SPARSE_MODEL,
                ),
                using=SPARSE_VECTOR,
                limit=10,
            ),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=1,
        with_payload=True,
    )

    if not smoke_result.points:
        raise RuntimeError(
            f"Validation failed for {collection_name}: "
            "smoke query returned no results"
        )

    print(f"Validated collection {collection_name}")


def activate_collection(collection_name, previous_collection):
    operations = []

    if previous_collection is not None:
        operations.append(
            models.DeleteAliasOperation(
                delete_alias=models.DeleteAlias(alias_name=ACTIVE_ALIAS)
            )
        )

    operations.append(
        models.CreateAliasOperation(
            create_alias=models.CreateAlias(
                collection_name=collection_name,
                alias_name=ACTIVE_ALIAS,
            )
        )
    )

    client.update_collection_aliases(
        change_aliases_operations=operations,
    )

    if get_alias_target() != collection_name:
        raise RuntimeError(
            f"Alias {ACTIVE_ALIAS} was not activated for {collection_name}"
        )

    print(f"Alias {ACTIVE_ALIAS} now points to {collection_name}")


def main():
    started = perf_counter()
    summary_node = get_indexable_summaries()

    if not summary_node:
        raise RuntimeError(
            "No PostgreSQL summaries were found; "
            "refusing to activate an empty index"
        )

    new_collection = build_collection_name()
    previous_collection = get_alias_target()

    print(f"Building new collection {new_collection}")

    if previous_collection is not None:
        print(f"Current alias target is {previous_collection}")

    try:
        create_collection(new_collection)
        index_summaries(new_collection, summary_node)
        validate_collection(new_collection, summary_node)
        activate_collection(
            new_collection,
            previous_collection,
        )
    except Exception:
        print(
            f"Indexing failed; collection {new_collection} "
            "was retained for inspection"
        )
        raise

    if previous_collection is not None:
        print(
            f"Previous collection {previous_collection} "
            "was retained for rollback"
        )

    source_document_ids = set()
    for summary in summary_node:
        if summary["document_id"] is not None:
            source_document_ids.add(str(summary["document_id"]))
        source_document_ids.update(summary["source_document_ids"])

    try:
        push_process_metrics(
            process="indexing",
            samples=[ProcessMetricSample(
                representation="summaries",
                document_count=len(source_document_ids),
                item_counts={"summaries": len(summary_node)},
                duration_seconds=perf_counter() - started,
            )],
            pushgateway_url=PUSHGATEWAY_URL,
            job="indexing_summaries",
        )
    except Exception as exc:
        print(f"[indexing] warning: could not publish metrics: {exc}")


if __name__ == "__main__":
    main()
