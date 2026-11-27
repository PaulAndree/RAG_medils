import math
import unittest

from RAG_medils.experiment.evaluate import (
    aggregate,
    evidence_scores,
    map_at_k,
    mrr_at_k,
    ndcg_at_k,
    ranked_dataset_ids,
    recall_at_k,
    hit_at_k,
    ndcg_first_hit_at_k,
    question_targets,
    score_question,
)


class DocumentMetricTests(unittest.TestCase):
    ranked = ["a", "x", "b", "y"]
    relevant = {"a", "b", "c"}

    def test_hit_recall_mrr(self):
        self.assertEqual(hit_at_k(self.ranked, self.relevant, 10), 1.0)
        self.assertEqual(hit_at_k(["x"], self.relevant, 10), 0.0)
        self.assertAlmostEqual(recall_at_k(self.ranked, self.relevant, 10), 2 / 3)
        self.assertEqual(mrr_at_k(["x", "b"], self.relevant, 10), 0.5)
        self.assertEqual(mrr_at_k(["x", "b"], self.relevant, 1), 0.0)

    def test_map_divides_by_relevant_count(self):
        # precision at hits: 1/1 and 2/3 -> (1 + 2/3) / 3
        self.assertAlmostEqual(map_at_k(self.ranked, self.relevant, 10), (1 + 2 / 3) / 3)

    def test_ndcg(self):
        dcg = 1 + 1 / math.log2(4)
        ideal = 1 + 1 / math.log2(3) + 1 / math.log2(4)
        self.assertAlmostEqual(ndcg_at_k(self.ranked, self.relevant, 10), dcg / ideal)
        self.assertEqual(ndcg_at_k(["a"], {"a"}, 10), 1.0)


class RankingTests(unittest.TestCase):
    def test_dedupes_and_skips_catalog(self):
        points = [
            {"scope": "passage", "dataset_id": "d1"},
            {"scope": "catalog", "source_dataset_ids": ["d1", "d2"]},
            {"scope": "document", "dataset_id": "d1"},
            {"scope": "document_cluster", "dataset_id": "d2"},
        ]
        self.assertEqual(ranked_dataset_ids(points), ["d1", "d2"])

    def test_evidence_normalizes_markdown_and_whitespace(self):
        recall, hit = evidence_scores([["| Valor  estimado | 38.600,00 € |"], ["missing"]],
                                      ["**| Valor estimado | 38.600,00 € |**"])
        self.assertEqual((recall, hit), (0.5, 1.0))

    def test_score_question_uses_unit_text_and_sources(self):
        question = {
            "id": "q1", "question": "?", "relevant_doc_ids": ["email1"],
            "evidence": [{"doc_id": "email1", "text": "original wording"},
                         {"doc_id": "doc9", "text": "chunk detail"}],
        }
        points = [
            # Over-limit unit stored as a summary: evidence checked on the record.
            {"scope": "passage", "level": 0, "dataset_id": "email1", "summary_text": "summary"},
            {"scope": "document", "level": 1, "dataset_id": "doc9", "summary_text": "abstract",
             "source_chunk_ids": ["c1"]},
        ]
        row = score_question(question, points, k=10,
                             unit_texts={"email1": "... original wording ..."},
                             chunk_texts={"c1": "a chunk detail here"})
        self.assertEqual(row["doc_hit@10"], 1.0)
        self.assertEqual(row["evidence_recall_strict@10"], 0.5)
        self.assertEqual(row["evidence_recall@10"], 1.0)
        summary = aggregate([row])
        self.assertEqual(summary["doc_mrr@10"], 1.0)


class FactsFormatTests(unittest.TestCase):
    question = {
        "id": "q2", "question": "?",
        "evidence": [
            {"alternatives": [
                {"doc_id": "pcap2", "kind": "text", "text": "38.600,00 €"},
                {"doc_id": "email33", "kind": "metadata", "field": "metadata.to"},
            ]},
            {"alternatives": [{"doc_id": "note6", "kind": "text", "text": "plazo de 15 días"}]},
        ],
    }

    def test_relevant_set_is_every_alternative_doc(self):
        question_format, relevant, facts = question_targets(self.question)
        self.assertEqual(question_format, "facts")
        self.assertEqual(relevant, {"pcap2", "email33", "note6"})
        self.assertEqual(facts, [["38.600,00 €"], ["plazo de 15 días"]])

    def test_ndcg_ideal_is_one_record_at_rank_one(self):
        relevant = {f"d{i}" for i in range(50)}
        self.assertEqual(ndcg_first_hit_at_k(["d1", "x"], relevant, 10), 1.0)
        self.assertAlmostEqual(ndcg_first_hit_at_k(["x", "y", "d3"], relevant, 10), 0.5)
        self.assertEqual(ndcg_first_hit_at_k(["x"], relevant, 10), 0.0)

    def test_any_alternative_in_any_node_counts(self):
        points = [
            {"scope": "passage", "level": 0, "dataset_id": "other_doc", "summary_text": "Importe: 38.600,00 €"},
            {"scope": "passage", "level": 0, "dataset_id": "email33", "summary_text": "..."},
        ]
        row = score_question(self.question, points, k=10, unit_texts={}, chunk_texts={})
        self.assertEqual(row["doc_hit@10"], 1.0)
        self.assertEqual(row["doc_mrr@10"], 0.5)  # other_doc is not relevant; email33 is at rank 2
        self.assertEqual(row["evidence_recall@10"], 0.5)
        self.assertEqual(row["evidence_hit@10"], 1.0)
        self.assertNotIn("doc_recall@10", row)


if __name__ == "__main__":
    unittest.main()
