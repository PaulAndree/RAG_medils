from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from sql_rag.semantic_search import (
    search_documents,
    get_document,
)


class RAGState(TypedDict):
    question: str
    documents: list


def retrieve(state: RAGState):

    question = state["question"]
    results = search_documents(question)
    documents = []

    for result in results:

        document_id = result.payload["document_id"]
        document = get_document(document_id)
        documents.append(document)

    return {
        "documents": documents
    }

builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", END)

graph = builder.compile()