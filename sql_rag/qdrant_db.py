from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


client = QdrantClient(
    url="http://qdrant:6333"
)

COLLECTION = "documents"


def create_collection():
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=4,
                distance=Distance.COSINE,
            ),
        )

def add_documents():

    client.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=1,
                vector=[0.9, 0.1, 0.1, 0.1],
                payload={
                    "title": "PostgreSQL",
                    "document_id": 1,
                },
            ),

            PointStruct(
                id=2,
                vector=[0.1, 0.9, 0.1, 0.1],
                payload={
                    "title": "Qdrant",
                    "document_id": 2,
                },
            ),

            PointStruct(
                id=3,
                vector=[0.1, 0.8, 0.2, 0.1],
                payload={
                    "title": "Vector databases",
                    "document_id": 3,
                },
            ),
        ],
    )

def search():

    results = client.query_points(
        collection_name=COLLECTION,
        query=[0.1, 0.85, 0.1, 0.1],
        limit=2,
    )

    for point in results.points:
        print(
            point.id,
            point.score,
            point.payload,
        )

create_collection()
add_documents()
search()