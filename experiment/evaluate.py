"""Retrieval evaluation over the benchmark questions (k = 10 by default).

Document metrics rank the dataset ids of the top-k retrieved nodes:
chunks and single-document summaries map to their own record id. The single
catalog (corpus-level) node spans every document, so it is not attributable
to one id and is skipped (its retrieval rate is reported).

Text evidence: a gold ``evidence.text`` span is found when its normalized
text is a substring of a top-k node's own text. For independent units
(email/event/note/task) the full rendered record is used, since an over-limit
unit is stored as a summary. ``*_via_sources`` variants also accept a span
found in the source chunks of a retrieved summary.
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


def ndcg_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, doc in enumerate(ranked[:k], start=1)
        if doc in relevant
    )
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return dcg / ideal


DOCUMENT_METRICS: dict[str, Callable[[Sequence[str], set[str], int], float]] = {
    "hit": hit_at_k,
    "recall": recall_at_k,
    "ndcg": ndcg_at_k,
    "mrr": mrr_at_k,
    "map": map_at_k,
}


def normalize_text(text: str) -> str:
    """Case-fold, drop markdown bold markers, collapse whitespace."""

    return re.sub(r"\s+", " ", text.replace("**", "")).strip().casefold()


def evidence_scores(spans: Sequence[str], texts: Iterable[str]) -> tuple[float, float]:
    """(recall, hit) of the evidence spans within the given texts."""

    haystack = [normalize_text(text) for text in texts]
    found = sum(
        1 for span in spans if any(normalize_text(span) in text for text in haystack)
    )
    return found / len(spans), float(found > 0)


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
    relevant = set(question.get("relevant_doc_ids") or [])
    row: dict[str, Any] = {
        "id": question["id"],
        "question": question["question"],
        "retrieval_type": question.get("retrieval_type"),
        "reasoning_type": question.get("reasoning_type"),
        "relevant_doc_ids": sorted(relevant),
        "retrieved_doc_ids": ranked,
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
        for name, metric in DOCUMENT_METRICS.items():
            row[f"doc_{name}@{k}"] = metric(ranked, relevant, k)

    spans = [item["text"] for item in question.get("evidence") or [] if item.get("text")]
    if spans:
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
        recall, hit = evidence_scores(spans, own_texts)
        row[f"evidence_recall@{k}"] = recall
        row[f"evidence_hit@{k}"] = hit
        recall, hit = evidence_scores(spans, [*own_texts, *source_texts])
        row[f"evidence_recall_via_sources@{k}"] = recall
        row[f"evidence_hit_via_sources@{k}"] = hit
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

    def relevant_type(row: dict[str, Any]) -> str:
        kinds = sorted({record_types.get(doc, "unknown") for doc in row["relevant_doc_ids"]})
        return "+".join(kinds) or "none"

    summary = {
        "questions_file": str(questions_path),
        "tenant_id": tenant_id,
        "k": k,
        "overall": aggregate(rows),
        "by_retrieval_type": _breakdown(rows, lambda row: str(row["retrieval_type"])),
        "by_reasoning_type": _breakdown(rows, lambda row: str(row["reasoning_type"])),
        "by_relevant_doc_type": _breakdown(rows, relevant_type),
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
        ("Text Evidence Recall (via sources)", f"evidence_recall_via_sources@{k}"),
        ("Text Evidence Hit (via sources)", f"evidence_hit_via_sources@{k}"),
    ]
    print(f"\n{'Metric':<40}{'Value':>8}{'n':>6}")
    for label, key in labels:
        value = overall.get(key)
        shown = f"{value:.4f}" if isinstance(value, float) else "-"
        print(f"{label + '@' + str(k):<40}{shown:>8}{overall.get('n_' + key, 0):>6}")
    print(f"{'Catalog node retrieved (rate)':<40}{overall.get('catalog_retrieved_rate') or 0:>8.4f}\n")
