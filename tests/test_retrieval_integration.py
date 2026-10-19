import unittest
from types import SimpleNamespace
from unittest.mock import patch

from qdrant_client import models

from api import QueryRequest, query
from retrieval.semantic_search import search_passages, search_summaries
from workflows.rag_graph import retrieve


def point(point_id, score, **payload):
    return SimpleNamespace(id=point_id, score=score, payload=payload)


class FakeQdrant:
    def __init__(self):
        self.calls = []

    def query_points(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(points=[])


class SemanticSearchTests(unittest.TestCase):
    @patch("retrieval.semantic_search.embed_texts")
    def test_passage_and_summary_search_use_their_own_aliases(self, embed_texts):
        embed_texts.side_effect = (
            lambda _texts, model, _input_type: [[0.1, 0.2]]
            if model == "bge-m3"
            else [{"indices": [1], "values": [0.5]}]
        )
        qdrant = FakeQdrant()

        search_passages("question", 3, qdrant_client=qdrant)
        search_summaries("question", 2, qdrant_client=qdrant)

        self.assertEqual(
            qdrant.calls[0]["collection_name"],
            "passages_embeddings_live",
        )
        self.assertEqual(
            qdrant.calls[1]["collection_name"],
            "summaries_embeddings_live",
        )
        for call in qdrant.calls:
            self.assertIsInstance(call["query"], models.FusionQuery)
            self.assertEqual(
                [prefetch.using for prefetch in call["prefetch"]],
                ["dense", "sparse"],
            )
            self.assertEqual(call["prefetch"][0].query, [0.1, 0.2])
            self.assertIsInstance(
                call["prefetch"][1].query,
                models.SparseVector,
            )
            self.assertTrue(
                all(
                    prefetch.limit >= call["limit"]
                    for prefetch in call["prefetch"]
                )
            )


class RetrievalWorkflowTests(unittest.TestCase):
    @patch("workflows.rag_graph.retrieve_graph")
    @patch("workflows.rag_graph.search_summaries")
    @patch("workflows.rag_graph.search_passages")
    def test_retrieve_combines_all_representations(
        self,
        search_passages,
        search_summaries,
        retrieve_graph,
    ):
        search_passages.return_value = [
            point(
                "passage-1",
                0.9,
                chunk_id="chunk-1",
                document_id="document-1",
                content="Text",
            )
        ]
        search_summaries.return_value = [
            point("summary-1", 0.8, node_id="summary-node", summary_text="Summary")
        ]
        retrieve_graph.return_value = {
            "results": [
                {
                    "result_id": "point-1",
                    "rank": 1,
                    "claim": "Alice works with NEXUS.",
                    "evidence": ["Alice is a NEXUS researcher."],
                    "source_chunk_id": "chunk-1",
                    "source_content": "Text",
                    "graph_expansion": {
                        "entities": [{"name": "Alice"}],
                        "relations": [],
                    },
                }
            ]
        }

        result = retrieve(
            {
                "question": "question",
                "limit": 3,
                "retrievals": ["documents", "summaries", "graph"],
            }
        )

        self.assertEqual(result["documents"][0]["chunk_id"], "chunk-1")
        self.assertEqual(result["documents"][0]["id"], "document-1")
        self.assertEqual(result["summaries"][0]["node_id"], "summary-node")
        self.assertEqual(result["summaries"][0]["id"], "summary-node")
        self.assertEqual(
            result["graph_context"]["results"][0]["graph_expansion"]["entities"][0]["name"],
            "Alice",
        )

    @patch("workflows.rag_graph.retrieve_graph")
    @patch("workflows.rag_graph.search_summaries")
    @patch("workflows.rag_graph.search_passages")
    def test_retrieve_runs_only_requested_representations(
        self,
        search_passages,
        search_summaries,
        retrieve_graph,
    ):
        search_summaries.return_value = [
            point("summary-1", 0.8, node_id="summary-node", summary_text="Summary")
        ]

        result = retrieve(
            {
                "question": "question",
                "limit": 3,
                "retrievals": ["summaries"],
            }
        )

        search_passages.assert_not_called()
        search_summaries.assert_called_once_with("question", 3)
        retrieve_graph.assert_not_called()
        self.assertEqual(result["documents"], [])
        self.assertEqual(result["summaries"][0]["id"], "summary-node")
        self.assertEqual(result["graph_context"], {"results": []})


class ApiIntegrationTests(unittest.TestCase):
    @patch("api.graph.invoke")
    def test_query_returns_all_representations(self, invoke):
        invoke.return_value = {
            "documents": [{"chunk_id": "chunk-1"}],
            "summaries": [{"node_id": "summary-1"}],
            "graph_context": {"results": []},
        }

        result = query(QueryRequest(question="question", limit=2))

        self.assertEqual(result["documents"][0]["chunk_id"], "chunk-1")
        self.assertEqual(result["summaries"][0]["node_id"], "summary-1")
        self.assertIn("graph_context", result)
        self.assertEqual(
            invoke.call_args.args[0]["retrievals"],
            ["documents", "summaries", "graph"],
        )

    @patch("api.graph.invoke")
    def test_query_passes_selected_retrievals_to_workflow(self, invoke):
        invoke.return_value = {
            "documents": [],
            "summaries": [{"node_id": "summary-1"}],
            "graph_context": {"results": []},
        }

        query(
            QueryRequest(
                question="question",
                limit=2,
                retrievals=["summaries"],
            )
        )

        self.assertEqual(
            invoke.call_args.args[0]["retrievals"],
            ["summaries"],
        )


if __name__ == "__main__":
    unittest.main()
