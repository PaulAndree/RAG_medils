import sqlite3

DB = "app.db"


def get_connection():
    return sqlite3.connect(DB)


def create_tables():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_document(title, content):
    conn = get_connection()

    conn.execute(
        "INSERT INTO documents (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()


def get_documents():
    conn = get_connection()

    cursor = conn.execute(
        "SELECT id, title, content FROM documents"
    )

    documents = cursor.fetchall()
    conn.close()

    return documents

def update_documents(id, title):
    conn = get_connection()

    conn.execute(
        "UPDATE documents SET title = ? WHERE id = ?",
        (title, id)
    )

    conn.commit()
    conn.close()

response = sqlite3.connect(DB).execute("SELECT * FROM documents WHERE title = ?", ("LangGraph",)).fetchall()
print(response)