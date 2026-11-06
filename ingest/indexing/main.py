"""Build the single summaries index and report its duration."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter


StageRunner = Callable[[], None]
Stage = tuple[str, StageRunner]


def _load_stage_runners() -> tuple[Stage, ...]:
    """Import the summaries indexer only when the pipeline is ready to run."""

    from RAG_medils.ingest.indexing.summaries.indexer_qdrant import main as index_summaries

    return (("summaries", index_summaries),)


def run_pipeline(
    stage_runners: Iterable[Stage] | None = None,
) -> dict[str, float]:
    """Run the configured indexing stages, stopping if a stage fails."""

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
