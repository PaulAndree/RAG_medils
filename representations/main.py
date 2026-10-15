"""Run all representation builders in order and record their durations."""

from __future__ import annotations

import argparse
import os
import shutil
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from metrics import ProcessMetricSample, push_process_metrics
from representations.common import StageResult


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = PROJECT_ROOT / "data"
DEFAULT_PUSHGATEWAY_URL = os.getenv(
    "PUSHGATEWAY_URL",
    "http://localhost:9091",
)
GENERATED_PATHS = (
    Path("pdf_parsed_output"),
    Path("passages_chunk"),
    Path("arguments/chunks_for_arguments"),
    Path("arguments/arguments_extracted"),
    Path("summaries"),
    Path("entities"),
)


def _load_stage_runners(*, skip_existing: bool):
    from representations.arguments.extractor import run as run_arguments
    from representations.graph.extractor import run as run_graph
    from representations.passages.builder import run as run_passages
    from representations.summaries.builder import run as run_summaries

    return (
        (
            "passages",
            lambda data_root: run_passages(
                data_root,
                skip_existing=skip_existing,
            ),
        ),
        (
            "arguments",
            lambda data_root: run_arguments(
                data_root,
                skip_existing=skip_existing,
            ),
        ),
        (
            "summaries",
            lambda data_root: run_summaries(
                data_root,
                skip_existing=skip_existing,
            ),
        ),
        (
            "graph",
            lambda data_root: run_graph(
                data_root,
                skip_existing=skip_existing,
            ),
        ),
    )


def clean_generated_outputs(data_root: Path) -> None:
    """Remove only the explicit generated-output allowlist."""

    data_root = data_root.resolve()
    targets: list[Path] = []
    for relative_path in GENERATED_PATHS:
        unresolved = data_root
        for part in relative_path.parts:
            unresolved /= part
            if unresolved.is_symlink():
                raise RuntimeError(
                    f"Refusing to clean generated path through symlink: "
                    f"{unresolved}"
                )
        target = unresolved.resolve()
        if target == data_root or not target.is_relative_to(data_root):
            raise RuntimeError(f"Refusing to clean unsafe path: {target}")
        if target.exists() and not target.is_dir():
            raise RuntimeError(
                f"Generated output path is not a directory: {target}"
            )
        targets.append(target)

    for target in targets:
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def run_pipeline(
    data_root: Path,
    *,
    pushgateway_url: str = DEFAULT_PUSHGATEWAY_URL,
    metrics_enabled: bool = True,
    clean: bool = False,
    stage_runners=None,
) -> list[StageResult]:
    """Run every builder, resuming existing outputs unless ``clean`` is set."""

    data_root = data_root.resolve()
    runners = (
        tuple(stage_runners)
        if stage_runners is not None
        else _load_stage_runners(skip_existing=not clean)
    )
    if clean:
        clean_generated_outputs(data_root)
        print("[pipeline] cleaned generated representation directories")
    else:
        print("[pipeline] resume mode: keeping existing representations")

    pipeline_started = perf_counter()
    results: list[StageResult] = []
    for stage, runner in runners:
        print(f"[pipeline] starting {stage}")
        stage_started = perf_counter()
        result = runner(data_root)
        elapsed = perf_counter() - stage_started
        result = replace(result, duration_seconds=elapsed)
        results.append(result)
        print(f"[pipeline] completed {stage} in {elapsed:.2f}s")

    elapsed = perf_counter() - pipeline_started
    if metrics_enabled:
        try:
            push_process_metrics(
                process="representation",
                samples=[
                    ProcessMetricSample(
                        representation=result.stage,
                        document_count=result.counts.get("documents", 0),
                        item_counts={
                            item_type: count
                            for item_type, count in result.counts.items()
                            if item_type != "documents"
                        },
                        duration_seconds=result.duration_seconds,
                    )
                    for result in results
                ],
                pushgateway_url=pushgateway_url,
                job="representation_builder",
            )
        except Exception as exc:
            print(f"[pipeline] warning: could not publish metrics: {exc}")

    print(f"[pipeline] complete in {elapsed:.2f}s")
    return results


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build passages, arguments, summaries, and graph data.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help=f"Corpus root (default: {DEFAULT_DATA_ROOT})",
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--resume",
        dest="clean",
        action="store_false",
        help=(
            "Keep completed representations and build only missing ones "
            "(default)."
        ),
    )
    mode.add_argument(
        "--clean",
        action="store_true",
        help="Delete generated representations before rebuilding everything.",
    )
    parser.set_defaults(clean=False)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    run_pipeline(
        args.data_dir,
        pushgateway_url=args.pushgateway_url,
        metrics_enabled=not args.no_metrics,
        clean=args.clean,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
