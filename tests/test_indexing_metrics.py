import unittest
from unittest.mock import MagicMock, patch

from indexing.arguments import indexer_qdrant as arguments
from indexing.graph import indexer_neo4j as graph
from indexing.passages import indexer_qdrant as passages
from indexing.summaries import indexer_qdrant as summaries


class IndexingMetricTests(unittest.TestCase):
    def test_passage_indexer_publishes_unique_document_and_chunk_counts(self):
        chunks = [
            {"document_id": "doc-1"},
            {"document_id": "doc-1"},
            {"document_id": "doc-2"},
        ]
        with (
            patch.object(passages, "get_indexable_chunks", return_value=chunks),
            patch.object(passages, "build_collection_name", return_value="new"),
            patch.object(passages, "get_alias_target", return_value=None),
            patch.object(passages, "create_collection"),
            patch.object(passages, "index_chunks"),
            patch.object(passages, "validate_collection"),
            patch.object(passages, "activate_collection"),
            patch.object(passages, "push_process_metrics") as push,
        ):
            passages.main()

        sample = push.call_args.kwargs["samples"][0]
        self.assertEqual(push.call_args.kwargs["job"], "indexing_passages")
        self.assertEqual(sample.document_count, 2)
        self.assertEqual(sample.item_counts, {"chunks": 3})

    def test_argument_indexer_publishes_unique_document_and_item_counts(self):
        records = [
            {"document_id": "doc-1"},
            {"document_id": "doc-1"},
            {"document_id": "doc-2"},
        ]
        with (
            patch.object(arguments, "get_indexable_arguments", return_value=records),
            patch.object(arguments, "build_collection_name", return_value="new"),
            patch.object(arguments, "get_alias_target", return_value=None),
            patch.object(arguments, "create_collection"),
            patch.object(arguments, "index_arguments"),
            patch.object(arguments, "validate_collection"),
            patch.object(arguments, "activate_collection"),
            patch.object(arguments, "push_process_metrics") as push,
        ):
            arguments.main()

        sample = push.call_args.kwargs["samples"][0]
        self.assertEqual(push.call_args.kwargs["job"], "indexing_arguments")
        self.assertEqual(sample.document_count, 2)
        self.assertEqual(sample.item_counts, {"arguments": 3})

    def test_summary_indexer_uses_direct_and_provenance_document_ids(self):
        records = [
            {
                "document_id": "doc-1",
                "source_document_ids": ["doc-1"],
            },
            {
                "document_id": None,
                "source_document_ids": ["doc-1", "doc-2"],
            },
        ]
        with (
            patch.object(summaries, "get_indexable_summaries", return_value=records),
            patch.object(summaries, "build_collection_name", return_value="new"),
            patch.object(summaries, "get_alias_target", return_value=None),
            patch.object(summaries, "create_collection"),
            patch.object(summaries, "index_summaries"),
            patch.object(summaries, "validate_collection"),
            patch.object(summaries, "activate_collection"),
            patch.object(summaries, "push_process_metrics") as push,
        ):
            summaries.main()

        sample = push.call_args.kwargs["samples"][0]
        self.assertEqual(push.call_args.kwargs["job"], "indexing_summaries")
        self.assertEqual(sample.document_count, 2)
        self.assertEqual(sample.item_counts, {"summaries": 2})

    def test_graph_indexer_publishes_validated_graph_counts(self):
        counts = {
            "documents": 2,
            "chunks": 7,
            "entities": 11,
            "relations": 5,
        }
        snapshot = {
            "documents": [object()],
            "chunks": [object()],
            "entities": [object()],
            "relations": [object()],
        }
        driver_context = MagicMock()
        driver = MagicMock()
        session_context = MagicMock()
        session = MagicMock()
        driver_context.__enter__.return_value = driver
        driver.session.return_value = session_context
        session_context.__enter__.return_value = session

        with (
            patch.object(graph, "get_indexable_entity_relations", return_value=[{}]),
            patch.object(graph, "build_graph_snapshot", return_value=snapshot),
            patch.object(graph.GraphDatabase, "driver", return_value=driver_context),
            patch.object(graph, "create_constraints"),
            patch.object(graph, "replace_graph"),
            patch.object(graph, "validate_graph", return_value=counts),
            patch.object(graph, "push_process_metrics") as push,
        ):
            graph.main()

        sample = push.call_args.kwargs["samples"][0]
        self.assertEqual(push.call_args.kwargs["job"], "indexing_graph")
        self.assertEqual(sample.document_count, 2)
        self.assertEqual(
            sample.item_counts,
            {"chunks": 7, "entities": 11, "relations": 5},
        )


if __name__ == "__main__":
    unittest.main()
