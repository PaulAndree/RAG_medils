"""Command-line entry point for PostgreSQL representation ingestion."""

import argparse
import os
import sys
from pathlib import Path

from metrics import ProcessMetricSample, push_process_metrics
from stores.database_postgres import persist_dataset
from stores.ingestion import (
    FolderScanError,
    InputValidationError,
    prepare_dataset,
)


DEFAULT_PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://localhost:9091",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and ingest document representations into PostgreSQL."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Root containing passages, arguments, entities, and summaries.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Drop and recreate the six representation tables before loading.",
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
    rebuild: bool = False,
    pushgateway_url: str = DEFAULT_PUSHGATEWAY_URL,
    metrics_enabled: bool = True,
) -> int:
    try:
        dataset = prepare_dataset(data_root)
    except (FolderScanError, InputValidationError) as exc:
        print(f"[fatal] invalid input: {exc}", file=sys.stderr)
        return 1

    for document in dataset.documents:
        for warning in document.warnings:
            print(f"[warning] {document.source_key}: {warning}")

    try:
        result = persist_dataset(
            dataset,
            rebuild=rebuild,
        )
    except Exception as exc:
        print(f"[fatal] database ingestion failed: {exc}", file=sys.stderr)
        return 1

    for source_key in result.stale_source_keys:
        print(
            f"[stale] {source_key}: source passage was not found; "
            "database rows were preserved"
        )

    print("Ingestion complete")
    print(f"  documents:       {result.documents}")
    print(f"  passage chunks:  {result.chunks}")
    print(f"  argument chunks: {result.argument_chunks}")
    print(f"  arguments:       {result.arguments}")
    print(f"  entity bundles:  {result.entities}")
    print(f"  summaries:       {result.summaries}")
    print(f"  stale documents: {len(result.stale_source_keys)}")

    if metrics_enabled:
        summary_document_ids = {
            str(summary.document_id)
            for summary in dataset.summaries
            if summary.document_id is not None
        }
        for summary in dataset.summaries:
            summary_document_ids.update(summary.source_document_ids)

        try:
            push_process_metrics(
                process="store",
                samples=[
                    ProcessMetricSample(
                        representation="passages",
                        document_count=len(dataset.documents),
                        item_counts={"chunks": result.chunks},
                        duration_seconds=result.durations["passages"],
                    ),
                    ProcessMetricSample(
                        representation="arguments",
                        document_count=sum(
                            bool(document.argument_chunks)
                            for document in dataset.documents
                        ),
                        item_counts={
                            "argument_chunks": result.argument_chunks,
                            "arguments": result.arguments,
                        },
                        duration_seconds=result.durations["arguments"],
                    ),
                    ProcessMetricSample(
                        representation="summaries",
                        document_count=len(summary_document_ids),
                        item_counts={"summaries": result.summaries},
                        duration_seconds=result.durations["summaries"],
                    ),
                    ProcessMetricSample(
                        representation="graph",
                        document_count=sum(
                            bool(document.entity_bundles)
                            for document in dataset.documents
                        ),
                        item_counts={
                            "entity_bundles": result.entities,
                            "entities": sum(
                                len(bundle.entities)
                                for document in dataset.documents
                                for bundle in document.entity_bundles
                            ),
                            "relations": sum(
                                len(bundle.relations)
                                for document in dataset.documents
                                for bundle in document.entity_bundles
                            ),
                        },
                        duration_seconds=result.durations["graph"],
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
        rebuild=args.rebuild,
        pushgateway_url=args.pushgateway_url,
        metrics_enabled=not args.no_metrics,
    )


if __name__ == "__main__":
    raise SystemExit(main())
