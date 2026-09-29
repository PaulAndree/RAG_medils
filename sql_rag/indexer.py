import os
from datetime import datetime, timezone
from uuid import uuid4

from qdrant_client import QdrantClient, models

from metrics import INDEX_DURATION
from sql_rag.database_postgres import get_documents

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

ACTIVE_ALIAS = os.getenv(
    "QDRANT_ALIAS",
    "documents_embeddings_live",
)
COLLECTION_PREFIX = os.getenv(
    "QDRANT_COLLECTION_PREFIX",
    "documents_embeddings",
)
MODEL = "BAAI/bge-small-en-v1.5"

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
    vector_size = client.get_embedding_size(MODEL)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_size,
            distance=models.Distance.COSINE,
        ),
    )

    print(
        f"Created collection {collection_name} "
        f"with vector size {vector_size}"
    )


@INDEX_DURATION.time()
def index_documents(collection_name, documents):
    ids = []
    vectors = []
    payloads = []

    for document_id, title, content in documents:
        ids.append(document_id)
        vectors.append(
            models.Document(
                text=content,
                model=MODEL,
            )
        )
        payloads.append(
            {
                "document_id": document_id,
                "title": title,
                "content": content,
            }
        )

    client.upload_collection(
        collection_name=collection_name,
        vectors=vectors,
        payload=payloads,
        ids=ids,
        wait=True,
    )

    print(f"Indexed {len(documents)} documents into {collection_name}")


def validate_collection(collection_name, documents):
    indexed_count = client.count(
        collection_name=collection_name,
        exact=True,
    ).count

    if indexed_count != len(documents):
        raise RuntimeError(
            f"Validation failed for {collection_name}: "
            f"expected {len(documents)} points, found {indexed_count}"
        )

    smoke_query = documents[0][2]
    smoke_result = client.query_points(
        collection_name=collection_name,
        query=models.Document(text=smoke_query, model=MODEL),
        limit=1,
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
    documents = get_documents()

    if not documents:
        raise RuntimeError(
            "No PostgreSQL documents were found; "
            "refusing to activate an empty index"
        )

    new_collection = build_collection_name()
    previous_collection = get_alias_target()

    print(f"Building new collection {new_collection}")
    if previous_collection is not None:
        print(f"Current alias target is {previous_collection}")

    try:
        create_collection(new_collection)
        index_documents(new_collection, documents)
        validate_collection(new_collection, documents)
        activate_collection(new_collection, previous_collection)
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


if __name__ == "__main__":
    main()
