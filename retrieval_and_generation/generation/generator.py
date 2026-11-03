import os
from datetime import date

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11436")
GENERATION_MODEL = os.getenv("OLLAMA_GENERATION_MODEL", "qwen3:14b")


class QueryAnalysis(BaseModel):
    query: str = Field(min_length=1)
    createdDate_greater_than: date | None = Field(description="Inclusive start date, or null")
    createdDate_less_than: date | None = Field(description="Inclusive end date, or null")


async def generate_answer(state: dict, context: str):
    llm = ChatOllama(
        model=GENERATION_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )

    system = SystemMessage(content=f"""
    You are a research assistant.

    Use the conversation history to understand follow-up questions and
    references to previous messages.

    For questions about the ingested documents, ground the answer only in
    the supplied document context. If that evidence is insufficient, say so.

    Context:
    {context}
    """)

    # LangGraph's message reducer preserves history.
    messages = [system, *state["messages"]]

    response = await llm.ainvoke(messages)

    return {"messages": [response]}



async def rewrite_query(query: str):
    llm = ChatOllama(
        model=GENERATION_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    ).with_structured_output(QueryAnalysis, method="json_schema")

    system = SystemMessage(content=f"""
    Today is {date.today().isoformat()}.
    Fix grammar only if needed, preserving the query's meaning and language.
    Extract date constraints only when they refer to the createdDateTime of
    ingested documents, not dates mentioned in their subject matter.
    Return createdDate_greater_than and createdDate_less_than as YYYY-MM-DD
    dates, or null when not applicable. Both bounds include the entire day.
    For a single day, use that date for both bounds. Resolve relative dates
    using today's date. Keep the schema field names unchanged.
    """)

    response = await llm.ainvoke([system, HumanMessage(content=query)])
    return response.model_dump(mode="json")
