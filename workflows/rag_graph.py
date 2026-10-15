from typing import Literal, NotRequired, TypedDict

from langgraph.graph import StateGraph, START, END

from metrics import RETRIEVAL_DURATION
from retrieval.graph_retriever import retrieve_graph
from retrieval.semantic_search import search_passages, search_summaries


RetrievalType = Literal["documents", "summaries", "graph"]
DEFAULT_RETRIEVALS: tuple[RetrievalType, ...] = (
    "documents",
    "summaries",
    "graph",
)


class RAGState(TypedDict):
    question: str
    limit: int
    retrievals: NotRequired[list[RetrievalType]]
    documents: list
    summaries: list
    graph_context: dict


def _serialize_points(points, id_field):
    serialized = []
    for point in points:
        payload = point.payload or {}
        serialized.append(
            {
                "id": payload.get(id_field, str(point.id)),
                **payload,
                "point_id": str(point.id),
                "score": point.score,
            }
        )
    return serialized


@RETRIEVAL_DURATION.labels(retrieval_type="end_to_end").time()
def retrieve(state: RAGState):
    requested = set(state.get("retrievals", DEFAULT_RETRIEVALS))

    documents = []
    summaries = []
    graph_context = {"matches": [], "records": []}

    if "documents" in requested:
        passages = search_passages(state["question"], state["limit"])
        documents = _serialize_points(passages, "document_id")

    if "summaries" in requested:
        summary_points = search_summaries(state["question"], state["limit"])
        summaries = _serialize_points(summary_points, "node_id")

    if "graph" in requested:
        graph_context = retrieve_graph(
            query=state["question"],
            limit=state["limit"],
        )

    return {
        "documents": documents,
        "summaries": summaries,
        "graph_context": graph_context,
    }

builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", END)

graph = builder.compile()
