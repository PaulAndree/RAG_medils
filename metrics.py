from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from prometheus_client import CollectorRegistry, Gauge, Histogram
from prometheus_client.exposition import push_to_gateway


@dataclass(frozen=True, slots=True)
class ProcessMetricSample:
    """Metrics produced by one representation in a completed batch process."""

    representation: str
    document_count: int
    item_counts: Mapping[str, int]
    duration_seconds: float


def push_process_metrics(
    *,
    process: str,
    samples: Sequence[ProcessMetricSample],
    pushgateway_url: str,
    job: str,
) -> None:
    """Push the latest completed batch metrics to Prometheus Pushgateway."""

    registry = CollectorRegistry()
    document_count = Gauge(
        "rag_process_document_count",
        "Source documents handled by the latest completed process",
        ("process", "representation"),
        registry=registry,
    )
    item_count = Gauge(
        "rag_process_item_count",
        "Native artifacts handled by the latest completed process",
        ("process", "representation", "item_type"),
        registry=registry,
    )
    duration = Gauge(
        "rag_process_duration_seconds",
        "Duration of the latest completed process",
        ("process", "representation"),
        registry=registry,
    )

    for sample in samples:
        labels = {
            "process": process,
            "representation": sample.representation,
        }
        document_count.labels(**labels).set(sample.document_count)
        duration.labels(**labels).set(sample.duration_seconds)
        for item_type, count in sample.item_counts.items():
            item_count.labels(
                **labels,
                item_type=item_type,
            ).set(count)

    push_to_gateway(
        pushgateway_url,
        job=job,
        registry=registry,
    )


RETRIEVAL_DURATION = Histogram(
    "rag_retrieval_duration_seconds",
    "Time spent in each retrieval path",
    ("retrieval_type",),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
