import psycopg
import os

def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ragdb"),
        user=os.getenv("POSTGRES_USER", "raguser"),
        password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
    )

def create_tables():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def add_document(title, content):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO documents (title, content)
        VALUES (%s, %s)
        """,
        (title, content)
    )

    conn.commit()
    conn.close()


def get_documents():
    conn = get_connection()

    cursor = conn.execute("""
        SELECT id, title, content
        FROM documents
    """)

    documents = cursor.fetchall()

    conn.close()

    return documents