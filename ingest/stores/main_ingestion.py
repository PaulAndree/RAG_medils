"""Command-line entry point for PostgreSQL representation ingestion."""

import argparse
import os
import sys
from pathlib import Path

from RAG_medils.metrics import ProcessMetricSample, push_process_metrics
from RAG_medils.ingest.stores.database_postgres import initialize_database, store_summaries
from RAG_medils.ingest.stores.ingestion import (
    FolderScanError,
    InputValidationError,
    prepare_summaries,
)


DEFAULT_PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://localhost:9093",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and store summaries for already registered documents."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Root containing the summaries/ RAPTOR level files.",
    )
    parser.add_argument(
        "--pushgateway-url",
        default=DEFAULT_PUSHGATEWAY_URL,
        help=f"Prometheus Pushgateway URL (default: {DEFAULT_PUSHGATEWAY_URL})",
    )
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Disable Pushgateway metric publication.",
    )
    return parser.parse_args()


def run_ingestion(
    data_root: Path,
    *,
    pushgateway_url: str = DEFAULT_PUSHGATEWAY_URL,
    metrics_enabled: bool = True,
) -> int:
    try:
        summaries = prepare_summaries(data_root / "summaries")
    except (FolderScanError, InputValidationError) as exc:
        print(f"[fatal] invalid input: {exc}", file=sys.stderr)
        return 1

    try:
        initialize_database()
        result = store_summaries(summaries)
    except Exception as exc:
        print(f"[fatal] database ingestion failed: {exc}", file=sys.stderr)
        return 1

    passage_nodes = sum(
        summary.scope == "passage" for summary in summaries
    )
    print("Ingestion complete")
    print(f"  documents:        {result.documents}")
    print(f"  level-zero nodes: {passage_nodes}")
    print(f"  summary nodes:    {result.summaries - passage_nodes}")
    print(f"  total nodes:      {result.summaries}")

    if metrics_enabled:
        try:
            push_process_metrics(
                process="store",
                samples=[
                    ProcessMetricSample(
                        representation="raptor",
                        document_count=result.documents,
                        item_counts={
                            "level_zero_nodes": passage_nodes,
                            "summary_nodes": result.summaries - passage_nodes,
                        },
                        duration_seconds=sum(result.durations.values()),
                    ),
                ],
                pushgateway_url=pushgateway_url,
                job="store_process",
            )
        except Exception as exc:
            print(f"[ingestion] warning: could not publish metrics: {exc}")

    return 0


def main() -> int:
    args = parse_args()
    return run_ingestion(
        args.data_dir,
        pushgateway_url=args.pushgateway_url,
        metrics_enabled=not args.no_metrics,
    )


if __name__ == "__main__":
    raise SystemExit(main())
