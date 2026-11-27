"""Retrieval evaluation over the benchmark questions (k = 10 by default).

Two question formats are supported:

* **facts** (current benchmark export): ``evidence`` is a list of facts, each
  with ``alternatives`` — every place that states the fact (``doc_id`` and,
  for text alternatives, the exact ``text``). Alternatives are unordered and
  equivalent: any one of them suffices.
* **legacy**: ``relevant_doc_ids`` plus ``evidence`` items with ``doc_id`` and
  ``text``.

Document metrics rank the record ids of the top-k nodes (duplicates removed,
catalog node skipped). In the facts format the relevant set is every
``doc_id`` of any alternative; Hit, MRR and nDCG use an ideal of one relevant
record at rank 1, since retrieving any one of them answers the question.

Text evidence: a fact is found when the normalized ``text`` of any of its
alternatives is a substring of the text of a top-k node, or of the source
chunks of a retrieved summary ("via sources"). Independent units
(email/event/note/task) are matched on their full rendered record.
Recall = facts found / facts; Hit = at least one fact found.
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Metrics (pure functions, binary relevance)
# ----------------------------------------------------------------------------


def hit_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    return float(any(doc in relevant for doc in ranked[:k]))


def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    return len(set(ranked[:k]) & relevant) / len(relevant)


def mrr_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    for rank, doc in enumerate(ranked[:k], start=1):
        if doc in relevant:
            return 1.0 / rank
    return 0.0


def map_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    """Average precision at k, normalized by |relevant| (ranx/trec convention)."""

    hits = 0
    total = 0.0
    for rank, doc in enumerate(ranked[:k], start=1):
        if doc in relevant:
            hits += 1
            total += hits / rank
    return total / len(relevant)


def ndcg_at_k(
    ranked: Sequence[str],
    relevant: set[str],
    k: int,
    *,
    ideal_relevant: int | None = None,
) -> float:
    """Binary nDCG. ``ideal_relevant`` caps the ideal ranking (1 = any one record suffices)."""

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, doc in enumerate(ranked[:k], start=1)
        if doc in relevant
    )
    ideal_count = min(len(relevant) if ideal_relevant is None else ideal_relevant, k)
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_count + 1))
    return min(dcg / ideal, 1.0)


def ndcg_first_hit_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    """nDCG with the ideal ranking = one relevant record at rank 1."""

    for rank, doc in enumerate(ranked[:k], start=1):
        if doc in relevant:
            return 1.0 / math.log2(rank + 1)
    return 0.0


LEGACY_DOCUMENT_METRICS: dict[str, Callable[[Sequence[str], set[str], int], float]] = {
    "hit": hit_at_k,
    "recall": recall_at_k,
    "ndcg": ndcg_at_k,
    "mrr": mrr_at_k,
    "map": map_at_k,
}
FACTS_DOCUMENT_METRICS: dict[str, Callable[[Sequence[str], set[str], int], float]] = {
    "hit": hit_at_k,
    "mrr": mrr_at_k,
    "ndcg": ndcg_first_hit_at_k,
}


def normalize_text(text: str) -> str:
    """Case-fold, drop markdown bold markers, collapse whitespace."""

    return re.sub(r"\s+", " ", text.replace("**", "")).strip().casefold()


def evidence_scores(facts: Sequence[Sequence[str]], texts: Iterable[str]) -> tuple[float, float]:
    """(recall, hit) over facts; a fact is found when any one of its texts appears."""

    haystack = [normalize_text(text) for text in texts]
    found = 0
    for alternatives in facts:
        needles = {normalize_text(text) for text in alternatives if text and text.strip()}
        if any(needle in text for needle in needles for text in haystack):
            found += 1
    return found / len(facts), float(found > 0)


def question_targets(question: dict[str, Any]) -> tuple[str, set[str], list[list[str]]]:
    """(format, relevant record ids, evidence facts as lists of alternative texts)."""

    evidence = question.get("evidence") or []
    if any(isinstance(item, dict) and "alternatives" in item for item in evidence):
        alternatives = [item.get("alternatives") or [] for item in evidence]
        relevant = {alt["doc_id"] for alts in alternatives for alt in alts if alt.get("doc_id")}
        facts = [[alt["text"] for alt in alts if alt.get("text")] for alts in alternatives]
        return "facts", relevant, [fact for fact in facts if fact]
    relevant = set(question.get("relevant_doc_ids") or [])
    facts = [[item["text"]] for item in evidence if isinstance(item, dict) and item.get("text")]
    return "legacy", relevant, facts


def ranked_dataset_ids(points: Sequence[dict[str, Any]]) -> list[str]:
    """Unique record ids in rank order; catalog nodes are skipped."""

    ranked: list[str] = []
    for point in points:
        if point.get("scope") == "catalog":
            continue
        dataset_id = point.get("dataset_id")
        if dataset_id is None:
            sources = point.get("source_dataset_ids") or []
            dataset_id = sources[0] if len(sources) == 1 else None
        if dataset_id is not None and dataset_id not in ranked:
            ranked.append(dataset_id)
    return ranked


# ----------------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------------


def score_question(
    question: dict[str, Any],
    points: Sequence[dict[str, Any]],
    *,
    k: int,
    unit_texts: dict[str, str],
    chunk_texts: dict[str, str],
) -> dict[str, Any]:
    points = list(points[:k])
    ranked = ranked_dataset_ids(points)
    question_format, relevant, facts = question_targets(question)
    row: dict[str, Any] = {
        "id": question["id"],
        "question": question["question"],
        "format": question_format,
        "retrieval_type": question.get("retrieval_type"),
        "reasoning_type": question.get("reasoning_type"),
        "answer_type": question.get("answer_type"),
        "relevant_doc_ids": sorted(relevant),
        "retrieved_doc_ids": ranked,
        "first_relevant_rank": next(
            (rank for rank, doc in enumerate(ranked, start=1) if doc in relevant), None
        ),
        "retrieved_nodes": [
            {
                "node_id": point.get("node_id"),
                "scope": point.get("scope"),
                "level": point.get("level"),
                "dataset_id": point.get("dataset_id"),
                "score": point.get("score"),
            }
            for point in points
        ],
        "catalog_retrieved": any(point.get("scope") == "catalog" for point in points),
    }
    if relevant:
        metrics = FACTS_DOCUMENT_METRICS if question_format == "facts" else LEGACY_DOCUMENT_METRICS
        for name, metric in metrics.items():
            row[f"doc_{name}@{k}"] = metric(ranked, relevant, k)

    if facts:
        own_texts: list[str] = []
        source_texts: list[str] = []
        for point in points:
            dataset_id = point.get("dataset_id")
            if point.get("level") == 0 and dataset_id in unit_texts:
                own_texts.append(unit_texts[dataset_id])
            else:
                own_texts.append(point.get("summary_text") or "")
            source_texts.extend(
                chunk_texts[chunk_id]
                for chunk_id in point.get("source_chunk_ids") or []
                if chunk_id in chunk_texts and point.get("scope") != "catalog"
            )
        row["facts"] = len(facts)
        # Headline: retrieved text plus the source chunks of retrieved summaries.
        recall, hit = evidence_scores(facts, [*own_texts, *source_texts])
        row[f"evidence_recall@{k}"] = recall
        row[f"evidence_hit@{k}"] = hit
        # Strict: only the retrieved nodes' own text.
        recall, hit = evidence_scores(facts, own_texts)
        row[f"evidence_recall_strict@{k}"] = recall
        row[f"evidence_hit_strict@{k}"] = hit
    return row


def aggregate(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    keys = sorted({key for row in rows for key in row if "@" in key})
    summary: dict[str, Any] = {"questions": len(rows)}
    for key in keys:
        values = [row[key] for row in rows if key in row]
        summary[key] = round(sum(values) / len(values), 4) if values else None
        summary[f"n_{key}"] = len(values)
    summary["catalog_retrieved_rate"] = round(
        sum(row["catalog_retrieved"] for row in rows) / len(rows), 4
    ) if rows else None
    return summary


def _breakdown(rows: Sequence[dict[str, Any]], key: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[key(row)].append(row)
    return {name: aggregate(group) for name, group in sorted(groups.items())}


def _load_unit_texts(data_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Rendered text of independent units, and record id -> record type."""

    from RAG_medils.ingest.corpus.loader import is_single_unit, load_records, render

    unit_texts: dict[str, str] = {}
    types: dict[str, str] = {}
    for record in load_records(data_dir):
        types[record["id"]] = record["type"]
        if is_single_unit(record):
            unit_texts[record["id"]] = render(record)
    return unit_texts, types


def _load_chunk_texts(tenant_id: str) -> dict[str, str]:
    from RAG_medils.ingest.stores.database_postgres import get_connection
    from RAG_medils.ingest.stores.ingestion import catalog_id_for_tenant

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT node_id, summary_text FROM summaries WHERE scope = 'passage' AND catalog_id = %s",
            (catalog_id_for_tenant(tenant_id),),
        ).fetchall()
    return dict(rows)


def run_evaluation(
    *,
    questions_path: Path,
    data_dir: Path,
    tenant_id: str,
    out_dir: Path,
    k: int = 10,
    limit: int | None = None,
    search: Callable[[str, int], Sequence[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    if search is None:
        from RAG_medils.retrieval_and_generation.retrieval.semantic_search import search_summaries
        from RAG_medils.retrieval_and_generation.workflows.rag_graph import _serialize_points

        def search(question: str, limit_: int) -> Sequence[dict[str, Any]]:
            # Verbatim question: no query rewrite, no date filters.
            return _serialize_points(search_summaries(question, limit_, tenant_id=tenant_id))

    dataset = json.loads(questions_path.read_text(encoding="utf-8"))
    questions = dataset["questions"] if isinstance(dataset, dict) else dataset
    if limit is not None:
        questions = questions[:limit]
    unit_texts, record_types = _load_unit_texts(data_dir)
    chunk_texts = _load_chunk_texts(tenant_id)
    if not chunk_texts:
        raise RuntimeError(f"no passages stored for tenant {tenant_id}; run `ingest` and `index` first")

    run_dir = out_dir / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    with (run_dir / "per_question.jsonl").open("w", encoding="utf-8") as output:
        for index, question in enumerate(questions, start=1):
            points = search(question["question"], k)
            row = score_question(question, points, k=k, unit_texts=unit_texts, chunk_texts=chunk_texts)
            rows.append(row)
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
            if index % 25 == 0 or index == len(questions):
                print(f"[evaluate] {index}/{len(questions)} questions ({time.perf_counter() - started:.0f}s)", flush=True)

    def first_relevant_type(row: dict[str, Any]) -> str:
        retrieved = [doc for doc in row["retrieved_doc_ids"] if doc in set(row["relevant_doc_ids"])]
        return record_types.get(retrieved[0], "unknown") if retrieved else "not_found"

    summary = {
        "questions_file": str(questions_path),
        "tenant_id": tenant_id,
        "k": k,
        "overall": aggregate(rows),
        "by_answer_type": _breakdown(rows, lambda row: str(row["answer_type"])),
        "by_retrieval_type": _breakdown(rows, lambda row: str(row["retrieval_type"])),
        "by_reasoning_type": _breakdown(rows, lambda row: str(row["reasoning_type"])),
        "by_first_relevant_record_type": _breakdown(rows, first_relevant_type),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print_summary(summary["overall"], k)
    print(f"[evaluate] results in {run_dir}")
    return summary


def print_summary(overall: dict[str, Any], k: int) -> None:
    labels = [
        ("Document Hit", f"doc_hit@{k}"),
        ("Document Recall", f"doc_recall@{k}"),
        ("Document nDCG", f"doc_ndcg@{k}"),
        ("Document MRR", f"doc_mrr@{k}"),
        ("Document MAP", f"doc_map@{k}"),
        ("Text Evidence Recall", f"evidence_recall@{k}"),
        ("Text Evidence Hit", f"evidence_hit@{k}"),
        ("Text Evidence Recall (strict)", f"evidence_recall_strict@{k}"),
        ("Text Evidence Hit (strict)", f"evidence_hit_strict@{k}"),
    ]
    print(f"\n{'Metric':<40}{'Value':>8}{'n':>6}")
    for label, key in labels:
        value = overall.get(key)
        if value is None:
            continue  # metric not defined for this question format
        print(f"{label + '@' + str(k):<40}{value:>8.4f}{overall.get('n_' + key, 0):>6}")
    print(f"{'Catalog node retrieved (rate)':<40}{overall.get('catalog_retrieved_rate') or 0:>8.4f}\n")
