"""Resumable ingestion of the JSON corpus into PostgreSQL.

Reuses the RAPTOR builder per document and checkpoints each finished document
to ``<work_dir>/nodes/<record id>.json``. A crashed or interrupted run resumes
from the checkpoints. The catalog (corpus-level) summary is built once at the
end, then the whole tenant catalog is stored atomically.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid5

from psycopg.types.json import Jsonb

from RAG_medils.ingest import RAG_ROOT
from RAG_medils.ingest.corpus.loader import document_metadata, is_single_unit, load_records, render
from RAG_medils.ingest.representations.common import DocumentInput
from RAG_medils.ingest.stores.database_postgres import get_connection, initialize_database, store_document, store_summaries
from RAG_medils.ingest.stores.ingestion import (
    DOCUMENT_NAMESPACE,
    PreparedDocument,
    catalog_id_for_tenant,
    prepare_summaries,
)

DEFAULT_WORK_DIR = RAG_ROOT / "ingest" / "data" / "company_benchmark"


@dataclass(frozen=True, slots=True)
class CorpusDocument:
    record: dict[str, Any]
    document_id: UUID
    markdown_path: Path
    text_hash: str
    single_unit: bool

    @property
    def dataset_id(self) -> str:
        return self.record["id"]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def document_uuid(tenant_id: str, dataset_id: str) -> UUID:
    return uuid5(DOCUMENT_NAMESPACE, f"{tenant_id}/{dataset_id}")


def clean(tenant_id: str, work_dir: Path) -> None:
    """Remove this tenant's documents, summaries and generated files."""

    catalog_id = catalog_id_for_tenant(tenant_id)
    with get_connection() as conn, conn.transaction():
        conn.execute("DELETE FROM summaries WHERE catalog_id = %s", (catalog_id,))
        conn.execute("DELETE FROM documents WHERE tenant_id = %s", (tenant_id,))
    for name in ("nodes", "summaries", "pdf_parsed_output", "catalog.json"):
        target = work_dir / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    print(f"[ingest] cleaned tenant {tenant_id} and {work_dir}")


def render_and_register(
    records: list[dict[str, Any]],
    *,
    tenant_id: str,
    work_dir: Path,
) -> list[CorpusDocument]:
    """Write each record's text to Markdown and register it in PostgreSQL."""

    markdown_dir = work_dir / "pdf_parsed_output"
    documents: list[CorpusDocument] = []
    with get_connection() as conn:
        for record in records:
            text = render(record)
            path = (markdown_dir / f"{record['id']}.md").resolve()
            if not path.is_relative_to(markdown_dir.resolve()):
                raise ValueError(f"record id escapes the work directory: {record['id']}")
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                _atomic_write(path, text)
            document = CorpusDocument(
                record=record,
                document_id=document_uuid(tenant_id, record["id"]),
                markdown_path=path,
                text_hash=_sha256(text),
                single_unit=is_single_unit(record),
            )
            metadata = document_metadata(record)
            registration = store_document(
                PreparedDocument(
                    id=document.document_id,
                    source_key=record["id"],
                    name=path.name,
                    title=metadata["title"],
                    doc_path=str(path),
                    language=record.get("language"),
                    # Identity is the record id, so re-renders keep the same row.
                    doc_hash=_sha256(f"{tenant_id}:{record['id']}"),
                    metadata=metadata,
                    tenant_id=tenant_id,
                ),
                connection=conn,
            )
            if registration.document_id != document.document_id:
                raise RuntimeError(
                    f"{record['id']}: registered under unexpected id {registration.document_id}"
                )
            if not registration.created:
                conn.execute(
                    "UPDATE documents SET title = %s, doc_path = %s, language = %s, metadata = %s WHERE id = %s",
                    (metadata["title"], str(path), record.get("language"), Jsonb(metadata), document.document_id),
                )
            documents.append(document)
        conn.commit()
    print(f"[ingest] rendered and registered {len(documents)} records")
    return documents


def _checkpoint_path(work_dir: Path, dataset_id: str) -> Path:
    return work_dir / "nodes" / f"{dataset_id}.json"


def _load_checkpoint(work_dir: Path, document: CorpusDocument) -> dict[str, Any] | None:
    path = _checkpoint_path(work_dir, document.dataset_id)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if data.get("text_hash") != document.text_hash or data.get("single_unit") != document.single_unit:
        return None  # source text or strategy changed: rebuild
    if any(
        not isinstance(node.get("text"), str) or not node["text"].strip()
        for nodes in data.get("levels", {}).values()
        for node in nodes
    ):
        print(f"[ingest] {document.dataset_id}: checkpoint has a blank node; rebuilding")
        return None
    return data


def build_one(document: CorpusDocument, *, catalog_id: str, work_dir: Path) -> dict[str, Any]:
    """Build one document's nodes with the existing RAPTOR functions."""

    from RAG_medils.ingest.representations.summaries import builder

    [loaded] = builder.load_documents(
        document.markdown_path.parent,
        registered_documents=[
            DocumentInput(
                id=document.document_id,
                source_key=document.dataset_id,
                markdown_path=document.markdown_path,
                catalog_id=catalog_id,
                title=document.record.get("title") or document.dataset_id,
                single_unit=document.single_unit,
            )
        ],
    )
    if document.single_unit:
        levels = {0: builder.load_document_nodes(loaded)}
        document_summary = None
    else:
        levels, document_summary = builder.build_document(loaded)
    checkpoint = {
        "dataset_id": document.dataset_id,
        "document_id": str(document.document_id),
        "text_hash": document.text_hash,
        "single_unit": document.single_unit,
        "levels": {
            str(level): [builder.clean_node(node) for node in nodes]
            for level, nodes in sorted(levels.items())
        },
        "document_summary_id": document_summary["node_id"] if document_summary else None,
        # Kept so the catalog summary does not need to re-embed every document.
        "document_summary_embedding": document_summary["embedding"] if document_summary else None,
    }
    _atomic_write(
        _checkpoint_path(work_dir, document.dataset_id),
        json.dumps(checkpoint, ensure_ascii=False),
    )
    return checkpoint


def build_documents(
    documents: list[CorpusDocument],
    *,
    catalog_id: str,
    work_dir: Path,
    workers: int,
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    checkpoints: list[dict[str, Any]] = []
    pending: list[CorpusDocument] = []
    for document in documents:
        checkpoint = _load_checkpoint(work_dir, document)
        if checkpoint is None:
            pending.append(document)
        else:
            checkpoints.append(checkpoint)
    print(f"[ingest] {len(checkpoints)} documents reused from checkpoints, {len(pending)} to build")

    failures: list[tuple[str, str]] = []
    started = time.perf_counter()
    done = 0
    # Cheap single units first, so progress and ETA become meaningful early.
    pending.sort(key=lambda document: (not document.single_unit, document.dataset_id))
    with ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix="corpus-doc") as executor:
        futures = {
            executor.submit(build_one, document, catalog_id=catalog_id, work_dir=work_dir): document
            for document in pending
        }
        for future in as_completed(futures):
            document = futures[future]
            done += 1
            try:
                checkpoints.append(future.result())
                status = "ok"
            except Exception as exc:  # keep going; failed documents are reported
                failures.append((document.dataset_id, f"{type(exc).__name__}: {exc}"))
                status = f"FAILED ({type(exc).__name__}: {exc})"
            elapsed = time.perf_counter() - started
            eta = elapsed / done * (len(pending) - done)
            print(
                f"[ingest] {done}/{len(pending)} {document.dataset_id} {status} "
                f"| elapsed {elapsed / 60:.1f} min | eta {eta / 60:.1f} min",
                flush=True,
            )
    return checkpoints, failures


def build_catalog(
    checkpoints: list[dict[str, Any]],
    *,
    catalog_id: str,
    work_dir: Path,
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any] | None]:
    """Merge document levels and add the corpus-level catalog summary."""

    from RAG_medils.ingest.representations.summaries import builder

    levels: dict[int, list[dict[str, Any]]] = defaultdict(list)
    document_summaries: list[dict[str, Any]] = []
    for checkpoint in sorted(checkpoints, key=lambda item: item["dataset_id"]):
        for level, nodes in checkpoint["levels"].items():
            levels[int(level)].extend(nodes)
            for node in nodes:
                if node["node_id"] == checkpoint["document_summary_id"]:
                    document_summaries.append(
                        {**node, "embedding": checkpoint["document_summary_embedding"]}
                    )
    if not document_summaries:
        return levels, None

    catalog_level = max(levels) + 1
    identity = _sha256(json.dumps(
        [catalog_level, *[(node["node_id"], _sha256(node["text"])) for node in document_summaries]]
    ))
    cache_path = work_dir / "catalog.json"
    if cache_path.is_file():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("identity") == identity:
            print("[ingest] reusing catalog summary")
            levels[catalog_level].append(cached["node"])
            return levels, cached["node"]

    print(f"[ingest] building catalog summary over {len(document_summaries)} document summaries")
    catalog = builder.clean_node(builder.build_catalog_summary(
        catalog_id=catalog_id,
        document_summaries=document_summaries,
        level=catalog_level,
    ))
    _atomic_write(cache_path, json.dumps({"identity": identity, "node": catalog}, ensure_ascii=False))
    levels[catalog_level].append(catalog)
    return levels, catalog


def run_ingest(
    *,
    data_dir: Path,
    tenant_id: str,
    work_dir: Path = DEFAULT_WORK_DIR,
    types: list[str] | None = None,
    limit: int | None = None,
    clean_first: bool = False,
    workers: int | None = None,
) -> int:
    from RAG_medils.ingest.representations.summaries import builder

    started = time.perf_counter()
    work_dir = work_dir.resolve()
    initialize_database()
    if clean_first:
        clean(tenant_id, work_dir)
    catalog_id = catalog_id_for_tenant(tenant_id)

    records = load_records(data_dir, types=types, limit=limit)
    print(f"[ingest] loaded {len(records)} records from {data_dir}")
    documents = render_and_register(records, tenant_id=tenant_id, work_dir=work_dir)
    checkpoints, failures = build_documents(
        documents,
        catalog_id=catalog_id,
        work_dir=work_dir,
        workers=workers or builder.RAPTOR_MAX_WORKERS,
    )
    if not checkpoints:
        print("[ingest] no document was built; nothing to store")
        return 1

    levels, _ = build_catalog(checkpoints, catalog_id=catalog_id, work_dir=work_dir)
    summaries_dir = work_dir / "summaries"
    builder.save_levels(levels, summaries_dir)
    summaries = prepare_summaries(summaries_dir)
    result = store_summaries(summaries, tenant_id=tenant_id)
    print(
        f"[ingest] stored {result.summaries} nodes for {result.documents} documents "
        f"in {(time.perf_counter() - started) / 60:.1f} min"
    )
    if failures:
        failures_path = work_dir / "failures.json"
        _atomic_write(failures_path, json.dumps(failures, ensure_ascii=False, indent=2))
        print(f"[ingest] WARNING: {len(failures)} documents failed; see {failures_path}. Rerun to retry them.")
    return 0
