from qdrant_client import QdrantClient, models

from sql_rag.database_postgres import get_connection, get_documents
from metrics import INDEX_DURATION, RETRIEVAL_DURATION
import os

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")

ACTIVE_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "documents_embeddings_live",
)

MODEL = "BAAI/bge-small-en-v1.5"


client = QdrantClient(
    url=QDRANT_URL
)


@RETRIEVAL_DURATION.time()
def search_documents(question, limit):

    result = client.query_points(
        collection_name=ACTIVE_COLLECTION,

        query=models.Document(
            text=question,
            model=MODEL,
        ),

        limit=limit,
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

