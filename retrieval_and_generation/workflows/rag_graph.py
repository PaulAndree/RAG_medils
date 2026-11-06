from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from RAG_medils.retrieval_and_generation.retrieval.semantic_search import search_summaries
from RAG_medils.retrieval_and_generation.generation.generator import generate_answer, rewrite_query


class RAGState(TypedDict):
    limit: int
    tenant_id: str
    summaries: list
    messages: Annotated[list[AnyMessage], add_messages]


def _serialize_points(points):
    serialized = []
    for point in points:
        payload = point.payload or {}
        serialized.append(
            {
                "id": payload.get("node_id", str(point.id)),
                **payload,
                "point_id": str(point.id),
                "score": point.score,
            }
        )
    return serialized

def create_graph(checkpointer):
    return builder.compile(
        checkpointer=checkpointer
    )

async def analyze_query(question:str):
    # Query rewritting and date filtering if exists
    query_analyzed = await rewrite_query(question)
    
    return query_analyzed
async def retrieve(state: RAGState):
    query_analyzed  = await analyze_query(state["messages"][-1].content)
    question = query_analyzed["query"]
    createdDate_greater_than = query_analyzed["createdDate_greater_than"]
    createdDate_less_than = query_analyzed["createdDate_less_than"]

    summary_points = search_summaries(
        question,
        state["limit"],
        tenant_id=state["tenant_id"],
        createdDate_greater_than=createdDate_greater_than,
        createdDate_less_than=createdDate_less_than,
    )

    return {
        "summaries": _serialize_points(summary_points),
    }

async def generate(state: RAGState):
    context = "\n\n".join(
        f"summary_text: {summary['summary_text']}\n"
        f"createdDateTime: {summary.get('createdDateTime') or 'Unknown'}\n"
        f"title_document: {summary.get('title') or 'Untitled'}\n"
        f"doc_author: {summary.get('doc_author') or 'Unknown'}\n"
        for summary in state["summaries"]
    )
    return await generate_answer(state, context)


builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
