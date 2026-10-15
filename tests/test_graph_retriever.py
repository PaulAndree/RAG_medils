import unittest
from types import SimpleNamespace

from qdrant_client import models

from retrieval.graph_retriever import retrieve_graph


class FakeQdrant:
    def __init__(self, points):
        self.points = points
        self.call = None

    def query_points(self, **kwargs):
        self.call = kwargs
        return SimpleNamespace(points=self.points)


class FakeSession:
    def __init__(self):
        self.call = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def run(self, query, parameters):
        self.call = (query, parameters)
        return [{"entity": "Alice"}]


class FakeDriver:
    def __init__(self):
        self.session_instance = FakeSession()

    def session(self, *, database):
        self.database = database
        return self.session_instance


class GraphRetrieverTests(unittest.TestCase):
    def setUp(self):
        self.point = SimpleNamespace(
            id="point-1",
            score=0.91,
            payload={"source_chunk_id": "chunk-1"},
        )
        self.qdrant = FakeQdrant([self.point])
        self.driver = FakeDriver()

    def test_runs_hybrid_text_query_and_maps_payload_chunk_id(self):
        result = retrieve_graph(
            query="Who works on the project?",
            qdrant_client=self.qdrant,
            driver=self.driver,
        )

        self.assertIsInstance(self.qdrant.call["query"], models.FusionQuery)
        self.assertEqual(
            [prefetch.using for prefetch in self.qdrant.call["prefetch"]],
            ["dense", "bm25"],
        )
        self.assertEqual(
            [prefetch.query.model for prefetch in self.qdrant.call["prefetch"]],
            ["BAAI/bge-small-en-v1.5", "Qdrant/bm25"],
        )
        self.assertEqual(result["matches"][0]["chunk_id"], "chunk-1")
        self.assertEqual(result["records"], [{"entity": "Alice"}])

    def test_accepts_existing_embedding_and_custom_cypher(self):
        result = retrieve_graph(
            embedding=[0.1, 0.2],
            cypher_query="RETURN $chunk_ids AS ids",
            cypher_parameters={"extra": True},
            qdrant_client=self.qdrant,
            driver=self.driver,
        )

        self.assertEqual(self.qdrant.call["query"], [0.1, 0.2])
        self.assertEqual(self.qdrant.call["using"], "dense")
        self.assertNotIn("prefetch", self.qdrant.call)
        query, parameters = self.driver.session_instance.call
        self.assertEqual(query, "RETURN $chunk_ids AS ids")
        self.assertEqual(parameters["chunk_ids"], ["chunk-1"])
        self.assertTrue(parameters["extra"])
        self.assertEqual(result["matches"][0]["point_id"], "point-1")

    def test_deduplicates_arguments_from_the_same_chunk(self):
        self.qdrant.points = [
            self.point,
            SimpleNamespace(
                id="point-2",
                score=0.85,
                payload={"source_chunk_id": "chunk-1"},
            ),
            SimpleNamespace(
                id="point-3",
                score=0.80,
                payload={"source_chunk_id": "chunk-2"},
            ),
        ]

        result = retrieve_graph(
            query="question",
            qdrant_client=self.qdrant,
            driver=self.driver,
        )

        self.assertEqual(
            [match["chunk_id"] for match in result["matches"]],
            ["chunk-1", "chunk-2"],
        )
        self.assertEqual(
            result["matches"][0]["point_ids"],
            ["point-1", "point-2"],
        )
        _query, parameters = self.driver.session_instance.call
        self.assertEqual(parameters["chunk_ids"], ["chunk-1", "chunk-2"])

    def test_requires_exactly_one_query_input(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            retrieve_graph(
                qdrant_client=self.qdrant,
                driver=self.driver,
            )

        with self.assertRaisesRegex(ValueError, "exactly one"):
            retrieve_graph(
                query="question",
                embedding=[0.1],
                qdrant_client=self.qdrant,
                driver=self.driver,
            )

    def test_rejects_points_without_chunk_id(self):
        self.qdrant.points = [
            SimpleNamespace(id="bad-point", score=0.5, payload={})
        ]

        with self.assertRaisesRegex(ValueError, "payload source_chunk_id"):
            retrieve_graph(
                query="question",
                qdrant_client=self.qdrant,
                driver=self.driver,
            )


if __name__ == "__main__":
    unittest.main()
