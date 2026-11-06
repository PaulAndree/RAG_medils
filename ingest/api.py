"""Register uploaded documents, then process their representations automatically."""

import asyncio
import hashlib
import json
import logging
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from RAG_medils.ingest.create_table import database_connection
from RAG_medils.ingest.processing import index_summaries, process_tenant_documents, tenant_data_root
from RAG_medils.ingest.stores.database_postgres import (
    get_document,
    get_pending_tenants,
    initialize_database,
    store_document,
)
from RAG_medils.ingest.stores.ingestion import InputValidationError, prepare_document, validate_metadata


logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(initialize_database)
    tenants = await asyncio.to_thread(get_pending_tenants)
    recovery_tasks = [asyncio.create_task(process_tenant_documents(tenant)) for tenant in tenants]
    app.state.recovery_tasks = recovery_tasks
    try:
        yield
    finally:
        if recovery_tasks:
            await asyncio.gather(*recovery_tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}

# The authetication receives the APIKEY and checks if it is valid and active, returning the tenant_id and permission if valid.
def authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
):
    key_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
    with database_connection() as connection:
        row = connection.execute(
            "SELECT tenant_id, permission, is_active FROM api_keys WHERE key_hash = %s",
            (key_hash,),
        ).fetchone()
    if row is None or not row[2]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"tenant_id": row[0], "permission": row[1]}


def require_ingest_tenant(auth: Annotated[dict, Depends(authenticate)]) -> str:
    if auth["permission"] not in {"ingest", "admin"}:
        raise HTTPException(status_code=403, detail="API key does not have ingestion permission")
    return auth["tenant_id"]


def _register_upload(file: UploadFile, metadata: dict, tenant_id: str):
    document_id = uuid4()
    filename = Path((file.filename or "").replace("\\", "/")).name
    if Path(filename).suffix.lower() not in {".pdf", ".md"}:
        raise InputValidationError("only PDF and Markdown files are supported")
    # create a directory under the tenant's data root for this document, and copy the file there
    directory = tenant_data_root(tenant_id) / "documents" / str(document_id)
    directory.mkdir(parents=True, exist_ok=False)
    try:
        location = directory / filename
        with location.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
        document = prepare_document(
            location, metadata, tenant_id=tenant_id, document_id=document_id,
        )
        # store_document returns only after its connection has committed.
        # If a document already exists with both the same tenant_id and the same doc_hash, PostgreSQL skips the insert.
        result = store_document(document)
    except Exception:
        shutil.rmtree(directory)
        raise
    if not result.created:
        shutil.rmtree(directory)
    return result


@app.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingestion(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    tenant_id: Annotated[str, Depends(require_ingest_tenant)],
    metadata: Annotated[str | None, Form()] = None,
):
    try:
        values = validate_metadata(json.loads(metadata) if metadata is not None else {})
        #guardamos docs en local y Postgresql
        result = await asyncio.to_thread(_register_upload, file, values, tenant_id)
    except (json.JSONDecodeError, InputValidationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Document registration failed for tenant %s", tenant_id)
        raise HTTPException(status_code=500, detail="Document registration failed") from exc
    finally:
        await file.close()

    if not result.has_summary:
        # process_tenant_documents se conecta con OCR y representation summaries, se ejecuta en segundo plano
        # se procesa una por una, para no bloquear el bucle de eventos de FastAPI (read postgreSQL)
        background_tasks.add_task(process_tenant_documents, tenant_id)

    if result.has_summary:
        # Summaries are already committed; run indexing after the response from _process_tenant_documents()
        background_tasks.add_task(index_summaries)
    return JSONResponse(
        status_code=200 if result.has_summary else 202,
        content={
            "document_id": str(result.document_id),
            "tenant_id": result.tenant_id,
            "has_summary": result.has_summary,
        },
    )


@app.get("/ingest/{document_id}")
def ingestion_status(document_id: UUID, auth: Annotated[dict, Depends(authenticate)]):
    document = get_document(document_id, auth["tenant_id"])
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "document_id": str(document["id"]),
        "tenant_id": document["tenant_id"],
        "has_summary": document["has_summary"],
    }
