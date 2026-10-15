"""Run all index builders sequentially and report their durations."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter


StageRunner = Callable[[], None]
Stage = tuple[str, StageRunner]


def _load_stage_runners() -> tuple[Stage, ...]:
    """Import indexers only when the pipeline is ready to run."""

    from indexing.arguments.indexer_qdrant import main as index_arguments
    from indexing.graph.indexer_neo4j import main as index_graph
    from indexing.passages.indexer_qdrant import main as index_passages
    from indexing.summaries.indexer_qdrant import main as index_summaries

    return (
        ("passages", index_passages),
        ("arguments", index_arguments),
        ("summaries", index_summaries),
        ("graph", index_graph),
    )


def run_pipeline(
    stage_runners: Iterable[Stage] | None = None,
) -> dict[str, float]:
    """Run every indexer in order, stopping if any stage fails."""

    runners = (
        tuple(stage_runners)
        if stage_runners is not None
        else _load_stage_runners()
    )
    pipeline_started = perf_counter()
    durations: dict[str, float] = {}

    for stage, runner in runners:
        print(f"[indexing] starting {stage}")
        stage_started = perf_counter()
        try:
            runner()
        except Exception:
            elapsed = perf_counter() - stage_started
            print(f"[indexing] failed {stage} after {elapsed:.2f}s")
            raise

        elapsed = perf_counter() - stage_started
        durations[stage] = elapsed
        print(f"[indexing] completed {stage} in {elapsed:.2f}s")

    elapsed = perf_counter() - pipeline_started
    print(f"[indexing] pipeline complete in {elapsed:.2f}s")
    return durations


def main() -> int:
    run_pipeline()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
