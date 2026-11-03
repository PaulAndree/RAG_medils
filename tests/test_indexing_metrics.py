import unittest
from datetime import datetime
from unittest.mock import patch

from RAG_medils.ingest.indexing import main as indexing_pipeline
from RAG_medils.ingest.indexing.summaries import indexer_qdrant as summaries


class IndexingMetricTests(unittest.TestCase):
    @patch("indexing.summaries.indexer_qdrant.main")
    def test_pipeline_runs_only_the_summaries_indexer(self, index_summaries):
        durations = indexing_pipeline.run_pipeline()

        index_summaries.assert_called_once_with()
        self.assertEqual(set(durations), {"summaries"})

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
            patch.object(summaries, "collection_update_lock"),
            patch.object(summaries, "cleanup_unused_collections"),
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

    def test_summary_indexer_embeds_and_uploads_the_complete_summary_schema(self):
        records = [
            {
                "node_id": "passage-1",
                "summary_text": "Passage text",
                "level": 0,
                "scope": "passage",
                "createdDateTime": datetime.fromisoformat("2026-10-28T10:30:00Z"),
                "modifiedDateTime": datetime.fromisoformat("2026-10-29T14:30:00Z"),
                "document_id": "doc-1",
                "catalog_id": "catalog",
                "source_key": "paper",
                "chunk_index": 0,
                "title": "Passage title",
                "token_count": 2,
                "source_node_ids": [],
                "source_chunk_ids": ["passage-1"],
                "source_document_ids": ["doc-1"],
            },
            {
                "node_id": "summary-1",
                "summary_text": "Document summary",
                "level": 1,
                "scope": "document",
                "createdDateTime": None,
                "modifiedDateTime": None,
                "document_id": "doc-1",
                "catalog_id": "catalog",
                "source_key": None,
                "chunk_index": None,
                "title": None,
                "token_count": None,
                "source_node_ids": ["passage-1"],
                "source_chunk_ids": ["passage-1"],
                "source_document_ids": ["doc-1"],
            },
        ]
        dense_vectors = [[0.1], [0.2]]
        sparse_vectors = [
            {"indices": [1], "values": [0.3]},
            {"indices": [2], "values": [0.4]},
        ]

        with (
            patch.object(
                summaries,
                "embed_texts",
                side_effect=[dense_vectors, sparse_vectors],
            ) as embed,
            patch.object(summaries.client, "upload_collection") as upload,
        ):
            summaries.index_summaries("summaries", records)

        self.assertEqual(
            embed.call_args_list[0].args[0],
            ["Passage title\n\nPassage text", "Document summary"],
        )
        payloads = upload.call_args.kwargs["payload"]
        self.assertEqual(payloads[0], {
            **records[0],
            "createdDateTime": "2026-10-28T10:30:00+00:00",
            "modifiedDateTime": "2026-10-29T14:30:00+00:00",
        })
        self.assertEqual(payloads[1], records[1])


if __name__ == "__main__":
    unittest.main()
