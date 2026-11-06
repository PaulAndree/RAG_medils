import asyncio
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import BackgroundTasks, UploadFile
from fastapi.testclient import TestClient
from RAG_medils.ingest import api
from RAG_medils.ingest.stores.database_postgres import DocumentRegistration


class UploadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.environment = patch.dict('os.environ', {'INGEST_DATA_ROOT': str(self.root)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        api.app.dependency_overrides[api.authenticate] = lambda: {'tenant_id': 'company', 'permission': 'ingest'}
        self.addCleanup(api.app.dependency_overrides.clear)
        self.rows = {}
        self.stored_documents = []
        self.store = patch('ingest.api.store_document', side_effect=self.register).start()
        self.process = patch('ingest.api.process_tenant_documents', new_callable=AsyncMock).start()
        self.index = patch('ingest.api.index_summaries').start()
        self.addCleanup(patch.stopall)
        self.client = TestClient(api.app)
        self.addCleanup(self.client.close)

    def register(self, document):
        self.assertTrue(Path(document.doc_path).is_file())
        key = (document.tenant_id, document.doc_hash)
        self.stored_documents.append(document)
        if key in self.rows:
            existing = self.rows[key]
            return DocumentRegistration(existing.document_id, existing.tenant_id, existing.has_summary, False)
        result = DocumentRegistration(document.id, document.tenant_id, False, True)
        self.rows[key] = result
        return result

    def upload(self, content=b'# Paper', metadata=None, filename='paper.md'):
        return self.client.post('/ingest', files={'file': (filename, content)},
                                data={} if metadata is None else {'metadata': metadata})

    def test_upload_registers_metadata_and_schedules_processing(self):
        metadata = {'title': 'Original title', 'repository_id': 'repo', 'custom': {'tags': ['a']}}
        response = self.upload(metadata=json.dumps(metadata))
        self.assertEqual(response.status_code, 202)
        self.assertFalse(response.json()['has_summary'])
        self.assertEqual(self.stored_documents[0].metadata, metadata)
        self.process.assert_awaited_once_with('company')
        self.index.assert_not_called()
        self.assertEqual(self.stored_documents[0].id.hex, response.json()['document_id'].replace('-', ''))

    def test_invalid_input_does_not_save_or_schedule(self):
        for metadata, filename, content in [('[]', 'x.md', b'x'), ('{', 'x.md', b'x'),
                                              ('{"x":NaN}', 'x.md', b'x'), ('{}', 'x.docx', b'x'),
                                              ('{}', 'x.md', b''), ('{}', 'x.md', b'\xff')]:
            with self.subTest(metadata=metadata, filename=filename, content=content):
                self.assertEqual(self.upload(content, metadata, filename).status_code, 422)
        self.store.assert_not_called()
        self.process.assert_not_awaited()
        self.assertEqual([p for p in self.root.rglob('*') if p.is_file()], [])

    def test_registration_failure_cleans_only_new_upload(self):
        first = self.upload()
        original = Path(self.stored_documents[0].doc_path)
        self.store.side_effect = RuntimeError('database unavailable')
        with self.assertLogs('ingest.api', level='ERROR'):
            response = self.upload(b'Second')
        self.assertEqual(response.status_code, 500)
        self.assertTrue(original.exists())
        self.assertEqual(len([p for p in self.root.rglob('*') if p.is_file()]), 1)
        self.assertEqual(self.process.await_count, 1)

    def test_pending_duplicate_retries_without_replacing_metadata(self):
        first = self.upload(metadata='{"title":"first"}')
        second = self.upload(metadata='{"title":"second"}', filename='renamed.md')
        self.assertEqual(second.status_code, 202)
        self.assertEqual(first.json()['document_id'], second.json()['document_id'])
        self.assertEqual(len([p for p in self.root.rglob('*') if p.is_file()]), 1)
        self.assertEqual(self.process.await_count, 2)
        self.assertEqual(self.stored_documents[0].title, 'first')

    def test_completed_duplicate_returns_200_without_processing(self):
        first = self.upload()
        key, value = next(iter(self.rows.items()))
        self.rows[key] = DocumentRegistration(value.document_id, value.tenant_id, True, True)
        response = self.upload()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['has_summary'])
        self.assertEqual(response.json()['document_id'], first.json()['document_id'])
        self.assertEqual(self.process.await_count, 1)
        self.index.assert_called_once_with()

    def test_filename_cannot_escape_document_directory(self):
        response = self.upload(filename='../../note-example.md')
        self.assertEqual(response.status_code, 202)
        path = Path(self.stored_documents[0].doc_path)
        self.assertTrue(path.is_relative_to(self.root))
        self.assertEqual(path.name, 'note-example.md')

    def test_status_lookup_is_scoped_to_authenticated_tenant(self):
        document_id = uuid4()
        with patch('ingest.api.get_document', return_value=None) as lookup:
            self.assertEqual(self.client.get(f'/ingest/{document_id}').status_code, 404)
        lookup.assert_called_once_with(document_id, 'company')
        with patch('ingest.api.get_document', return_value={'id': document_id, 'tenant_id': 'company', 'has_summary': True}):
            response = self.client.get(f'/ingest/{document_id}')
        self.assertTrue(response.json()['has_summary'])

    def test_read_only_key_cannot_upload(self):
        api.app.dependency_overrides[api.authenticate] = lambda: {'tenant_id': 'company', 'permission': 'read'}
        self.assertEqual(self.upload().status_code, 403)
        self.store.assert_not_called()

    def test_invalid_key_is_rejected(self):
        api.app.dependency_overrides.clear()
        with patch('ingest.api.database_connection') as connection:
            connection.return_value.__enter__.return_value.execute.return_value.fetchone.return_value = None
            response = self.client.post('/ingest', headers={'Authorization': 'Bearer invalid'}, files={'file': ('x.md', b'x')})
        self.assertEqual(response.status_code, 401)
        self.process.assert_not_awaited()


class BackgroundResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_completed_document_indexes_only_after_response(self):
        events = []
        result = DocumentRegistration(uuid4(), 'company', True, False)
        def index():
            self.assertEqual(events, ['http.response.start', 'http.response.body'])
            events.append('indexed')
        async def send(message):
            events.append(message['type'])
        async def receive():
            return {'type': 'http.disconnect'}
        upload = UploadFile(filename='paper.md', file=io.BytesIO(b'Text'))
        background = BackgroundTasks()
        with patch('ingest.api._register_upload', return_value=result), patch('ingest.api.index_summaries', index):
            response = await api.ingestion(upload, background, 'company')
            self.assertEqual(events, [])
            response.background = background
            await response({'type': 'http', 'method': 'POST'}, receive, send)
        self.assertEqual(events[-1], 'indexed')

    async def test_response_body_is_sent_before_processing_begins(self):
        events = []
        result = DocumentRegistration(uuid4(), 'company', False, True)
        async def process(tenant_id):
            self.assertEqual(events, ['committed', 'http.response.start', 'http.response.body'])
            events.append('processing')
        def register(*args):
            events.append('committed')
            return result
        async def send(message):
            events.append(message['type'])
        async def receive():
            return {'type': 'http.disconnect'}
        upload = UploadFile(filename='paper.md', file=io.BytesIO(b'Text'))
        background = BackgroundTasks()
        with patch('ingest.api._register_upload', side_effect=register), patch('ingest.api.process_tenant_documents', process):
            response = await api.ingestion(upload, background, 'company')
            self.assertEqual(events, ['committed'])
            response.background = background
            await response({'type': 'http', 'method': 'POST'}, receive, send)
        self.assertEqual(events[-1], 'processing')

    async def test_startup_reschedules_pending_tenants_without_waiting_for_processing(self):
        release = asyncio.Event()
        started = []
        async def process(tenant):
            started.append(tenant)
            await release.wait()
        with patch('ingest.api.initialize_database') as initialize, patch('ingest.api.get_pending_tenants', return_value=['a', 'b']), patch('ingest.api.process_tenant_documents', process):
            async with api.lifespan(api.app):
                initialize.assert_called_once()
                await asyncio.sleep(0)
                self.assertEqual(started, ['a', 'b'])
                self.assertTrue(all(not task.done() for task in api.app.state.recovery_tasks))
                release.set()
            self.assertTrue(all(task.done() for task in api.app.state.recovery_tasks))


if __name__ == '__main__':
    unittest.main()
