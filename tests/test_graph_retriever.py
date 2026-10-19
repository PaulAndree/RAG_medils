import unittest
from types import SimpleNamespace
from unittest.mock import patch

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
        return [
            {
                "source_chunk_id": "chunk-1",
                "chunk": {"id": "chunk-1", "content": "Source content"},
                "entity": {"id": "entity-1", "name": "Alice", "type": "PERSON"},
                "relation": {
                    "id": "relation-1",
                    "relation": "WORKS_WITH",
                    "evidence": "Alice works with NEXUS.",
                },
                "connected_entity": {
                    "id": "entity-2",
                    "name": "NEXUS",
                    "type": "ORGANIZATION",
                },
            }
        ]


class FakeDriver:
    def __init__(self):
        self.session_instance = FakeSession()

    def session(self, *, database):
        self.database = database
        return self.session_instance


class GraphRetrieverTests(unittest.TestCase):
    def setUp(self):
        embedding_patcher = patch("retrieval.graph_retriever.embed_texts")
        self.embed_texts = embedding_patcher.start()
        self.addCleanup(embedding_patcher.stop)
        self.embed_texts.side_effect = (
            lambda _texts, model, _input_type: [[0.1, 0.2]]
            if model == "bge-m3"
            else [{"indices": [1], "values": [0.5]}]
        )
        self.point = SimpleNamespace(
            id="point-1",
            score=0.91,
            payload={
                "argument_id": "argument-1",
                "claim": "Alice works with NEXUS.",
                "evidence": ["Alice is part of the NEXUS project."],
                "source_chunk_id": "chunk-1",
                "source_content": "Source content",
            },
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
            ["dense", "sparse"],
        )
        self.assertEqual(self.qdrant.call["prefetch"][0].query, [0.1, 0.2])
        self.assertIsInstance(
            self.qdrant.call["prefetch"][1].query,
            models.SparseVector,
        )
        graph_result = result["results"][0]
        self.assertEqual(graph_result["result_id"], "point-1")
        self.assertEqual(graph_result["argument_id"], "argument-1")
        self.assertEqual(graph_result["claim"], "Alice works with NEXUS.")
        self.assertEqual(
            graph_result["evidence"],
            ["Alice is part of the NEXUS project."],
        )
        self.assertEqual(graph_result["source_chunk_id"], "chunk-1")
        self.assertEqual(
            graph_result["graph_expansion"]["entities"][0]["name"],
            "Alice",
        )
        self.assertEqual(
            graph_result["graph_expansion"]["relations"][0]["target"]["name"],
            "NEXUS",
        )

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
        self.assertEqual(result["results"][0]["result_id"], "point-1")
        self.assertEqual(parameters["results"][0]["claim"], "Alice works with NEXUS.")

    def test_preserves_argument_ranks_when_points_share_a_chunk(self):
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
            [item["result_id"] for item in result["results"]],
            ["point-1", "point-2", "point-3"],
        )
        self.assertEqual([item["rank"] for item in result["results"]], [1, 2, 3])
        _query, parameters = self.driver.session_instance.call
        self.assertEqual(parameters["chunk_ids"], ["chunk-1", "chunk-2"])

    def test_keeps_claim_and_evidence_when_graph_expansion_is_empty(self):
        self.driver.session_instance.run = lambda _query, _parameters: []

        result = retrieve_graph(
            query="question",
            qdrant_client=self.qdrant,
            driver=self.driver,
        )

        graph_result = result["results"][0]
        self.assertEqual(graph_result["claim"], "Alice works with NEXUS.")
        self.assertEqual(
            graph_result["graph_expansion"],
            {"entities": [], "relations": []},
        )

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
