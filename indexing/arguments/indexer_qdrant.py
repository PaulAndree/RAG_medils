import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import NAMESPACE_URL, uuid4, uuid5

from qdrant_client import QdrantClient, models

from indexing.embedding_api import (
    DENSE_MODEL,
    DENSE_VECTOR_SIZE,
    SPARSE_MODEL,
    embed_texts,
)
from metrics import ProcessMetricSample, push_process_metrics
from stores.database_postgres import get_indexable_arguments

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

ACTIVE_ALIAS = "arguments_embeddings_live"
COLLECTION_PREFIX = "arguments_embeddings"
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "sparse"

client = QdrantClient(url=QDRANT_URL)
POINT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/qdrant/arguments",
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
    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            DENSE_VECTOR: models.VectorParams(
                size=DENSE_VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        },
        sparse_vectors_config={
            SPARSE_VECTOR: models.SparseVectorParams(),
        },
    )

    print(
        f"Created collection {collection_name} "
        f"with vector size {DENSE_VECTOR_SIZE}"
    )


def embedding_text(argument):
    text = argument["claim"]
    if argument["evidence"]:
        text += "\n\nEvidence:\n" + "\n".join(argument["evidence"])
    return text


def index_arguments(collection_name, arguments):
    ids = []
    vectors = []
    payloads = []
    texts = [embedding_text(argument) for argument in arguments]
    dense_vectors = embed_texts(texts, DENSE_MODEL)
    sparse_vectors = embed_texts(texts, SPARSE_MODEL)

    for argument, dense_vector, sparse_vector in zip(
        arguments,
        dense_vectors,
        sparse_vectors,
        strict=True,
    ):
        ids.append(str(uuid5(
            POINT_NAMESPACE,
            argument["argument_id"],
        )))

        vectors.append({
            DENSE_VECTOR: dense_vector,
            SPARSE_VECTOR: models.SparseVector(
                indices=sparse_vector["indices"],
                values=sparse_vector["values"],
            ),
        })

        payloads.append(
            {
                "argument_id": argument["argument_id"],
                "claim": argument["claim"],
                "evidence": argument["evidence"],
                "source_chunk_id": argument["source_chunk_id"],
                "document_id": argument["document_id"],
                "doc_name": argument["doc_name"],
                "document_title": argument["document_title"],
                "chunk_title": argument["chunk_title"],
                "source_content": argument["source_content"],
                "chunk_index": argument["chunk_index"],
                "token_count": argument["token_count"],
                "language": argument["language"],
                "document_version": argument["document_version"],
            }
        )

    client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=ids,
        wait=True,
    )

    print(
        f"Indexed {len(arguments)} arguments into {collection_name}"
    )


def validate_collection(collection_name, arguments):
    indexed_count = client.count(
        collection_name=collection_name,
        exact=True,
    ).count

    if indexed_count != len(arguments):
        raise RuntimeError(
            f"Validation failed for {collection_name}: "
            f"expected {len(arguments)} points, "
            f"found {indexed_count}"
        )

    text = embedding_text(arguments[0])
    dense_query = embed_texts([text], DENSE_MODEL, "query")[0]
    sparse_query = embed_texts([text], SPARSE_MODEL, "query")[0]

    smoke_result = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=dense_query,
                using=DENSE_VECTOR,
                limit=10,
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_query["indices"],
                    values=sparse_query["values"],
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
    arguments = get_indexable_arguments()

    if not arguments:
        raise RuntimeError(
            "No PostgreSQL arguments were found; "
            "refusing to activate an empty index"
        )

    new_collection = build_collection_name()
    previous_collection = get_alias_target()

    print(f"Building new collection {new_collection}")

    if previous_collection is not None:
        print(f"Current alias target is {previous_collection}")

    try:
        create_collection(new_collection)
        index_arguments(new_collection, arguments)
        validate_collection(new_collection, arguments)
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

    try:
        push_process_metrics(
            process="indexing",
            samples=[ProcessMetricSample(
                representation="arguments",
                document_count=len({
                    argument["document_id"]
                    for argument in arguments
                }),
                item_counts={"arguments": len(arguments)},
                duration_seconds=perf_counter() - started,
            )],
            pushgateway_url=PUSHGATEWAY_URL,
            job="indexing_arguments",
        )
    except Exception as exc:
        print(f"[indexing] warning: could not publish metrics: {exc}")


if __name__ == "__main__":
    main()
