import hashlib
import os
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from psycopg import errors, sql

from stores.database_postgres import get_connection, persist_dataset
from stores.ingestion import prepare_dataset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    os.getenv("RUN_POSTGRES_TESTS") == "1",
    "set RUN_POSTGRES_TESTS=1 to run PostgreSQL integration tests",
)
class PostgreSQLIngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = prepare_dataset(PROJECT_ROOT / "data")

    def setUp(self) -> None:
        self.connection = get_connection()
        self.schema = f"stores_test_{uuid4().hex}"
        self.connection.execute(
            sql.SQL("CREATE SCHEMA {}").format(
                sql.Identifier(self.schema)
            )
        )
        self.connection.execute(
            sql.SQL("SET search_path TO {}").format(
                sql.Identifier(self.schema)
            )
        )

    def tearDown(self) -> None:
        self.connection.rollback()
        self.connection.close()

    def _count(self, table: str) -> int:
        return self.connection.execute(
            sql.SQL("SELECT count(*) FROM {}").format(
                sql.Identifier(table)
            )
        ).fetchone()[0]

    def test_full_load_and_idempotent_rerun(self) -> None:
        result = persist_dataset(
            self.dataset,
            rebuild=True,
            connection=self.connection,
        )
        self.assertEqual(result.documents, 1)
        expected = {
            "documents": 1,
            "chunks": 37,
            "chunks_for_arguments": 28,
            "arguments": 14,
            "entities": 28,
            "summaries": 25,
        }
        self.assertEqual(
            {table: self._count(table) for table in expected},
            expected,
        )
        original_ids = self.connection.execute(
            "SELECT id FROM chunks ORDER BY chunk_index"
        ).fetchall()

        persist_dataset(
            self.dataset,
            connection=self.connection,
        )
        self.assertEqual(
            {table: self._count(table) for table in expected},
            expected,
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT id FROM chunks ORDER BY chunk_index"
            ).fetchall(),
            original_ids,
        )

    def test_argument_chunk_delete_cascades(self) -> None:
        persist_dataset(
            self.dataset,
            rebuild=True,
            connection=self.connection,
        )
        chunk_id = self.connection.execute(
            """
            SELECT chunk_id
            FROM arguments
            ORDER BY id
            LIMIT 1
            """
        ).fetchone()[0]
        self.connection.execute(
            "DELETE FROM chunks_for_arguments WHERE id = %s",
            (chunk_id,),
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT count(*) FROM arguments WHERE chunk_id = %s",
                (chunk_id,),
            ).fetchone()[0],
            0,
        )
        self.assertEqual(
            self.connection.execute(
                "SELECT count(*) FROM entities WHERE chunk_id = %s",
                (chunk_id,),
            ).fetchone()[0],
            0,
        )

    def test_changed_passage_increments_version(self) -> None:
        persist_dataset(
            replace(self.dataset, summaries=()),
            rebuild=True,
            connection=self.connection,
        )
        original_id = self.connection.execute(
            "SELECT id FROM chunks WHERE chunk_index = 0"
        ).fetchone()[0]

        document = self.dataset.documents[0]
        first_chunk = document.chunks[0]
        changed_content = first_chunk.content + " changed"
        changed_chunk = replace(
            first_chunk,
            content=changed_content,
            content_hash=hashlib.sha256(
                changed_content.encode("utf-8")
            ).hexdigest(),
        )
        changed_document = replace(
            document,
            json_hash="0" * 64,
            chunks=(changed_chunk,) + document.chunks[1:],
        )
        changed_dataset = replace(
            self.dataset,
            documents=(changed_document,),
            summaries=(),
        )
        persist_dataset(
            changed_dataset,
            connection=self.connection,
        )

        version = self.connection.execute(
            "SELECT version FROM documents"
        ).fetchone()[0]
        changed_id = self.connection.execute(
            "SELECT id FROM chunks WHERE chunk_index = 0"
        ).fetchone()[0]
        self.assertEqual(version, 2)
        self.assertNotEqual(changed_id, original_id)

    def test_failed_replacement_rolls_back_to_savepoint(self) -> None:
        persist_dataset(
            self.dataset,
            rebuild=True,
            connection=self.connection,
        )
        document = self.dataset.documents[0]
        bad_document = replace(
            document,
            arguments=document.arguments + (document.arguments[0],),
        )
        bad_dataset = replace(
            self.dataset,
            documents=(bad_document,),
            summaries=(),
        )

        with self.assertRaises(errors.UniqueViolation):
            with self.connection.transaction():
                persist_dataset(
                    bad_dataset,
                    connection=self.connection,
                )

        self.assertEqual(self._count("arguments"), 14)


if __name__ == "__main__":
    unittest.main()
