import json
import unittest

from indexing.graph.indexer_neo4j import (
    build_graph_snapshot,
    entity_id,
)


def bundle(chunk_id, *, relations=None):
    return {
        "bundle_id": f"bundle-{chunk_id}",
        "chunk_id": chunk_id,
        "entities": [
            {"id": "E1", "name": "Alice", "type": "PERSON"},
            {"id": "E2", "name": "Project", "type": "PROJECT"},
        ],
        "relations": relations
        if relations is not None
        else [
            {
                "subject_id": "E1",
                "object_id": "E2",
                "relation": "WORKS_ON",
                "evidence": "Alice works on Project.",
                "confidence": 0.9,
                "negated": False,
                "certainty": "high",
                "qualifiers": {"since": 2024},
            }
        ],
        "document_id": "document-1",
        "document_version": 1,
        "chunk_index": 0,
        "chunk_title": "Introduction",
        "chunk_content": "Alice works on Project.",
        "doc_name": "document.pdf",
        "document_title": "Document",
    }


class GraphSnapshotTests(unittest.TestCase):
    def test_entity_ids_are_scoped_to_the_chunk(self):
        snapshot = build_graph_snapshot(
            [bundle("chunk-1"), bundle("chunk-2")]
        )

        ids = {item["id"] for item in snapshot["entities"]}
        self.assertIn(entity_id("chunk-1", "E1"), ids)
        self.assertIn(entity_id("chunk-2", "E1"), ids)
        self.assertEqual(len(ids), 4)

    def test_snapshot_preserves_relation_properties(self):
        snapshot = build_graph_snapshot([bundle("chunk-1")])

        self.assertEqual(len(snapshot["documents"]), 1)
        self.assertEqual(len(snapshot["chunks"]), 1)
        self.assertEqual(len(snapshot["entities"]), 2)
        self.assertEqual(len(snapshot["relations"]), 1)
        relation = snapshot["relations"][0]
        self.assertEqual(relation["relation"], "WORKS_ON")
        self.assertEqual(
            json.loads(relation["qualifiers_json"]),
            {"since": 2024},
        )

    def test_empty_relation_bundles_are_ignored(self):
        snapshot = build_graph_snapshot(
            [bundle("chunk-1", relations=[])]
        )

        self.assertTrue(all(not rows for rows in snapshot.values()))

    def test_unreferenced_entities_are_ignored(self):
        source = bundle("chunk-1")
        source["entities"].append(
            {"id": "E3", "name": "Unused", "type": "CONCEPT"}
        )

        snapshot = build_graph_snapshot([source])

        self.assertEqual(
            {row["local_id"] for row in snapshot["entities"]},
            {"E1", "E2"},
        )

    def test_self_relation_bundles_are_ignored(self):
        self_relation = {
            "subject_id": "E1",
            "object_id": "E1",
            "relation": "SAME_AS",
        }

        snapshot = build_graph_snapshot(
            [bundle("chunk-1", relations=[self_relation])]
        )

        self.assertTrue(all(not rows for rows in snapshot.values()))

    def test_missing_relation_endpoint_is_rejected(self):
        invalid = bundle("chunk-1")
        invalid["relations"][0]["object_id"] = "missing"

        with self.assertRaisesRegex(ValueError, "does not exist"):
            build_graph_snapshot([invalid])


if __name__ == "__main__":
    unittest.main()
