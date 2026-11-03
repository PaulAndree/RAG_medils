import asyncio
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RAG_medils.ingest import processing
from RAG_medils.ingest.representations.common import DocumentInput
from RAG_medils.ingest.stores.ingestion import prepare_summaries, validate_summary_references
from tests.test_stores_raptor import write_raptor_fixture


class ProcessingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = patch.dict('os.environ', {'INGEST_DATA_ROOT': str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        index_patch = patch('RAG_medils.ingest.processing.index_summaries')
        self.index = index_patch.start()
        self.addCleanup(index_patch.stop)

    def document(self, suffix='.md', name='note-example'):
        original = self.root / (name + suffix)
        original.write_bytes(b'Original content')
        return {'id': uuid4(), 'source_key': f'unique/{name}', 'doc_path': str(original), 'title': 'Registered document title', 'has_summary': False}

    def test_pdf_calls_ocr_and_caches_markdown(self):
        document = self.document('.pdf')
        with patch('RAG_medils.ingest.processing.httpx.Client') as client:
            response = client.return_value.__enter__.return_value.post.return_value
            response.json.return_value = {'content_parsed': '# OCR result'}
            path = processing._prepare_markdown(document, processing.tenant_data_root('a'))
            self.assertEqual(path.read_text(), '# OCR result')
            processing._prepare_markdown(document, processing.tenant_data_root('a'))
            self.assertEqual(client.call_count, 1)
            response.raise_for_status.assert_called_once()
        self.assertTrue(Path(document['doc_path']).exists())

    def test_markdown_bypasses_ocr_and_preserves_filename_prefix(self):
        document = self.document()
        with patch('RAG_medils.ingest.processing.httpx.Client') as client:
            path = processing._prepare_markdown(document, processing.tenant_data_root('a'))
        client.assert_not_called()
        self.assertEqual(path.name, 'note-example.md')
        self.assertEqual(path.read_text(), 'Original content')
        self.assertNotEqual(processing.tenant_data_root('a'), processing.tenant_data_root('b'))

    def test_invalid_ocr_does_not_create_markdown(self):
        document = self.document('.pdf')
        with patch('RAG_medils.ingest.processing.httpx.Client') as client:
            client.return_value.__enter__.return_value.post.return_value.json.return_value = {'content_parsed': None}
            with self.assertRaises(ValueError):
                processing._prepare_markdown(document, processing.tenant_data_root('a'))
        self.assertTrue(Path(document['doc_path']).exists())
        self.assertFalse(any(self.root.rglob('*.md')))

    def test_orchestration_uses_registered_ids_before_storing(self):
        document = self.document()
        events = []
        self.index.side_effect = lambda: events.append('index')
        def run(data_root, *, registered_documents):
            events.append('represent')
            self.assertEqual(registered_documents[0].id, document['id'])
            self.assertEqual(registered_documents[0].source_key, document['source_key'])
            self.assertEqual(registered_documents[0].catalog_id, 'tenant:a')
            self.assertEqual(registered_documents[0].title, document['title'])
            write_raptor_fixture(data_root, document_id=document['id'], source_key=document['source_key'], catalog_id='tenant:a')
        def store(nodes, *, tenant_id):
            events.append('store')
            self.assertEqual(tenant_id, 'a')
            validate_summary_references(nodes, {document['id']: document['source_key']})
        with patch('RAG_medils.ingest.processing.get_tenant_documents', return_value=[document]), patch('RAG_medils.ingest.representations.main.run_pipeline', side_effect=run), patch('RAG_medils.ingest.processing.store_summaries', side_effect=store):
            processing._process_tenant_documents('a')
        self.assertEqual(events, ['represent', 'store', 'index'])

    def test_completed_documents_do_not_trigger_processing(self):
        document = self.document()
        document['has_summary'] = True
        with patch('RAG_medils.ingest.processing.get_tenant_documents', return_value=[document]), patch('RAG_medils.ingest.processing._prepare_markdown') as prepare:
            processing._process_tenant_documents('a')
        prepare.assert_not_called()
        self.index.assert_not_called()

    def test_pipeline_failure_does_not_store_summaries(self):
        document = self.document()
        with patch('RAG_medils.ingest.processing.get_tenant_documents', return_value=[document]), patch('RAG_medils.ingest.representations.main.run_pipeline', side_effect=RuntimeError('model unavailable')), patch('RAG_medils.ingest.processing.store_summaries') as store:
            with self.assertRaises(RuntimeError):
                processing._process_tenant_documents('a')
        store.assert_not_called()
        self.index.assert_not_called()
        self.assertTrue(Path(document['doc_path']).exists())

    def test_storage_failure_does_not_index(self):
        document = self.document()
        with patch('RAG_medils.ingest.processing.get_tenant_documents', return_value=[document]), patch('RAG_medils.ingest.representations.main.run_pipeline'), patch('RAG_medils.ingest.processing.prepare_summaries', return_value=()), patch('RAG_medils.ingest.processing.store_summaries', side_effect=RuntimeError('storage failed')):
            with self.assertRaisesRegex(RuntimeError, 'storage failed'):
                processing._process_tenant_documents('a')
        self.index.assert_not_called()

    def test_builder_uses_registered_id_and_catalog(self):
        from RAG_medils.ingest.representations.summaries.builder import load_documents
        document = self.document()
        markdown_root = self.root / 'pdf_parsed_output'
        markdown_root.mkdir()
        record = DocumentInput(document['id'], document['source_key'], Path(document['doc_path']), 'tenant:a', title=document['title'])
        with patch('RAG_medils.ingest.representations.summaries.builder.chunk_document', return_value={'chunk_list': ['Text']}), patch('RAG_medils.ingest.representations.summaries.builder._embed_texts', return_value=[[0.1, 0.2]]):
            docs = load_documents(markdown_root, registered_documents=[record])
        self.assertEqual(docs[0]['document_id'], str(document['id']))
        self.assertEqual(docs[0]['catalog_id'], 'tenant:a')
        self.assertEqual(docs[0]['source_key'], document['source_key'])
        self.assertEqual(docs[0]['document_title'], document['title'])

    def test_standalone_builder_uses_filename_as_document_title(self):
        from RAG_medils.ingest.representations.summaries import builder

        self.document(name='Filename title')
        with patch.object(builder, 'chunk_document', return_value={'chunk_list': ['Text'], 'chunk_title': ['Section title']}), patch.object(builder, '_embed_texts', return_value=[[0.1, 0.2]]):
            document = builder.load_documents(self.root)[0]
        self.assertEqual(document['document_title'], 'Filename title')
        self.assertEqual(document['chunks'][0]['title'], 'Section title')

    def test_metadata_survives_clusters_json_and_reused_hierarchies(self):
        from RAG_medils.ingest.representations.summaries import builder

        markdown_root = self.root / 'pdf_parsed_output'
        markdown_root.mkdir()
        inputs = []
        for index, title in enumerate(('Título científico', 'Second document')):
            path = markdown_root / f'paper-{index}.md'
            path.write_text('Scientific content.')
            inputs.append(DocumentInput(uuid4(), path.stem, path, 'tenant:a', title=title))
        titles = {document.id: document.title for document in inputs}
        chunks = {'chunk_list': [f'Passage {index}' for index in range(10)], 'chunk_title': ['Section'] * 10}
        with patch.object(builder, 'chunk_document', return_value=chunks) as chunk, patch.object(builder, '_embed_texts', side_effect=lambda texts: [[0.1, 0.2] for _ in texts]), patch.object(builder, '_invoke_summary', return_value='Summary.') as summarize, patch.object(builder, 'perform_clustering', side_effect=lambda **kwargs: [[0] for _ in kwargs['embeddings']]):
            builder.run(self.root, registered_documents=inputs)
            summaries = prepare_summaries(self.root / 'summaries')
            self.assertEqual({node.scope for node in summaries}, {'passage', 'document_cluster', 'document', 'catalog'})
            for node in summaries:
                self.assertEqual(node.catalog_id, 'tenant:a')
                self.assertEqual(node.document_title, titles.get(node.document_id))
            validate_summary_references(summaries, {document.id: document.source_key for document in inputs})
            chunk.reset_mock()
            summarize.reset_mock()
            builder.run(self.root, skip_existing=True, registered_documents=[replace(document, has_summary=True) for document in inputs])
            self.assertEqual(prepare_summaries(self.root / 'summaries'), summaries)
            chunk.assert_not_called()
            summarize.assert_not_called()


class IndexingTests(unittest.TestCase):
    def test_indexing_stops_after_failed_stage_and_allows_retry(self):
        from unittest.mock import Mock
        first = Mock(side_effect=RuntimeError('index unavailable'))
        second = Mock()
        with patch('RAG_medils.ingest.indexing.main._load_stage_runners', return_value=(('first', first), ('second', second))):
            with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
                processing.index_summaries()
            second.assert_not_called()
            first.side_effect = None
            processing.index_summaries()
        self.assertEqual(first.call_count, 2)
        second.assert_called_once_with()

    def test_shared_index_rebuilds_are_serialized(self):
        started = threading.Event()
        release = threading.Event()
        attempted = threading.Event()
        def run():
            started.set()
            if not release.wait(3):
                raise TimeoutError('test release not signaled')
        def second_run():
            attempted.set()
            processing.index_summaries()
        with patch('RAG_medils.ingest.indexing.main.run_pipeline', side_effect=run) as pipeline:
            with ThreadPoolExecutor(max_workers=2) as pool:
                first = pool.submit(processing.index_summaries)
                try:
                    self.assertTrue(started.wait(2))
                    second = pool.submit(second_run)
                    self.assertTrue(attempted.wait(2))
                    self.assertEqual(pipeline.call_count, 1)
                finally:
                    release.set()
                first.result(timeout=3)
                second.result(timeout=3)
        self.assertEqual(pipeline.call_count, 2)


class SerializationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        processing._tenant_locks.clear()

    async def test_same_tenant_runs_serially_without_blocking_event_loop(self):
        started = threading.Event()
        release = threading.Event()
        calls = []
        def work(tenant):
            calls.append(tenant)
            if len(calls) == 1:
                started.set()
                if not release.wait(3):
                    raise TimeoutError('test release not signaled')
        with patch('RAG_medils.ingest.processing._process_tenant_documents', side_effect=work):
            first = asyncio.create_task(processing.process_tenant_documents('a'))
            await asyncio.wait_for(asyncio.to_thread(started.wait), 2)
            second = asyncio.create_task(processing.process_tenant_documents('a'))
            await asyncio.sleep(0.02)
            self.assertEqual(calls, ['a'])
            release.set()
            await asyncio.wait_for(asyncio.gather(first, second), 3)
        self.assertEqual(calls, ['a', 'a'])

    async def test_background_failure_is_logged_and_allows_retry(self):
        with patch('RAG_medils.ingest.processing._process_tenant_documents', side_effect=[RuntimeError('OCR failed'), None]) as work:
            with self.assertLogs('RAG_medils.ingest.processing', level='ERROR'):
                await processing.process_tenant_documents('a')
            await processing.process_tenant_documents('a')
        self.assertEqual(work.call_count, 2)


if __name__ == '__main__':
    unittest.main()
