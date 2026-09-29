from database_postgres import add_document, get_documents, create_tables

#create_tables()

add_document(
    "PostgreSQL",
    "PostgreSQL is a relational database."
)

add_document(
    "Qdrant",
    "Qdrant is a vector database."
)

for document in get_documents():
    print(document)