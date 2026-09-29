from qdrant_client import QdrantClient, models

from sql_rag.database_postgres import get_connection, get_documents
from metrics import INDEX_DURATION, RETRIEVAL_DURATION
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

COLLECTION = "documents_embeddings"

MODEL = "BAAI/bge-small-en-v1.5"


client = QdrantClient(
    url=QDRANT_URL
)


def create_collection():
    if not client.collection_exists(COLLECTION):

        vector_size = client.get_embedding_size(MODEL)

        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

        print(f"Collection created with vector size: {vector_size}")

@INDEX_DURATION.time()
def index_documents():

    documents = get_documents()

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
            }
        )

    client.upload_collection(
        collection_name=COLLECTION,
        vectors=vectors,
        payload=payloads,
        ids=ids,
    )

    print(f"Indexed {len(documents)} documents")

@RETRIEVAL_DURATION.time()
def search_documents(question):

    result = client.query_points(
        collection_name=COLLECTION,

        query=models.Document(
            text=question,
            model=MODEL,
        ),

        limit=3,
    )

    return result.points

def get_document(document_id):

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT id, title, content
        FROM documents
        WHERE id = %s
        """,
        (document_id,),
    )

    document = cursor.fetchone()

    conn.close()

    return document


if __name__ == "__main__":

    create_collection()

    index_documents()

    question = "Which database can I use for vectors?"

    results = search_documents(question)

    print(f"\nQuestion: {question}\n")

    for result in results:

        document_id = result.payload["document_id"]

        document = get_document(document_id)

        print("Score:", result.score)
        print("Document:", document)
        print()