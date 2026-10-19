import os

import requests


EMBEDDING_URL = os.getenv(
    "EMBEDDING_URL",
    "http://127.0.0.1:8089/embed",
)
DENSE_MODEL = "bge-m3"
SPARSE_MODEL = "milco-650m"
#SPARSE_MODEL = "bm25"
DENSE_VECTOR_SIZE = 1024


def embed_texts(texts, model, input_type="passage"):
    response = requests.post(
        EMBEDDING_URL,
        json={
            "texts": texts,
            "model": model,
            "input_type": input_type,
            "normalize": True,
        },
        timeout=(10, 600),
    )
    response.raise_for_status()
    result = response.json()
    key = "embeddings" if result.get("kind") == "dense" else "sparse"
    vectors = result.get(key)

    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise RuntimeError(
            f"Embedding API returned invalid {result.get('kind')} vectors"
        )

    return vectors
