import os
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from qdrant_client import QdrantClient, models

from metrics import ProcessMetricSample, push_process_metrics
from stores.database_postgres import get_indexable_chunks

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

ACTIVE_ALIAS = "passages_embeddings_live"
COLLECTION_PREFIX = "passages_embeddings"
DENSE_VECTOR = "dense"
SPARSE_VECTOR = "bm25"
DENSE_MODEL = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL = "Qdrant/bm25"

client = QdrantClient(url=QDRANT_URL)


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


def index_chunks(collection_name, chunks):
    ids = []
    vectors = []
    payloads = []

    for chunk in chunks:
        embedding_text = chunk["content"]

        if chunk["chunk_title"]:
            embedding_text = (
                f"{chunk['chunk_title']}\n\n"
                f"{chunk['content']}"
            )

        ids.append(chunk["chunk_id"])

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
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "doc_name": chunk["doc_name"],
                "document_title": chunk["document_title"],
                "title": (
                    chunk["chunk_title"]
                    or chunk["document_title"]
                ),
                "content": chunk["content"],
                "chunk_index": chunk["chunk_index"],
                "token_count": chunk["token_count"],
                "language": chunk["language"],
                "document_version": chunk["document_version"],
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
        f"Indexed {len(chunks)} chunks into {collection_name}"
    )


def validate_collection(collection_name, chunks):
    indexed_count = client.count(
        collection_name=collection_name,
        exact=True,
    ).count

    if indexed_count != len(chunks):
        raise RuntimeError(
            f"Validation failed for {collection_name}: "
            f"expected {len(chunks)} points, "
            f"found {indexed_count}"
        )

    smoke_result = client.query_points(
        collection_name=collection_name,
        prefetch=[
            models.Prefetch(
                query=models.Document(
                    text=chunks[0]["content"],
                    model=DENSE_MODEL,
                ),
                using=DENSE_VECTOR,
                limit=10,
            ),
            models.Prefetch(
                query=models.Document(
                    text=chunks[0]["content"],
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
    #deletes only the alias binding. It does not delete the collection that the alias previously referenced.
    if previous_collection is not None:
        operations.append(
            models.DeleteAliasOperation(
                delete_alias=models.DeleteAlias(alias_name=ACTIVE_ALIAS)
            )
        )
    #The following operation recreates the alias pointing to the new collection:
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
    chunks = get_indexable_chunks()

    if not chunks:
        raise RuntimeError(
            "No PostgreSQL chunks were found; "
            "refusing to activate an empty index"
        )

    new_collection = build_collection_name()
    previous_collection = get_alias_target()

    print(f"Building new collection {new_collection}")

    if previous_collection is not None:
        print(f"Current alias target is {previous_collection}")

    try:
        create_collection(new_collection)
        index_chunks(new_collection, chunks)
        validate_collection(new_collection, chunks)
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
        client.delete_collection(previous_collection)
        print(f"Deleted previous collection {previous_collection}")

    try:
        push_process_metrics(
            process="indexing",
            samples=[ProcessMetricSample(
                representation="passages",
                document_count=len({
                    chunk["document_id"]
                    for chunk in chunks
                }),
                item_counts={"chunks": len(chunks)},
                duration_seconds=perf_counter() - started,
            )],
            pushgateway_url=PUSHGATEWAY_URL,
            job="indexing_passages",
        )
    except Exception as exc:
        print(f"[indexing] warning: could not publish metrics: {exc}")



if __name__ == "__main__":
    main()
