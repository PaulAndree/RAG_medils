"""Automatically build, store, and index representations of registered documents."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import threading
from pathlib import Path

import httpx

from RAG_medils.ingest import RAG_ROOT
from RAG_medils.ingest.representations.common import DocumentInput
from RAG_medils.ingest.stores.database_postgres import get_tenant_documents, store_summaries
from RAG_medils.ingest.stores.ingestion import catalog_id_for_tenant, prepare_summaries


logger = logging.getLogger(__name__)
_tenant_locks: dict[str, asyncio.Lock] = {}
_indexing_lock = threading.Lock()


def index_summaries() -> None:
    """Run the shared index in a background thread after summaries are committed."""
    try:
        # All tenants share the live Qdrant alias. Serialize API-triggered rebuilds.
        with _indexing_lock:
            from RAG_medils.ingest.indexing.main import run_pipeline

            run_pipeline()
    except Exception:
        logger.exception(
            "Summary indexing failed; stored summaries are preserved. "
            "Reupload an existing document to retry indexing."
        )


def tenant_data_root(tenant_id: str) -> Path:
    root = Path(os.getenv("INGEST_DATA_ROOT", str(RAG_ROOT / "ingest" / "data"))).resolve()
    # Tenant names are database values, never filesystem paths.
    tenant_key = hashlib.sha256(tenant_id.encode("utf-8")).hexdigest()
    return root / "tenants" / tenant_key


def _prepare_markdown(document: dict, data_root: Path) -> Path:
    markdown_root = data_root / "pdf_parsed_output"
    markdown_path = (markdown_root / f"{document['source_key']}.md").resolve()
    if not markdown_path.is_relative_to(markdown_root.resolve()):
        raise ValueError("document source_key escapes the Markdown directory")
    if markdown_path.is_file() and markdown_path.stat().st_size:
        return markdown_path

    original = Path(document["doc_path"])
    if original.suffix.lower() == ".pdf":
        with httpx.Client(timeout=1000) as client, original.open("rb") as pdf:
            response = client.post(
                os.getenv("OCR_URL", "http://127.0.0.1:8084/services/ocr"),
                files={"file": (original.name, pdf, "application/pdf")},
                data={"type_name": "pdf"},
            )
            response.raise_for_status()
            content = response.json()["content_parsed"]
    elif original.suffix.lower() == ".md":
        content = original.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported original file: {original}")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("parsed document must contain text")
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = markdown_path.with_suffix(".md.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(markdown_path)
    return markdown_path


def _process_tenant_documents(tenant_id: str) -> None:
    documents = get_tenant_documents(tenant_id)
    if not any(not document["has_summary"] for document in documents):
        return
    data_root = tenant_data_root(tenant_id)
    inputs = [
        DocumentInput(
            id=document["id"],
            source_key=document["source_key"],
            markdown_path=_prepare_markdown(document, data_root),
            catalog_id=catalog_id_for_tenant(tenant_id),
            title=document["title"],
            has_summary=document["has_summary"],
        )
        for document in documents
    ]
    # Import the model pipeline only in the background, after registration.
    from RAG_medils.ingest.representations.main import run_pipeline

    run_pipeline(data_root, registered_documents=inputs)
    summaries = prepare_summaries(data_root / "summaries")
    store_summaries(summaries, tenant_id=tenant_id)
    logger.info("Stored representations for %d documents in tenant %s", len(inputs), tenant_id)
    index_summaries()


async def process_tenant_documents(tenant_id: str) -> None:
    """Serialize one tenant's work without blocking the API event loop.

    The service runs with one API worker. Waiting tasks re-read PostgreSQL
    after acquiring the lock, including uploads committed during earlier work.
    """
    lock = _tenant_locks.setdefault(tenant_id, asyncio.Lock())
    async with lock:
        # Shield the thread and wait on cancellation so a restart cannot leave
        # an abandoned worker writing files after the tenant lock is released.
        task = asyncio.create_task(asyncio.to_thread(_process_tenant_documents, tenant_id))
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError:
            await task
            raise
        except Exception:
            logger.exception(
                "Document processing failed for tenant %s; unfinished documents remain pending",
                tenant_id,
            )
