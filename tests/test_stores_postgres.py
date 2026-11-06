import os
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from uuid import UUID, uuid4

from psycopg import sql

from RAG_medils.ingest.stores.database_postgres import (
    get_connection, initialize_database,
    store_document, store_summaries,
)
from RAG_medils.ingest.stores.ingestion import InputValidationError, prepare_document, prepare_summaries
from tests.test_stores_raptor import write_raptor_fixture


@unittest.skipUnless(os.getenv("RUN_POSTGRES_TESTS") == "1", "set RUN_POSTGRES_TESTS=1")
class PostgreSQLIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.connection = get_connection()
        self.addCleanup(self.connection.close)
        self.addCleanup(self.connection.rollback)
        self.schema = f"stores_test_{uuid4().hex}"
        self.connection.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.connection.execute(sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema)))
        initialize_database(self.connection)

    def fixture(self, tenant="company", name="paper"):
        root = self.root / name
        document_id = write_raptor_fixture(root, source_key=name, catalog_id=f"tenant:{tenant}")
        document = prepare_document(
            root / "pdf_parsed_output" / f"{name}.md",
            {"title": "Uploaded title", "repository_id": "repo", "nested": {"x": 1}},
            tenant_id=tenant, document_id=UUID(document_id), source_key=name,
        )
        return document, prepare_summaries(root / "summaries")

    def stored(self, document_id):
        return self.connection.execute(
            "SELECT has_summary, metadata, doc_path, index_status FROM documents WHERE id = %s", (document_id,),
        ).fetchone()

    def test_document_can_be_stored_before_any_summaries(self):
        document, _ = self.fixture()
        registration = store_document(document, connection=self.connection)
        self.assertTrue(registration.created)
        self.assertFalse(self.stored(document.id)[0])
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 0)

    def test_success_and_rerun_preserve_document_metadata(self):
        document, summaries = self.fixture()
        store_document(document, connection=self.connection)
        result = store_summaries(summaries, tenant_id="company", connection=self.connection)
        self.assertEqual((result.documents, result.summaries), (1, 3))
        store_summaries(summaries, connection=self.connection)
        stored = self.stored(document.id)
        self.assertTrue(stored[0])
        self.assertEqual(stored[1], document.metadata)
        self.assertEqual(stored[2], document.doc_path)
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 3)
        self.assertEqual(
            self.connection.execute('SELECT "createdDateTime", "modifiedDateTime" FROM summaries').fetchall(),
            [(None, None)] * 3,
        )

    def test_document_dates_are_copied_to_all_non_catalog_levels(self):
        document, nodes = self.fixture()
        document = replace(document, metadata={
            **document.metadata,
            "createdDateTime": "2026-10-28T12:30:00+02:00",
            "modifiedDateTime": "2026-10-29T14:30:00Z",
        })
        passage, doc_summary, catalog = nodes
        cluster = replace(doc_summary, node_id="cluster", scope="document_cluster")
        doc_summary = replace(doc_summary, level=2, source_node_ids=(cluster.node_id,))
        catalog = replace(catalog, level=3)
        summaries = (passage, cluster, doc_summary, catalog)
        store_document(document, connection=self.connection)
        expected_dates = (datetime.fromisoformat("2026-10-28T10:30:00Z"),
                          datetime.fromisoformat("2026-10-29T14:30:00Z"))
        for _ in range(2):
            store_summaries(summaries, connection=self.connection)
            self.assertEqual(
                self.connection.execute(
                    'SELECT scope, "createdDateTime", "modifiedDateTime" FROM summaries ORDER BY level'
                ).fetchall(),
                [(scope, *expected_dates) for scope in ("passage", "document_cluster", "document")]
                + [("catalog", None, None)],
            )
        self.assertEqual(self.stored(document.id)[1], document.metadata)

    def test_hash_deduplication_preserves_original_metadata_and_completion(self):
        document, summaries = self.fixture()
        store_document(document, connection=self.connection)
        store_summaries(summaries, connection=self.connection)
        duplicate = replace(document, id=uuid4(), source_key="duplicate", metadata={"title": "replacement"})
        result = store_document(duplicate, connection=self.connection)
        self.assertFalse(result.created)
        self.assertTrue(result.has_summary)
        self.assertEqual(result.document_id, document.id)
        self.assertEqual(self.stored(document.id)[1], document.metadata)
        different_tenant = replace(duplicate, tenant_id="another")
        self.assertTrue(store_document(different_tenant, connection=self.connection).created)

    def test_other_tenant_summaries_survive_replacement(self):
        document, summaries = self.fixture()
        other, other_summaries = self.fixture("other", "other-paper")
        for doc, nodes in ((document, summaries), (other, other_summaries)):
            store_document(doc, connection=self.connection)
            store_summaries(nodes, connection=self.connection)
        store_summaries(summaries, connection=self.connection)
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 6)
        self.assertTrue(self.stored(other.id)[0])

    def test_wrong_tenant_and_unregistered_references_are_rejected(self):
        document, summaries = self.fixture()
        with self.assertRaises(InputValidationError):
            store_summaries(summaries, connection=self.connection)
        store_document(document, connection=self.connection)
        with self.assertRaisesRegex(InputValidationError, "outside"):
            store_summaries(summaries, tenant_id="another", connection=self.connection)
        self.assertFalse(self.stored(document.id)[0])

    def test_failed_inserts_roll_back_deletion_and_completion(self):
        document, summaries = self.fixture()
        store_document(document, connection=self.connection)
        from RAG_medils.ingest.stores.database_postgres import _insert_summaries
        def fail_after_insert(conn, nodes):
            _insert_summaries(conn, nodes)
            raise RuntimeError("simulated failure after insert")
        with patch("stores.database_postgres._insert_summaries", side_effect=fail_after_insert):
            with self.assertRaises(RuntimeError):
                store_summaries(summaries, connection=self.connection)
        self.assertFalse(self.stored(document.id)[0])
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 0)
        store_summaries(summaries, connection=self.connection)
        with patch("stores.database_postgres._insert_summaries", side_effect=fail_after_insert):
            with self.assertRaises(RuntimeError):
                store_summaries(summaries, connection=self.connection)
        self.assertTrue(self.stored(document.id)[0])
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 3)

    def test_incomplete_catalog_cannot_remove_other_documents(self):
        document, summaries = self.fixture()
        other, other_summaries = self.fixture("company", "second-paper")
        other = replace(other, doc_hash="0" * 64)
        for doc in (document, other):
            store_document(doc, connection=self.connection)
        root = replace(summaries[-1],
            source_node_ids=(summaries[1].node_id, other_summaries[1].node_id),
            source_chunk_ids=(summaries[0].node_id, other_summaries[0].node_id),
            source_document_ids=(str(document.id), str(other.id)),
        )
        store_summaries(summaries[:2] + other_summaries[:2] + (root,), connection=self.connection)
        with self.assertRaisesRegex(InputValidationError, "all existing documents"):
            store_summaries(summaries, connection=self.connection)
        self.assertEqual(self.connection.execute("SELECT count(*) FROM summaries").fetchone()[0], 5)

    def test_repeated_initialization_preserves_documents_and_summaries(self):
        document, summaries = self.fixture()
        store_document(document, connection=self.connection)
        store_summaries(summaries, connection=self.connection)
        pending = replace(document, id=uuid4(), source_key="pending", doc_hash="0" * 64)
        store_document(pending, connection=self.connection)
        documents_before = self.connection.execute("SELECT * FROM documents ORDER BY id").fetchall()
        summaries_before = self.connection.execute("SELECT * FROM summaries ORDER BY node_id").fetchall()

        initialize_database(self.connection)
        initialize_database(self.connection)

        self.assertEqual(
            self.connection.execute("SELECT * FROM documents ORDER BY id").fetchall(), documents_before,
        )
        self.assertEqual(
            self.connection.execute("SELECT * FROM summaries ORDER BY node_id").fetchall(), summaries_before,
        )


if __name__ == "__main__":
    unittest.main()
