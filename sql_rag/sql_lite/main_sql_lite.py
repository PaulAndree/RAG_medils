from sql_rag.sql_lite.sql_lite_database import create_tables, add_document, get_documents

create_tables()

add_document(
    "LangGraph",
    "LangGraph is a framework for building stateful AI agents."
)

add_document(
    "RAG",
    "RAG combines retrieval with language models."
)

documents = get_documents()

for document in documents:
    print(document)