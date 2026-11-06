import hashlib
import json
import logging
import mimetypes
import os
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from prometheus_client import make_asgi_app
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from langchain_core.messages import HumanMessage
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field, SecretStr
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from qdrant_client.models import ScoredPoint
from RAG_medils.retrieval_and_generation.retrieval.semantic_search import (
    SUMMARIES_COLLECTION, client as qdrant_client, search_summaries,
)
from qdrant_client import models
from RAG_medils.retrieval_and_generation.workflows.rag_graph import analyze_query, create_graph

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://raguser:ragpass@127.0.0.1:5433/ragdb",
)
DOCUMENT_PATH_PREFIX = Path(os.getenv(
    "DOCUMENT_PATH_PREFIX",
    Path(__file__).resolve().parent,
)).resolve()
DOCUMENT_ROOT = Path(os.getenv(
    "DOCUMENT_ROOT",
    DOCUMENT_PATH_PREFIX,
)).resolve()

APPLICATION_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id UUID PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL DEFAULT 'New chat',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        archived_at TIMESTAMPTZ
    )
    """,
    """
    ALTER TABLE conversations
    ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT NOT NULL,
        conversation_id UUID NOT NULL
            REFERENCES conversations(id) ON DELETE CASCADE,
        parent_id TEXT,
        format TEXT NOT NULL,
        content JSONB NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        PRIMARY KEY (conversation_id, id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_chat_messages_thread
    ON chat_messages(conversation_id, created_at)
    """,
)


password_hasher = PasswordHash.recommended()
# Verify a real hash even for unknown users, to avoid a fast username probe.
DUMMY_PASSWORD_HASH = password_hasher.hash(secrets.token_urlsafe(32))
bearer_scheme = HTTPBearer(auto_error=False)
login_attempts: dict[tuple[str, str], tuple[int, float]] = {}


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=200)
    password: SecretStr = Field(min_length=1, max_length=1024)


class ChatRequest(BaseModel):
    messages: list[dict] = Field(min_length=1)
    id: UUID
    limit: int = Field(default=3, ge=1, le=20)


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1, pattern=r"\S", description="Query to retrieve relevant points for.")
    limit: int = Field(default=3, ge=1, description="Maximum number of points to return.")


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    archived: bool | None = None


class ChatMessageCreate(BaseModel):
    id: str = Field(min_length=1)
    parent_id: str | None = None
    format: str = Field(min_length=1)
    content: dict


@asynccontextmanager
async def database():
    async with await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        row_factory=dict_row,
    ) as connection:
        yield connection


async def get_source_documents(document_ids: list[str], tenant_id: str):
    if not document_ids:
        return []

    async with database() as connection:
        result = await connection.execute(
            """
            SELECT id, title, doc_path AS path
            FROM documents
            WHERE id = ANY(%s::uuid[]) AND tenant_id = %s
            """,
            (document_ids, tenant_id),
        )
        rows = await result.fetchall()

    documents = {str(row["id"]): row for row in rows}
    return [
        documents[document_id]
        for document_id in document_ids
        if document_id in documents
    ]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database() as connection:
        for statement in APPLICATION_SCHEMA:
            await connection.execute(statement)
        await connection.execute(Path(__file__).with_name("auth.sql").read_text())

    # Existing and newly rebuilt collections need the same tenant payload index.
    if await run_in_threadpool(qdrant_client.collection_exists, SUMMARIES_COLLECTION):
        await run_in_threadpool(
            qdrant_client.create_payload_index,
            collection_name=SUMMARIES_COLLECTION,
            field_name="catalog_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )

    async with AsyncPostgresSaver.from_conn_string(
        DATABASE_URL
    ) as checkpointer:

        await checkpointer.setup()

        app.state.graph = create_graph(checkpointer)

        yield


app = FastAPI(title="RAG API", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())


def sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def latest_user_text(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") != "user":
            continue

        parts = message.get("parts", [])
        text = "\n".join(
            part.get("text", "")
            for part in parts
            if part.get("type") == "text"
        ).strip()

        # Also accept simple legacy text messages.
        text = text or message.get("content", "")
        if isinstance(text, str) and text.strip():
            return text.strip()

    raise ValueError("No user message found")


async def authenticate(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
):
    token_hash = hashlib.sha256(credentials.credentials.encode()).hexdigest() if credentials else ""
    async with database() as connection:
        result = await connection.execute(
            """
            SELECT u.id AS user_id, u.username, u.tenant_id
            FROM sessions s JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = %s AND s.expires_at > NOW() AND u.is_active
            """,
            (token_hash,),
        )
        user = await result.fetchone()
    if user is None:
        raise HTTPException(401, "Invalid or expired session", headers={"WWW-Authenticate": "Bearer"})
    return user


CurrentUser = Annotated[dict, Depends(authenticate)]


@app.post("/auth/login")
async def login(body: LoginRequest, request: Request):
    # Five attempts per username/client per minute, per API process.
    now = time.monotonic()
    for key, (_, started) in list(login_attempts.items()):
        if now - started >= 60:
            del login_attempts[key]
    key = (request.client.host if request.client else "", body.username)
    count, started = login_attempts.get(key, (0, now))
    if count >= 5:
        raise HTTPException(429, "Too many login attempts", headers={"Retry-After": "60"})
    login_attempts[key] = (count + 1, started)

    async with database() as connection:
        result = await connection.execute(
            "SELECT id, username, tenant_id, password_hash, is_active FROM users WHERE username = %s FOR UPDATE",
            (body.username,),
        )
        user = await result.fetchone()
        try:
            valid = await run_in_threadpool(
                password_hasher.verify, body.password.get_secret_value(),
                user["password_hash"] if user else DUMMY_PASSWORD_HASH,
            )
        except (ValueError, UnknownHashError):
            valid = False
        if not valid or not user or not user["is_active"]:
            raise HTTPException(401, "Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        await connection.execute("DELETE FROM sessions WHERE expires_at <= NOW()")
        await connection.execute(
            "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (%s, %s, NOW() + INTERVAL '8 hours')",
            (token_hash, user["id"]),
        )
    return JSONResponse(
        {"access_token": token, "token_type": "bearer", "expires_in": 28800},
        headers={"Cache-Control": "no-store"},
    )


@app.get("/auth/me")
async def me(user: CurrentUser):
    return user


@app.post("/auth/logout", status_code=204)
async def logout(user: CurrentUser, credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]):
    async with database() as connection:
        await connection.execute(
            "DELETE FROM sessions WHERE token_hash = %s",
            (hashlib.sha256(credentials.credentials.encode()).hexdigest(),),
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/retrieve", response_model=list[ScoredPoint], tags=["Evaluation"])
async def retrieve(body: RetrievalRequest, user: CurrentUser):
    """Rewrite the query, apply extracted date filters, and return ranked Qdrant points without answer generation."""
    analyzed = await analyze_query(body.query)
    return await run_in_threadpool(
        search_summaries,
        analyzed["query"],
        body.limit,
        tenant_id=user["tenant_id"],
        createdDate_greater_than=analyzed["createdDate_greater_than"],
        createdDate_less_than=analyzed["createdDate_less_than"],
    )


@app.get("/conversations")
async def list_conversations(user: CurrentUser):
    async with database() as connection:
        rows = await connection.execute(
            """
            SELECT id, title, created_at, updated_at, archived_at
            FROM conversations
            WHERE user_id = %s AND tenant_id = %s
            ORDER BY updated_at DESC
            """,
            (user["user_id"], user["tenant_id"]),
        )
        return await rows.fetchall()


@app.post("/conversations", status_code=201)
async def create_conversation(user: CurrentUser):
    conversation_id = uuid4()
    async with database() as connection:
        row = await connection.execute(
            """
            INSERT INTO conversations (id, user_id, tenant_id)
            VALUES (%s, %s, %s)
            RETURNING id, title, created_at, updated_at, archived_at
            """,
            (conversation_id, user["user_id"], user["tenant_id"]),
        )
        return await row.fetchone()


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID, user: CurrentUser):
    async with database() as connection:
        result = await connection.execute(
            """
            SELECT id, title, created_at, updated_at, archived_at
            FROM conversations
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (conversation_id, user["user_id"], user["tenant_id"]),
        )
        row = await result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return row


@app.patch("/conversations/{conversation_id}")
async def update_conversation(
    conversation_id: UUID,
    body: ConversationUpdate,
    user: CurrentUser,
):
    async with database() as connection:
        result = await connection.execute(
            """
            UPDATE conversations
            SET title = COALESCE(%s, title),
                archived_at = CASE
                    WHEN %s::boolean IS NULL THEN archived_at
                    WHEN %s::boolean THEN NOW()
                    ELSE NULL
                END,
                updated_at = NOW()
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            RETURNING id, title, created_at, updated_at, archived_at
            """,
            (
                body.title,
                body.archived,
                body.archived,
                conversation_id,
                user["user_id"],
                user["tenant_id"],
            ),
        )
        row = await result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return row


@app.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: UUID, user: CurrentUser):
    async with database() as connection:
        result = await connection.execute(
            """
            DELETE FROM conversations
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            RETURNING id
            """,
            (conversation_id, user["user_id"], user["tenant_id"]),
        )
        if await result.fetchone() is None:
            raise HTTPException(status_code=404, detail="Conversation not found")


@app.get("/conversations/{conversation_id}/messages")
async def list_chat_messages(conversation_id: UUID, user: CurrentUser):
    await get_conversation(conversation_id, user)
    async with database() as connection:
        result = await connection.execute(
            """
            SELECT message.id, message.parent_id, message.format,
                   message.content, message.created_at
            FROM chat_messages AS message
            JOIN conversations AS conversation
              ON conversation.id = message.conversation_id
            WHERE message.conversation_id = %s
              AND conversation.user_id = %s AND conversation.tenant_id = %s
            ORDER BY message.created_at, message.id
            """,
            (conversation_id, user["user_id"], user["tenant_id"]),
        )
        return await result.fetchall()


@app.get("/documents/{document_id}/content")
async def get_document_content(document_id: UUID, user: CurrentUser):
    async with database() as connection:
        result = await connection.execute(
            """
            SELECT title, doc_path AS path
            FROM documents
            WHERE id = %s AND tenant_id = %s
            """,
            (document_id, user["tenant_id"]),
        )
        document = await result.fetchone()

    if document is None or document["path"] is None:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        relative_path = Path(document["path"]).relative_to(
            DOCUMENT_PATH_PREFIX
        )
        path = (DOCUMENT_ROOT / relative_path).resolve()
        path.relative_to(DOCUMENT_ROOT)
    except ValueError:
        raise HTTPException(status_code=404, detail="Document file not found")

    if not path.is_file():
        raise HTTPException(status_code=404, detail="Document file not found")

    if path.suffix.lower() not in {".md", ".pdf"}:
        raise HTTPException(status_code=415, detail="Unsupported document type")

    return FileResponse(
        path,
        media_type=mimetypes.guess_type(path)[0],
        filename=path.name,
        content_disposition_type="inline",
    )


@app.post("/conversations/{conversation_id}/messages", status_code=201)
async def create_chat_message(
    conversation_id: UUID,
    body: ChatMessageCreate,
    user: CurrentUser,
):
    async with database() as connection:
        conversation = await connection.execute(
            """
            SELECT id FROM conversations
            WHERE id = %s AND user_id = %s AND tenant_id = %s
            """,
            (conversation_id, user["user_id"], user["tenant_id"]),
        )
        if await conversation.fetchone() is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        result = await connection.execute(
            """
            INSERT INTO chat_messages (
                id, conversation_id, parent_id, format, content
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (conversation_id, id) DO UPDATE
            SET parent_id = EXCLUDED.parent_id,
                format = EXCLUDED.format,
                content = EXCLUDED.content
            RETURNING id, parent_id, format, content, created_at
            """,
            (
                body.id,
                conversation_id,
                body.parent_id,
                body.format,
                Jsonb(body.content),
            ),
        )
        await connection.execute(
            """
            UPDATE conversations SET updated_at = NOW()
            WHERE id = %s
            """,
            (conversation_id,),
        )
        return await result.fetchone()


@app.post("/chat")
async def chat(
    body: ChatRequest,
    request: Request,
    user: CurrentUser,
):
    try:
        question = latest_user_text(body.messages)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    await get_conversation(body.id, user)
    # JSON avoids ambiguity even when tenant identifiers contain punctuation.
    thread_id = json.dumps([user["tenant_id"], user["user_id"], str(body.id)])

    graph = request.app.state.graph
    async def generate():
        message_id = str(uuid4())
        text_id = str(uuid4())
        started = False

        yield sse({
            "type": "start",
            "messageId": message_id,
        })

        try:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }

            async for mode, data in graph.astream(
                {
                    "messages": [HumanMessage(content=question)],
                    "limit": body.limit,
                    "tenant_id": user["tenant_id"],
                },
                config=config,
                stream_mode=["messages", "updates"],
            ):
                if mode == "updates":
                    summaries = data.get("retrieve", {}).get("summaries", [])
                    document_ids = list(dict.fromkeys(
                        str(document_id)
                        for summary in summaries
                        for document_id in summary.get(
                            "source_document_ids", []
                        )
                    ))[:10]

                    for document in await get_source_documents(document_ids, user["tenant_id"]):
                        path = document["path"]
                        yield sse({
                            "type": "source-document",
                            "sourceId": str(document["id"]),
                            "mediaType": (
                                mimetypes.guess_type(path)[0]
                                or "application/octet-stream"
                            ),
                            "title": document["title"],
                            "filename": os.path.basename(path),
                            "providerMetadata": {
                                "rag": {"path": path},
                            },
                        })
                    continue

                if mode != "messages":
                    continue

                chunk, metadata = data

                # Do not stream tokens from other nodes.
                if metadata.get("langgraph_node") != "generate":
                    continue

                content = chunk.content

                if not isinstance(content, str) or not content:
                    continue

                if not started:
                    yield sse({
                        "type": "text-start",
                        "id": text_id,
                    })
                    started = True

                yield sse({
                    "type": "text-delta",
                    "id": text_id,
                    "delta": content,
                })

            if not started:
                yield sse({
                    "type": "text-start",
                    "id": text_id,
                })
                yield sse({
                    "type": "text-delta",
                    "id": text_id,
                    "delta": "No response was generated.",
                })

            yield sse({
                "type": "text-end",
                "id": text_id,
            })
            yield sse({"type": "finish"})

        except Exception:
            logger.exception("Chat stream failed")
            yield sse({
                "type": "error",
                "errorText": "The generation failed.",
            })

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-ui-message-stream": "v1",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
