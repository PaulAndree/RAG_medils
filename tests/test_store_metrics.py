import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from stores.main_ingestion import run_ingestion


class StoreMetricTests(unittest.TestCase):
    @patch("stores.main_ingestion.push_process_metrics")
    @patch("stores.main_ingestion.persist_dataset")
    @patch("stores.main_ingestion.prepare_dataset")
    def test_publishes_per_representation_counts_and_durations(
        self,
        prepare_dataset,
        persist_dataset,
        push_process_metrics,
    ):
        bundle = SimpleNamespace(
            entities=({"id": "E1"}, {"id": "E2"}),
            relations=({"subject_id": "E1", "object_id": "E2"},),
        )
        document_id = uuid4()
        document = SimpleNamespace(
            source_key="paper",
            warnings=(),
            argument_chunks=(object(),),
            entity_bundles=(bundle,),
        )
        summary = SimpleNamespace(
            document_id=document_id,
            source_document_ids=(str(document_id),),
        )
        prepare_dataset.return_value = SimpleNamespace(
            documents=(document,),
            summaries=(summary,),
        )
        persist_dataset.return_value = SimpleNamespace(
            documents=1,
            chunks=10,
            argument_chunks=6,
            arguments=3,
            entities=1,
            summaries=4,
            stale_source_keys=(),
            durations={
                "passages": 0.1,
                "arguments": 0.2,
                "summaries": 0.3,
                "graph": 0.4,
            },
        )

        with tempfile.TemporaryDirectory() as directory:
            result = run_ingestion(Path(directory))

        self.assertEqual(result, 0)
        kwargs = push_process_metrics.call_args.kwargs
        self.assertEqual(kwargs["process"], "store")
        self.assertEqual(kwargs["job"], "store_process")
        samples = {
            sample.representation: sample
            for sample in kwargs["samples"]
        }
        self.assertEqual(samples["passages"].document_count, 1)
        self.assertEqual(samples["arguments"].item_counts["arguments"], 3)
        self.assertEqual(samples["summaries"].document_count, 1)
        self.assertEqual(samples["graph"].item_counts["entities"], 2)
        self.assertEqual(samples["graph"].item_counts["relations"], 1)
        self.assertEqual(samples["graph"].duration_seconds, 0.4)


if __name__ == "__main__":
    unittest.main()
