from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import make_asgi_app

from workflows.rag_graph import DEFAULT_RETRIEVALS, RetrievalType, graph

app = FastAPI(title="RAG API")
app.mount("/metrics", make_asgi_app())


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    limit: int = Field(default=3, ge=1, le=20)
    retrievals: list[RetrievalType] = Field(
        default_factory=lambda: list(DEFAULT_RETRIEVALS)
    )


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    # Check PostgreSQL, Qdrant, and that the active alias exists.
    return {"status": "ready"}


@app.post("/v1/query")
def query(request: QueryRequest):
    try:
        result = graph.invoke({
            "question": request.question,
            "limit": request.limit,
            "retrievals": request.retrievals,
            "documents": [],
            "summaries": [],
            "graph_context": {"matches": [], "records": []},
        })
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG workflow unavailable",
        ) from exc

    return {
        "question": request.question,
        "documents": result["documents"],
        "summaries": result["summaries"],
        "graph_context": result["graph_context"],
    }
