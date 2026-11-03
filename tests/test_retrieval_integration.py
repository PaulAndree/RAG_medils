import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from langchain_core.messages import HumanMessage
from qdrant_client import models

from RAG_medils.retrieval_and_generation import api
from RAG_medils.retrieval_and_generation.retrieval.semantic_search import search_summaries
from RAG_medils.retrieval_and_generation.workflows import rag_graph


def point(point_id, score, **payload):
    return SimpleNamespace(id=point_id, score=score, payload=payload)


class FakeQdrant:
    def __init__(self):
        self.calls = []

    def query_points(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(points=[])


class SemanticSearchTests(unittest.TestCase):
    @patch("RAG_medils.retrieval_and_generation.retrieval.semantic_search.embed_texts")
    def test_summary_search_uses_hybrid_retrieval_on_the_summary_alias(
        self,
        embed_texts,
    ):
        embed_texts.side_effect = (
            lambda _texts, model, _input_type: [[0.1, 0.2]]
            if model == "bge-m3"
            else [{"indices": [1], "values": [0.5]}]
        )
        qdrant = FakeQdrant()

        search_summaries("question", 2, tenant_id="a", qdrant_client=qdrant)

        self.assertEqual(
            qdrant.calls[0]["collection_name"],
            "summaries_embeddings_live",
        )
        call = qdrant.calls[0]
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


class RetrievalWorkflowTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(rag_graph, "analyze_query", new_callable=AsyncMock)
    @patch.object(rag_graph, "search_summaries")
    async def test_retrieve_returns_only_serialized_summaries(self, search_summaries, analyze_query):
        analyze_query.return_value = {
            "query": "question",
            "createdDate_greater_than": None,
            "createdDate_less_than": None,
        }
        search_summaries.return_value = [
            point("summary-1", 0.8, node_id="summary-node", summary_text="Summary")
        ]

        result = await rag_graph.retrieve(
            {
                "messages": [HumanMessage(content="question")],
                "limit": 3,
                "summaries": [],
                "tenant_id": "a",
            }
        )

        search_summaries.assert_called_once_with(
            "question", 3, tenant_id="a",
            createdDate_greater_than=None, createdDate_less_than=None,
        )
        self.assertEqual(set(result), {"summaries"})
        self.assertEqual(result["summaries"][0]["node_id"], "summary-node")
        self.assertEqual(result["summaries"][0]["id"], "summary-node")


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Exercise retrieval independently of login/database setup.
        api.app.dependency_overrides[api.authenticate] = lambda: {"user_id": "user-a", "tenant_id": "a"}
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    @patch.object(api, "analyze_query", new_callable=AsyncMock)
    @patch.object(rag_graph, "generate_answer", new_callable=AsyncMock)
    @patch.object(api, "search_summaries")
    def test_retrieve_returns_ranked_qdrant_points(self, search, generate, analyze):
        analyze.return_value = {
            "query": "Rewritten query",
            "createdDate_greater_than": "2026-10-01",
            "createdDate_less_than": "2026-10-30",
        }
        points = [
            models.ScoredPoint(
                id=42, version=1, score=0.9,
                payload={"node_id": "node-1", "document_title": "Paper", "catalog_id": "tenant:a"},
            ),
            models.ScoredPoint(id="3a79f51b-9544-4eee-a9df-112327874001", version=2, score=0.5, payload=None),
        ]
        search.return_value = points
        response = self.client.post('/retrieve', json={"query": "My exact query", "limit": 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [point.model_dump(mode="json") for point in points])
        search.assert_called_once_with(
            "Rewritten query", 50, tenant_id="a",
            createdDate_greater_than="2026-10-01",
            createdDate_less_than="2026-10-30",
        )
        generate.assert_not_awaited()
        analyze.assert_awaited_once_with("My exact query")

    @patch.object(api, "analyze_query", new_callable=AsyncMock)
    @patch.object(api, "search_summaries", return_value=[])
    def test_retrieve_defaults_limit_and_handles_no_matches(self, search, analyze):
        analyze.return_value = {
            "query": "question",
            "createdDate_greater_than": None,
            "createdDate_less_than": None,
        }
        response = self.client.post('/retrieve', json={"query": "question"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        search.assert_called_once_with(
            "question", 3, tenant_id="a",
            createdDate_greater_than=None, createdDate_less_than=None,
        )
        analyze.assert_awaited_once_with("question")

    @patch.object(api, "analyze_query", new_callable=AsyncMock)
    @patch.object(api, "search_summaries")
    def test_retrieve_rejects_invalid_input_before_search(self, search, analyze):
        for body in (
            {}, {"query": ""}, {"query": " \n\t"}, {"query": None},
            {"query": "question", "limit": 0},
            {"query": "question", "limit": -1},
            {"query": "question", "limit": 1.5},
        ):
            with self.subTest(body=body):
                self.assertEqual(self.client.post('/retrieve', json=body).status_code, 422)
        search.assert_not_called()
        analyze.assert_not_awaited()

    @patch.object(api, "analyze_query", new_callable=AsyncMock)
    @patch("RAG_medils.retrieval_and_generation.retrieval.semantic_search.embed_texts")
    def test_retrieve_applies_analyzed_dates_to_qdrant(self, embed, analyze):
        embed.side_effect = lambda texts, model, input_type: (
            [[0.1, 0.2]] if model == "bge-m3"
            else [{"indices": [1], "values": [0.5]}]
        )
        qdrant = FakeQdrant()
        for start, end in (
            ("2026-10-01", "2026-10-30"),
            ("2026-10-01", None),
            (None, "2026-10-30"),
            (None, None),
        ):
            with self.subTest(start=start, end=end):
                analyze.return_value = {
                    "query": "Rewritten query",
                    "createdDate_greater_than": start,
                    "createdDate_less_than": end,
                }
                def search(*args, **kwargs):
                    return search_summaries(*args, qdrant_client=qdrant, **kwargs)
                with patch.object(api, "search_summaries", side_effect=search):
                    response = self.client.post('/retrieve', json={"query": "Original query", "limit": 7})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(qdrant.calls[-1]['limit'], 7)
                self.assertEqual(embed.call_args.args[0], ["Rewritten query"])
                query_filter = qdrant.calls[-1]['query_filter']
                self.assertEqual(query_filter.must[0].key, "catalog_id")
                self.assertEqual(query_filter.must[0].match.value, "tenant:a")
                self.assertTrue(all(p.filter == query_filter for p in qdrant.calls[-1]["prefetch"]))
                if start is None and end is None:
                    self.assertIsNone(query_filter.should)
                else:
                    dated, undated = query_filter.should
                    self.assertEqual(dated.key, 'createdDateTime')
                    self.assertEqual(dated.range.gte, datetime(2026, 10, 1, tzinfo=timezone.utc) if start else None)
                    self.assertEqual(dated.range.lt, datetime(2026, 10, 31, tzinfo=timezone.utc) if end else None)
                    self.assertEqual(undated.is_empty.key, 'createdDateTime')

    def test_retrieve_is_documented_in_swagger(self):
        self.assertEqual(self.client.get('/docs').status_code, 200)
        schema = self.client.get('/openapi.json').json()
        operation = schema['paths']['/retrieve']['post']
        self.assertEqual(operation['tags'], ['Evaluation'])
        self.assertIn('extracted date filters', operation['description'])
        self.assertEqual(operation['responses']['200']['content']['application/json']['schema']['type'], 'array')
        request = schema['components']['schemas']['RetrievalRequest']
        self.assertEqual(set(request['properties']), {'query', 'limit'})


if __name__ == "__main__":
    unittest.main()
