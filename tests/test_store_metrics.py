import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from RAG_medils.ingest.stores.main_ingestion import run_ingestion


class StoreMetricTests(unittest.TestCase):
    @patch("stores.main_ingestion.push_process_metrics")
    @patch("stores.main_ingestion.initialize_database")
    @patch("stores.main_ingestion.store_summaries")
    @patch("stores.main_ingestion.prepare_summaries")
    def test_publishes_raptor_counts_and_duration(
        self,
        prepare_summaries,
        store_summaries,
        initialize_database,
        push_process_metrics,
    ):
        document = SimpleNamespace(
            source_key="paper",
            warnings=(),
        )
        level_zero = SimpleNamespace(scope="passage")
        summary = SimpleNamespace(scope="document")
        prepare_summaries.return_value = (level_zero, summary)
        store_summaries.return_value = SimpleNamespace(
            documents=1,
            summaries=2,
            stale_source_keys=(),
            durations={
                "documents": 0.1,
                "summaries": 0.3,
            },
        )

        with tempfile.TemporaryDirectory() as directory:
            result = run_ingestion(Path(directory))

        self.assertEqual(result, 0)
        kwargs = push_process_metrics.call_args.kwargs
        self.assertEqual(kwargs["process"], "store")
        self.assertEqual(kwargs["job"], "store_process")
        samples = kwargs["samples"]
        self.assertEqual(len(samples), 1)
        sample = samples[0]
        self.assertEqual(sample.representation, "raptor")
        self.assertEqual(sample.document_count, 1)
        self.assertEqual(sample.item_counts["level_zero_nodes"], 1)
        self.assertEqual(sample.item_counts["summary_nodes"], 1)
        self.assertAlmostEqual(sample.duration_seconds, 0.4)


if __name__ == "__main__":
    unittest.main()
