import unittest
from unittest.mock import patch

from prometheus_client import generate_latest

from metrics import ProcessMetricSample, push_process_metrics


class ProcessMetricTests(unittest.TestCase):
    @patch("metrics.push_to_gateway")
    def test_pushes_dashboard_metric_contract(self, push):
        push_process_metrics(
            process="representation",
            samples=[
                ProcessMetricSample(
                    representation="passages",
                    document_count=2,
                    item_counts={"chunks": 12},
                    duration_seconds=1.25,
                ),
                ProcessMetricSample(
                    representation="graph",
                    document_count=2,
                    item_counts={"entities": 8, "relations": 4},
                    duration_seconds=2.5,
                ),
            ],
            pushgateway_url="http://pushgateway:9091",
            job="representation_builder",
        )

        push.assert_called_once()
        kwargs = push.call_args.kwargs
        self.assertEqual(kwargs["job"], "representation_builder")
        self.assertEqual(
            push.call_args.args[0],
            "http://pushgateway:9091",
        )
        payload = generate_latest(kwargs["registry"]).decode("utf-8")
        self.assertIn(
            'rag_process_document_count{process="representation",'
            'representation="passages"} 2.0',
            payload,
        )
        self.assertIn(
            'rag_process_item_count{item_type="chunks",'
            'process="representation",representation="passages"} 12.0',
            payload,
        )
        self.assertIn(
            'rag_process_duration_seconds{process="representation",'
            'representation="graph"} 2.5',
            payload,
        )


if __name__ == "__main__":
    unittest.main()
