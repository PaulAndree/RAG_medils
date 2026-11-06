import unittest
from unittest.mock import patch

from representations.graph.normalizer import (
    GraphValidationError,
    normalize_document_graph,
)


def relation(subject="E1", object_id="E2", confidence=0.9):
    return {
        "subject_id": subject,
        "relation": "works on",
        "object_id": object_id,
        "evidence": "Alice works on Project Alpha.",
        "confidence": confidence,
        "negated": False,
        "certainty": "certain",
        "qualifiers": {},
    }


def chunk_result(chunk_id=0):
    return {
        "chunk_id": chunk_id,
        "entities": [
            {"id": "E1", "name": "Alice", "type": "Person"},
            {"id": "E2", "name": "Project Alpha", "type": "Project"},
            {"id": "E3", "name": "Unused name", "type": "Concept"},
        ],
        "relations": [relation()],
    }


NORMALIZATION_RESPONSE = {
    "entities": [
        {
            "mapping_id": "ENTITY_1",
            "canonical_name": "Alice",
            "canonical_type": "PERSON",
        },
        {
            "mapping_id": "ENTITY_2",
            "canonical_name": "Project Alpha",
            "canonical_type": "PROJECT",
        },
    ],
    "relations": [
        {
            "mapping_id": "RELATION_1",
            "canonical_relation": "WORKS_ON",
        }
    ],
}


class GraphNormalizerTests(unittest.TestCase):
    @patch(
        "representations.graph.normalizer._request_normalization",
        return_value=NORMALIZATION_RESPONSE,
    )
    def test_normalizes_without_changing_ids_or_evidence(self, request):
        original = chunk_result()
        normalized = normalize_document_graph(
            [original],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(
            [entity["id"] for entity in normalized[0]["entities"]],
            ["E1", "E2"],
        )
        self.assertEqual(normalized[0]["entities"][0]["type"], "PERSON")
        self.assertEqual(
            normalized[0]["entities"][0]["original_type"],
            "Person",
        )
        self.assertEqual(
            normalized[0]["relations"][0]["relation"],
            "WORKS_ON",
        )
        self.assertEqual(
            normalized[0]["relations"][0]["evidence"],
            original["relations"][0]["evidence"],
        )
        self.assertEqual(len(original["entities"]), 3)
        request.assert_called_once()

    @patch(
        "representations.graph.normalizer._request_normalization",
        return_value={
            "entities": [
                {
                    "mapping_id": "ENTITY_1",
                    "canonical_name": "Alice",
                    "canonical_type": "person",
                },
                {
                    "mapping_id": "ENTITY_2",
                    "canonical_name": "Project Alpha",
                    "canonical_type": "research project",
                },
            ],
            "relations": [
                {
                    "mapping_id": "RELATION_1",
                    "canonical_relation": "works-on",
                }
            ],
        },
    )
    def test_normalizes_model_labels_to_upper_snake_case(self, request):
        normalized = normalize_document_graph(
            [chunk_result()],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(
            [entity["type"] for entity in normalized[0]["entities"]],
            ["PERSON", "RESEARCH_PROJECT"],
        )
        self.assertEqual(
            normalized[0]["relations"][0]["relation"],
            "WORKS_ON",
        )
        request.assert_called_once()

    @patch("representations.graph.normalizer._request_normalization")
    def test_low_confidence_relation_and_orphan_entities_are_pruned(
        self,
        request,
    ):
        result = chunk_result()
        result["relations"][0]["confidence"] = 0.7

        normalized = normalize_document_graph(
            [result],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(normalized[0]["entities"], [])
        self.assertEqual(normalized[0]["relations"], [])
        request.assert_not_called()

    @patch(
        "representations.graph.normalizer._request_normalization",
        return_value={"entities": [], "relations": []},
    )
    def test_missing_llm_mapping_is_rejected(self, request):
        with self.assertRaisesRegex(
            GraphValidationError,
            "mappings do not match",
        ):
            normalize_document_graph(
                [chunk_result()],
                ["Alice works on Project Alpha."],
                "document",
            )
        request.assert_called_once()

    @patch("representations.graph.normalizer._request_normalization")
    def test_unknown_relation_endpoint_is_pruned(self, request):
        result = chunk_result()
        result["relations"][0]["object_id"] = "missing"

        normalized = normalize_document_graph(
            [result],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(normalized[0]["entities"], [])
        self.assertEqual(normalized[0]["relations"], [])
        request.assert_not_called()

    @patch(
        "representations.graph.normalizer._request_normalization",
        return_value=NORMALIZATION_RESPONSE,
    )
    def test_missing_qualifiers_receive_empty_object(self, request):
        result = chunk_result()
        result["relations"][0].pop("qualifiers")

        normalized = normalize_document_graph(
            [result],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(normalized[0]["relations"][0]["qualifiers"], {})
        request.assert_called_once()

    @patch("representations.graph.normalizer._request_normalization")
    def test_non_verbatim_evidence_and_entities_are_pruned(self, request):
        result = chunk_result()
        result["relations"][0]["evidence"] = "Paraphrased evidence"

        normalized = normalize_document_graph(
            [result],
            ["Alice works on Project Alpha."],
            "document",
        )

        self.assertEqual(normalized[0]["entities"], [])
        self.assertEqual(normalized[0]["relations"], [])
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
