from prometheus_client import start_http_server

from rag_graph import graph


start_http_server(8008)

print("RAG chatbot started")
print("Type 'exit' to quit\n")


while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    result = graph.invoke({
        "question": question,
        "documents": [],
    })

    print("\nRetrieved documents:")

    for document in result["documents"]:
        print(document)

    print()