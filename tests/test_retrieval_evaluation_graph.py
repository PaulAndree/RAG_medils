import unittest

from evaluation.retrieval_metrics import (
    BenchmarkQuestion,
    EvidenceItem,
    EvidenceJudgment,
    EvaluationError,
    PairTask,
    RAGCheckerRetrievalAdapter,
    RetrievedItem,
    extract_graph,
)


class GraphEvaluationContractTests(unittest.TestCase):
    def test_extracts_self_contained_graph_results(self):
        response = {
            "graph_context": {
                "results": [
                    {
                        "result_id": "point-1",
                        "rank": 1,
                        "score": 0.91,
                        "argument_id": "argument-1",
                        "claim": "Alice works with NEXUS.",
                        "evidence": ["Alice is a NEXUS researcher."],
                        "source_chunk_id": "chunk-1",
                        "source_content": "The project roster includes Alice.",
                        "graph_expansion": {
                            "entities": [
                                {"id": "entity-1", "name": "Alice", "type": "PERSON"},
                                {
                                    "id": "entity-2",
                                    "name": "NEXUS",
                                    "type": "ORGANIZATION",
                                },
                            ],
                            "relations": [
                                {
                                    "id": "relation-1",
                                    "relation": "WORKS_WITH",
                                    "evidence": "Alice works with NEXUS.",
                                    "source": {"id": "entity-1", "name": "Alice"},
                                    "target": {"id": "entity-2", "name": "NEXUS"},
                                }
                            ],
                        },
                    }
                ]
            }
        }

        items = extract_graph(response, "q1")

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].identifier, "point-1")
        self.assertEqual(items[0].rank, 1)
        self.assertIn("Claim: Alice works with NEXUS.", items[0].content)
        self.assertIn("Argument evidence: Alice is a NEXUS researcher.", items[0].content)
        self.assertIn("Relation: Alice --WORKS_WITH--> NEXUS", items[0].content)

    def test_empty_graph_expansion_remains_judgeable(self):
        response = {
            "graph_context": {
                "results": [
                    {
                        "result_id": "point-1",
                        "rank": 1,
                        "score": 0.91,
                        "claim": "The pilot starts in October.",
                        "evidence": ["The approved window begins on 5 October."],
                        "source_chunk_id": "chunk-1",
                        "source_content": "",
                        "graph_expansion": {"entities": [], "relations": []},
                    }
                ]
            }
        }

        items = extract_graph(response, "q1")

        self.assertEqual(len(items), 1)
        self.assertIn("Claim: The pilot starts in October.", items[0].content)

    def test_rejects_result_without_any_judgeable_content(self):
        response = {
            "graph_context": {
                "results": [
                    {
                        "result_id": "point-1",
                        "rank": 1,
                        "claim": None,
                        "evidence": [],
                        "source_content": None,
                        "graph_expansion": {"entities": [], "relations": []},
                    }
                ]
            }
        }

        with self.assertRaisesRegex(EvaluationError, "no judgeable content"):
            extract_graph(response, "q1")


class RetrievalMetricCutoffTests(unittest.TestCase):
    def test_fewer_than_ten_results_use_actual_count_for_precision(self):
        question = BenchmarkQuestion(
            "q1",
            "Question?",
            (
                EvidenceItem("e1", "Evidence one."),
                EvidenceItem("e2", "Evidence two."),
            ),
        )
        item = RetrievedItem(1, "r1", "graph", "Supports evidence one.", 0.9, {})
        judgments = {
            PairTask(question, evidence, item).pair_id: EvidenceJudgment(
                evidence_id=evidence.identifier,
                result_id=item.identifier,
                match=1 if evidence.identifier == "e1" else 0,
                explanation="Test judgment.",
            )
            for evidence in question.evidence
        }

        metrics = RAGCheckerRetrievalAdapter().compute(question, [item], judgments)

        self.assertEqual(metrics["evidence_recall_at_10"], 0.5)
        self.assertEqual(metrics["context_precision_at_10"], 1.0)
        self.assertEqual(metrics["rr_at_10"], 1.0)


if __name__ == "__main__":
    unittest.main()
