from qdrant_client import QdrantClient, models

from stores.database_postgres import get_connection
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
        with_payload=True,
    )

    return result.points

def get_document(document_id):
    with get_connection() as conn:
        document = conn.execute(
            """
            SELECT
                d.id,
                d.name AS doc_name,
                d.title,
                string_agg(
                    c.content,
                    E'\n\n'
                    ORDER BY c.chunk_index
                ) AS content
            FROM documents AS d
            LEFT JOIN chunks AS c
              ON c.document_id = d.id
             AND c.document_version = d.version
            WHERE d.id = %s
            GROUP BY d.id, d.name, d.title
            """,
            (document_id,),
        ).fetchone()

    return document
