import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from evaluation.retrieval_metrics import (
    BenchmarkQuestion,
    EvaluationError,
    EvidenceItem,
    RetrievedItem,
    evaluate_runs,
    extract_graph,
    extract_passages,
    extract_summaries,
    load_questions,
    match_retrieved_items,
    query_api,
    run_evaluation,
)


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, *, json, timeout):
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse(self.responses.pop(0))


class KeywordEmbedder:
    def embed(self, texts):
        for text in texts:
            lowered = text.lower()
            if "alpha" in lowered:
                yield np.array([1.0, 0.0])
            elif "beta" in lowered:
                yield np.array([0.0, 1.0])
            else:
                yield np.array([-1.0, 0.0])


def api_response():
    return {
        "question": "Question?",
        "documents": [
            {
                "chunk_id": "passage-1",
                "content": "Alpha result",
                "score": 0.9,
            }
        ],
        "summaries": [
            {
                "node_id": "summary-1",
                "summary_text": "Beta summary",
                "score": 0.8,
            }
        ],
        "graph_context": {
            "matches": [
                {"rank": 1, "chunk_id": "graph-1", "score": 0.7},
                {"rank": 2, "chunk_id": "graph-2", "score": 0.6},
            ],
            "records": [
                {
                    "rank": 1,
                    "chunk": {"id": "graph-1", "content": "Alpha graph"},
                    "entity": {"name": "Alice", "type": "Person"},
                    "relation": {
                        "relation": "works with",
                        "evidence": "Alpha relation evidence",
                    },
                    "connected_entity": {"name": "NEXUS"},
                },
                {
                    "rank": 1,
                    "chunk": {"id": "graph-1", "content": "Alpha graph"},
                    "entity": {"name": "Alice", "type": "Person"},
                    "relation": {"relation": "works with"},
                    "connected_entity": {"name": "NEXUS"},
                },
            ],
        },
    }


class DatasetTests(unittest.TestCase):
    def test_load_questions_validates_and_deduplicates_normalized_evidence(self):
        data = {
            "question_count": 1,
            "questions": [
                {
                    "id": "q1",
                    "question": "Question?",
                    "evidence": [
                        {"text": "Alpha   evidence"},
                        {"text": "Alpha evidence\n"},
                        {"text": "Beta evidence"},
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            questions = load_questions(path)

        self.assertEqual(len(questions), 1)
        self.assertEqual(
            [item.text for item in questions[0].evidence],
            ["Alpha evidence", "Beta evidence"],
        )
        self.assertEqual(
            [item.identifier for item in questions[0].evidence],
            ["q1::evidence::1", "q1::evidence::2"],
        )

    def test_load_questions_rejects_empty_evidence(self):
        data = {
            "question_count": 1,
            "questions": [{"id": "q1", "question": "Question?", "evidence": []}],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(EvaluationError, "has no evidence"):
                load_questions(path)


class ApiAndExtractionTests(unittest.TestCase):
    def setUp(self):
        self.question = BenchmarkQuestion(
            identifier="q1",
            question="Question?",
            evidence=(EvidenceItem("q1::evidence::1", "Alpha evidence"),),
        )

    def test_query_api_uses_documents_wire_value(self):
        session = FakeSession([api_response()])

        result = query_api(
            session,
            api_url="http://localhost:8004/v1/query",
            question=self.question,
            limit=5,
            timeout=60,
        )

        self.assertEqual(result["documents"][0]["chunk_id"], "passage-1")
        self.assertEqual(
            session.calls[0]["json"],
            {
                "question": "Question?",
                "limit": 5,
                "retrievals": ["documents", "summaries", "graph"],
            },
        )

    def test_query_api_rejects_malformed_response(self):
        session = FakeSession([{"documents": [], "summaries": []}])

        with self.assertRaisesRegex(EvaluationError, "graph_context"):
            query_api(
                session,
                api_url="http://localhost:8004/v1/query",
                question=self.question,
                limit=5,
                timeout=60,
            )

    def test_extractors_preserve_rank_and_group_graph_records(self):
        response = api_response()

        passages = extract_passages(response, "q1", 5)
        summaries = extract_summaries(response, "q1", 5)
        graph = extract_graph(response, "q1", 5)

        self.assertEqual(passages[0].identifier, "passage-1")
        self.assertEqual(passages[0].text, "Alpha result")
        self.assertEqual(summaries[0].identifier, "summary-1")
        self.assertEqual(summaries[0].text, "Beta summary")
        self.assertEqual([item.rank for item in graph], [1, 2])
        self.assertEqual(graph[0].text.count("Alpha graph"), 1)
        self.assertIn("Alpha relation evidence", graph[0].text)
        self.assertIn("Alice", graph[0].text)
        self.assertEqual(graph[1].text, "")


class MatchingAndMetricTests(unittest.TestCase):
    def test_rank_first_matching_is_one_to_one_and_honors_threshold(self):
        question = BenchmarkQuestion(
            identifier="q1",
            question="Question?",
            evidence=(
                EvidenceItem("e1", "Evidence one"),
                EvidenceItem("e2", "Evidence two"),
            ),
        )
        items = [
            RetrievedItem(1, "r1", "Result mixed", 0.9, {}),
            RetrievedItem(2, "r2", "Result duplicate", 0.8, {}),
        ]
        embeddings = {
            "Evidence one": np.array([1.0, 0.0]),
            "Evidence two": np.array([0.0, 1.0]),
            "Result mixed": np.array([0.8, 0.6]),
            "Result duplicate": np.array([1.0, 0.0]),
        }

        run, diagnostics = match_retrieved_items(
            question=question,
            representation="passage",
            items=items,
            embeddings=embeddings,
            threshold=0.60,
            cutoff=5,
        )

        self.assertEqual(diagnostics[0]["matched_evidence_id"], "e1")
        self.assertFalse(diagnostics[1]["matched"])
        self.assertIn("q1::passage::nonrelevant::2", run)
        self.assertEqual(list(run.values()), [5.0, 4.0])

    def test_empty_retrieval_gets_irrelevant_sentinel(self):
        question = BenchmarkQuestion(
            identifier="q1",
            question="Question?",
            evidence=(EvidenceItem("e1", "Evidence"),),
        )

        run, diagnostics = match_retrieved_items(
            question=question,
            representation="graph",
            items=[],
            embeddings={"Evidence": np.array([1.0])},
            threshold=0.60,
            cutoff=5,
        )

        self.assertEqual(diagnostics, [])
        self.assertEqual(run, {"q1::graph::nonrelevant::empty": 0.0})

    def test_ranx_metrics_are_deterministic(self):
        qrels = {"q1": {"e1": 1, "e2": 1}}
        one_match = {"q1": {"e1": 5.0, "nonrelevant": 4.0}}
        runs = {
            representation: one_match
            for representation in ("passage", "summaries", "graph")
        }

        aggregate, per_question = evaluate_runs(qrels, runs, 5)

        for representation in runs:
            self.assertEqual(aggregate[representation]["hit_rate@5"], 1.0)
            self.assertEqual(aggregate[representation]["recall@5"], 0.5)
            self.assertEqual(aggregate[representation]["mrr@5"], 1.0)
            self.assertEqual(aggregate[representation]["map@5"], 0.5)
            self.assertEqual(
                per_question[representation]["q1"],
                aggregate[representation],
            )


class EndToEndTests(unittest.TestCase):
    def test_run_evaluation_writes_aggregate_and_detailed_results(self):
        data = {
            "question_count": 1,
            "questions": [
                {
                    "id": "q1",
                    "question": "Question?",
                    "evidence": [
                        {"text": "Alpha evidence"},
                        {"text": "Beta evidence"},
                    ],
                }
            ],
        }
        session = FakeSession([api_response()])
        with tempfile.TemporaryDirectory() as directory:
            questions_path = Path(directory) / "questions.json"
            output_path = Path(directory) / "results.json"
            questions_path.write_text(json.dumps(data), encoding="utf-8")

            result = run_evaluation(
                questions_path=questions_path,
                api_url="http://localhost:8004/v1/query",
                limit=5,
                threshold=0.60,
                timeout=60,
                output_path=output_path,
                session=session,
                embedder=KeywordEmbedder(),
            )
            persisted = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(len(session.calls), 1)
        self.assertEqual(
            set(result["aggregate_metrics"]),
            {"passage", "summaries", "graph"},
        )
        self.assertTrue(
            all(len(metrics) == 5 for metrics in result["aggregate_metrics"].values())
        )
        self.assertEqual(persisted["configuration"]["question_count"], 1)
        self.assertEqual(len(persisted["questions"]), 1)
        self.assertEqual(
            set(persisted["questions"][0]["representations"]),
            {"passage", "summaries", "graph"},
        )
        self.assertIn("api_response", persisted["questions"][0])


if __name__ == "__main__":
    unittest.main()
