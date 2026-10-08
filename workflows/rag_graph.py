from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from retrieval.semantic_search import (
    search_documents,
    get_document,
)


class RAGState(TypedDict):
    question: str
    limit: int
    documents: list


def retrieve(state: RAGState):
    results = search_documents(
        question=state["question"],
        limit=state["limit"],
    )

    documents = [
        {
            "id": point.payload["document_id"],
            "doc_name": point.payload["doc_name"],
            "title": point.payload["title"],
            "content": point.payload.get("content"),
            "score": point.score,
        }
        for point in results
    ]

    return {"documents": documents}

builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", END)

graph = builder.compile()