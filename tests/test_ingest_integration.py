"""Exercise the actual upload -> representation -> PostgreSQL workflow.

Remote OCR/model/chunking/embedding/metrics calls and the indexing stage are mocked. Every test
uses its own committed schema so background connections see real transactions.
"""

import asyncio
import json
import os
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

from psycopg import sql
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RAG_medils.ingest import api
from RAG_medils.ingest import processing
from RAG_medils.ingest.stores.database_postgres import get_connection as base_get_connection
from RAG_medils.ingest.stores.database_postgres import get_indexable_summaries


@unittest.skipUnless(os.getenv('RUN_POSTGRES_TESTS') == '1', 'set RUN_POSTGRES_TESTS=1')
class AutomaticIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.schema = f'ingest_test_{uuid4().hex}'
        with base_get_connection() as conn:
            conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(self.schema)))
        self.addCleanup(self.drop_schema)
        self.start_patch(patch.dict(os.environ, {'INGEST_DATA_ROOT': str(self.root)}))
        self.start_patch(patch('RAG_medils.ingest.stores.database_postgres.get_connection', side_effect=self.connection))
        self.chunk = self.start_patch(patch(
            'RAG_medils.ingest.representations.summaries.builder.chunk_document',
            side_effect=lambda path: {'chunk_list': [path.read_text()]},
        ))
        self.start_patch(patch('RAG_medils.ingest.representations.summaries.builder._embed_texts', side_effect=lambda texts: [[0.1, 0.2] for _ in texts]))
        self.summarize = self.start_patch(patch('RAG_medils.ingest.representations.summaries.builder._invoke_summary', return_value='Generated summary.'))
        self.start_patch(patch('RAG_medils.ingest.representations.main.push_process_metrics'))
        self.indexed_snapshots = []
        self.index = Mock(side_effect=self.capture_index)
        self.start_patch(patch('RAG_medils.ingest.indexing.main._load_stage_runners', return_value=(('summaries', self.index),)))
        processing._tenant_locks.clear()
        api.app.dependency_overrides[api.authenticate] = lambda: {'tenant_id': 'a', 'permission': 'ingest'}
        self.addCleanup(api.app.dependency_overrides.clear)
        self.client = TestClient(api.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def start_patch(self, patcher):
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

    def drop_schema(self):
        with base_get_connection() as conn:
            conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(self.schema)))

    def connection(self):
        conn = base_get_connection()
        conn.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(self.schema)))
        conn.commit()
        return conn

    def query(self, query, params=()):
        with self.connection() as conn:
            return conn.execute(query, params).fetchall()

    def upload(self, content=b'First document', name='note-first.md', metadata='{"title":"Uploaded title"}'):
        return self.client.post('/ingest', files={'file': (name, content)}, data={'metadata': metadata})

    def capture_index(self):
        records = get_indexable_summaries()
        self.assertTrue(records)
        documents = {
            document_id: (title, f'tenant:{tenant_id}')
            for document_id, title, tenant_id in self.query('SELECT id::text, title, tenant_id FROM documents')
        }
        for record in records:
            if record['scope'] == 'catalog':
                self.assertIsNone(record['document_title'])
            else:
                self.assertEqual(
                    (record['document_title'], record['catalog_id']),
                    documents[record['document_id']],
                )
        self.assertEqual(self.query(
            'SELECT count(*) FROM summaries s JOIN documents d ON d.id = s.document_id WHERE NOT d.has_summary'
        ), [(0,)])
        self.indexed_snapshots.append(records)

    def test_titles_reach_every_level_and_qdrant_payload(self):
        from RAG_medils.ingest.representations.summaries import builder

        self.chunk.side_effect = None
        self.chunk.return_value = {
            'chunk_list': [f'Scientific passage {index}' for index in range(10)],
            'chunk_title': ['Section title'] * 10,
        }
        with patch.object(builder, 'perform_clustering', side_effect=lambda **kwargs: [[0] for _ in kwargs['embeddings']]):
            response = self.upload(metadata=json.dumps({'title': 'Título científico'}))
        self.assertEqual(response.status_code, 202)
        self.index.assert_called_once_with()
        records = self.indexed_snapshots[-1]
        self.assertEqual({row['scope'] for row in records}, {'passage', 'document_cluster', 'document', 'catalog'})
        for row in records:
            self.assertEqual(row['document_title'], None if row['scope'] == 'catalog' else 'Título científico')
            self.assertEqual(row['catalog_id'], 'tenant:a')
            if row['scope'] == 'passage':
                self.assertEqual(row['title'], 'Section title')

        # Exercise the real payload builder without contacting Qdrant or models.
        with patch('qdrant_client.QdrantClient'):
            from RAG_medils.ingest.indexing.summaries import indexer_qdrant as indexer

        def embed(texts, model):
            vector = [0.1, 0.2] if model == indexer.DENSE_MODEL else {'indices': [1], 'values': [0.5]}
            return [vector for _ in texts]

        with patch.object(indexer, 'client') as client, patch.object(indexer, 'embed_texts', side_effect=embed):
            indexer.index_summaries('test-summaries', records)
        payloads = client.upload_collection.call_args.kwargs['payload']
        self.assertEqual(len(payloads), len(records))
        for payload, record in zip(payloads, records, strict=True):
            self.assertEqual(payload['document_title'], record['document_title'])
            self.assertEqual(payload['catalog_id'], record['catalog_id'])
            self.assertEqual(payload['title'], record['title'])

    def test_missing_upload_title_uses_original_filename(self):
        response = self.upload(name='Filename title.md', metadata='{}')
        self.assertEqual(response.status_code, 202)
        self.index.assert_called_once_with()
        self.assertEqual(
            self.query('SELECT DISTINCT document_title FROM summaries WHERE document_id = %s',
                       (response.json()['document_id'],)),
            [('Filename title',)],
        )

    def test_complete_workflow_reuses_hierarchies_and_isolates_tenants(self):
        first = self.upload(metadata=json.dumps({
            "title": "Uploaded title",
            "createdDateTime": "2026-10-28T10:30:00Z",
            "modifiedDateTime": "2026-10-29T14:30:00Z",
        }))
        self.assertEqual(first.status_code, 202)
        first_id = first.json()['document_id']
        self.assertFalse(first.json()['has_summary'])
        self.assertTrue(self.client.get(f'/ingest/{first_id}').json()['has_summary'])
        self.index.assert_called_once_with()
        self.assertEqual(len(self.indexed_snapshots[0]), 3)
        self.assertEqual(
            {row['createdDateTime'] for row in self.indexed_snapshots[0] if row['document_id'] == first_id},
            {datetime.fromisoformat('2026-10-28T10:30:00Z')},
        )
        second = self.upload(b'Second document', 'note-second.md')
        self.assertEqual(second.status_code, 202)
        second_id = second.json()['document_id']
        self.assertEqual(self.chunk.call_count, 2, 'completed first hierarchy must be reused')
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(5,)])
        self.assertEqual(len(self.indexed_snapshots[-1]), 5)
        self.assertEqual(
            self.query(
                'SELECT "createdDateTime", "modifiedDateTime" FROM summaries WHERE document_id = %s',
                (first_id,),
            ),
            [(datetime.fromisoformat("2026-10-28T10:30:00Z"),
              datetime.fromisoformat("2026-10-29T14:30:00Z"))] * 2,
        )
        self.assertEqual(
            self.query(
                'SELECT "createdDateTime", "modifiedDateTime" FROM summaries '
                'WHERE document_id = %s OR scope = \'catalog\'', (second_id,),
            ), [(None, None)] * 3,
        )
        sources = self.query("SELECT source_document_ids FROM summaries WHERE scope = 'catalog' AND catalog_id = 'tenant:a'")[0][0]
        self.assertEqual(set(sources), {first_id, second_id})
        duplicate = self.upload(metadata='{"title":"Must not replace original"}')
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(self.index.call_count, 3)
        self.assertEqual(self.chunk.call_count, 2)
        self.assertEqual(duplicate.json()['document_id'], first_id)
        self.assertEqual(self.query('SELECT title FROM documents WHERE id = %s', (first_id,)), [('Uploaded title',)])
        api.app.dependency_overrides[api.authenticate] = lambda: {'tenant_id': 'b', 'permission': 'ingest'}
        third = self.upload()
        self.assertEqual(third.status_code, 202)
        self.assertNotEqual(third.json()['document_id'], first_id)
        self.assertEqual(self.client.get(f'/ingest/{first_id}').status_code, 404)
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(8,)])
        self.assertEqual(len(self.indexed_snapshots[-1]), 8)
        self.assertEqual(self.query("SELECT source_document_ids FROM summaries WHERE scope = 'catalog' AND catalog_id = 'tenant:a'")[0][0], sources)

    def test_failed_model_preserves_document_and_reupload_retries(self):
        with patch('RAG_medils.ingest.representations.summaries.builder._invoke_summary', side_effect=RuntimeError('model down')):
            with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
                first = self.upload()
        document_id = first.json()['document_id']
        self.assertEqual(first.status_code, 202)
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(False,)])
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(0,)])
        self.index.assert_not_called()
        original = Path(self.query('SELECT doc_path FROM documents')[0][0])
        self.assertTrue(original.exists())
        retry = self.upload(metadata='{"title":"Ignored duplicate title"}')
        self.assertEqual(retry.json()['document_id'], document_id)
        self.assertEqual(self.query('SELECT has_summary, title FROM documents'), [(True, 'Uploaded title')])
        self.assertEqual(len(list(self.root.rglob('documents/*/*.md'))), 1)

    def test_failed_indexing_preserves_summaries_and_reupload_retries(self):
        self.index.side_effect = RuntimeError('index unavailable')
        with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
            first = self.upload()
        self.assertEqual(first.status_code, 202)
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(True,)])
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(3,)])
        self.index.side_effect = self.capture_index
        retry = self.upload()
        self.assertEqual(retry.status_code, 200)
        self.assertEqual(retry.json()['document_id'], first.json()['document_id'])
        self.assertEqual(self.index.call_count, 2)
        self.assertEqual(self.chunk.call_count, 1)
        self.assertEqual(len(self.indexed_snapshots[-1]), 3)

    def test_concurrent_identical_uploads_register_only_one_original(self):
        barrier = threading.Barrier(2)
        real_store = api.store_document
        def store(document):
            barrier.wait(timeout=5)
            return real_store(document)
        with patch('RAG_medils.ingest.api.store_document', side_effect=store):
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(lambda _: self.upload(), range(2)))
        self.assertTrue(all(response.status_code in {200, 202} for response in responses))
        self.assertEqual(len({response.json()['document_id'] for response in responses}), 1)
        self.assertEqual(self.query('SELECT count(*), bool_and(has_summary) FROM documents'), [(1, True)])
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(3,)])
        self.assertEqual(len(list(self.root.rglob('documents/*/*.md'))), 1)

    def test_pdf_ocr_runs_after_registration_and_stores_original_path(self):
        def post(*args, **kwargs):
            self.assertEqual(self.query('SELECT has_summary FROM documents'), [(False,)])
            from unittest.mock import Mock
            response = Mock()
            response.json.return_value = {'content_parsed': '# Converted PDF'}
            return response
        with patch('RAG_medils.ingest.processing.httpx.Client') as client:
            client.return_value.__enter__.return_value.post.side_effect = post
            response = self.upload(b'%PDF example', 'paper.pdf')
        self.assertEqual(response.status_code, 202)
        row = self.query('SELECT doc_path, has_summary FROM documents')[0]
        self.assertTrue(row[0].endswith('paper.pdf'))
        self.assertTrue(row[1])
        self.assertEqual(Path(row[0]).read_bytes(), b'%PDF example')

    def test_concurrent_distinct_uploads_keep_both_catalog_members(self):
        barrier = threading.Barrier(2)
        real_store = api.store_document

        def store(document):
            result = real_store(document)
            barrier.wait(timeout=5)
            return result

        def upload(number):
            return self.upload(f'Document {number}'.encode(), f'note-{number}.md')

        with patch('RAG_medils.ingest.api.store_document', side_effect=store):
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(upload, range(2)))
        self.assertTrue(all(response.status_code == 202 for response in responses))
        ids = {response.json()['document_id'] for response in responses}
        self.assertEqual(self.query('SELECT count(*), bool_and(has_summary) FROM documents'), [(2, True)])
        sources = self.query("SELECT source_document_ids FROM summaries WHERE scope = 'catalog'")[0][0]
        self.assertEqual(set(sources), ids)

    def test_failed_storage_keeps_pending_flag_and_rebuilds_uncommitted_cache(self):
        with patch('RAG_medils.ingest.processing.store_summaries', side_effect=RuntimeError('storage failed')):
            with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
                first = self.upload()
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(False,)])
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(0,)])
        self.assertTrue(list(self.root.rglob('summaries/level_0.json')))
        second = self.upload()
        self.assertEqual(second.json()['document_id'], first.json()['document_id'])
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(True,)])
        self.assertEqual(self.chunk.call_count, 2, 'uncommitted cached hierarchy must be rebuilt')

    def test_restart_recovers_pending_rows(self):
        with patch('RAG_medils.ingest.representations.summaries.builder._invoke_summary', side_effect=RuntimeError('interrupted')):
            with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
                self.upload()
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(False,)])
        processing._tenant_locks.clear()
        async def wait_recovery():
            await asyncio.gather(*api.app.state.recovery_tasks)
        with TestClient(api.app) as restarted:
            restarted.portal.call(wait_recovery)
        self.assertEqual(self.query('SELECT has_summary FROM documents'), [(True,)])
        self.assertEqual(self.query('SELECT count(*) FROM summaries'), [(3,)])


if __name__ == '__main__':
    unittest.main()
