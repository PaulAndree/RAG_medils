import json
import shutil
import tempfile
import unittest
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from RAG_medils.ingest.representations.common import StageResult
from RAG_medils.ingest.representations.main import (
    GENERATED_PATHS,
    clean_generated_outputs,
    run_pipeline,
)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.data_root = Path(self.temporary_directory.name)
        pdf_dir = self.data_root / "pdf_docs"
        pdf_dir.mkdir()
        (pdf_dir / "paper.pdf").write_bytes(b"pdf")
        markdown_dir = self.data_root / "pdf_parsed_output"
        markdown_dir.mkdir()
        (markdown_dir / "paper.md").write_text("Text", encoding="utf-8")
        (self.data_root / "keep.txt").write_text("keep", encoding="utf-8")
        for relative_path in GENERATED_PATHS:
            directory = self.data_root / relative_path
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "old.txt").write_text("old", encoding="utf-8")

    def test_runs_stages_in_order_and_cleans_only_generated_outputs(self):
        calls = []

        def stage(name):
            def run(data_root):
                calls.append(name)
                output = data_root / "summaries" / f"{name}.txt"
                output.write_text(name, encoding="utf-8")
                return StageResult(name, 0.1, {"items": 1})

            return run

        results = run_pipeline(
            self.data_root,
            metrics_enabled=False,
            clean=True,
            stage_runners=[
                ("passages", stage("passages")),
                ("arguments", stage("arguments")),
                ("summaries", stage("summaries")),
                ("graph", stage("graph")),
            ],
        )

        self.assertEqual(
            calls,
            [
                "passages",
                "arguments",
                "summaries",
                "graph",
            ],
        )
        self.assertEqual([result.stage for result in results], [
            "passages",
            "arguments",
            "summaries",
            "graph",
        ])
        self.assertTrue((self.data_root / "pdf_docs" / "paper.pdf").exists())
        self.assertTrue(
            (self.data_root / "pdf_parsed_output" / "paper.md").exists()
        )
        self.assertEqual(
            (self.data_root / "keep.txt").read_text(encoding="utf-8"),
            "keep",
        )
        self.assertFalse(any(self.data_root.rglob("old.txt")))

    def test_resume_mode_keeps_existing_outputs(self):
        existing = self.data_root / "summaries" / "old.txt"

        run_pipeline(
            self.data_root,
            metrics_enabled=False,
            stage_runners=[(
                "passages",
                lambda _root: StageResult("passages", 0.0),
            )],
        )

        self.assertTrue(existing.exists())

    def test_cleanup_validates_every_target_before_deleting_anything(self):
        invalid_target = self.data_root / "summaries"
        shutil.rmtree(invalid_target)
        invalid_target.write_text("not a directory", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "not a directory"):
            clean_generated_outputs(self.data_root)

        self.assertEqual(
            invalid_target.read_text(encoding="utf-8"),
            "not a directory",
        )

    def test_stage_failure_stops_pipeline_and_keeps_partial_outputs(self):
        calls = []

        def passages(data_root):
            calls.append("passages")
            (data_root / "summaries" / "partial.json").write_text(
                "{}",
                encoding="utf-8",
            )
            return StageResult("passages", 0.1)

        def arguments(_data_root):
            calls.append("arguments")
            raise RuntimeError("model failed")

        def summaries(_data_root):
            calls.append("summaries")
            return StageResult("summaries", 0.1)

        with self.assertRaisesRegex(RuntimeError, "model failed"):
            run_pipeline(
                self.data_root,
                metrics_enabled=False,
                stage_runners=[
                    ("passages", passages),
                    ("arguments", arguments),
                    ("summaries", summaries),
                ],
            )

        self.assertEqual(calls, ["passages", "arguments"])
        self.assertTrue(
            (self.data_root / "summaries" / "partial.json").exists()
        )

    @patch("representations.main.push_process_metrics")
    def test_metric_publication_failure_is_nonfatal(self, push):
        push.side_effect = OSError("gateway down")

        run_pipeline(
            self.data_root,
            stage_runners=[(
                "passages",
                lambda _root: StageResult("passages", 0.0),
            )],
        )

        push.assert_called_once()

    @patch("representations.main.push_process_metrics")
    def test_publishes_counts_and_duration_for_each_stage(self, push):
        results = run_pipeline(
            self.data_root,
            stage_runners=[
                (
                    "passages",
                    lambda _root: StageResult(
                        "passages",
                        0.0,
                        {"documents": 2, "chunks": 12},
                    ),
                ),
                (
                    "graph",
                    lambda _root: StageResult(
                        "graph",
                        0.0,
                        {"documents": 2, "entities": 8, "relations": 4},
                    ),
                ),
            ],
        )

        self.assertEqual(len(results), 2)
        kwargs = push.call_args.kwargs
        self.assertEqual(kwargs["process"], "representation")
        self.assertEqual(kwargs["job"], "representation_builder")
        samples = {
            sample.representation: sample
            for sample in kwargs["samples"]
        }
        self.assertEqual(samples["passages"].document_count, 2)
        self.assertEqual(samples["passages"].item_counts, {"chunks": 12})
        self.assertGreaterEqual(samples["passages"].duration_seconds, 0)
        self.assertEqual(
            samples["graph"].item_counts,
            {"entities": 8, "relations": 4},
        )


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class BuilderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.data_root = Path(self.temporary_directory.name)

    @patch("representations.passages.builder.requests.post")
    def test_passage_builder_writes_valid_outputs(self, post):
        from RAG_medils.ingest.representations.passages.builder import run

        markdown_dir = self.data_root / "pdf_parsed_output"
        markdown_dir.mkdir()
        (markdown_dir / "paper.md").write_text(
            "# Title\n\nText",
            encoding="utf-8",
        )
        post.return_value = FakeResponse({
            "chunk_list": ["Text"],
            "chunk_size": 1,
            "chunk_title": ["Title"],
            "token_count": [1],
        })

        result = run(self.data_root)

        self.assertEqual(result.counts, {"documents": 1, "chunks": 1})
        self.assertEqual(post.call_count, 1)
        output = json.loads(
            (self.data_root / "passages_chunk/paper_chunks.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(output["chunk_list"], ["Text"])

    @patch("representations.passages.builder.requests.post")
    def test_passage_builder_keeps_short_document_as_one_chunk(self, post):
        from RAG_medils.ingest.representations.passages.builder import run

        markdown_dir = self.data_root / "pdf_parsed_output"
        markdown_dir.mkdir()
        content = "A short chat message"
        (markdown_dir / "chat-example.md").write_text(
            content,
            encoding="utf-8",
        )

        result = run(self.data_root)

        post.assert_not_called()
        self.assertEqual(result.counts, {"documents": 1, "chunks": 1})
        output = json.loads(
            (
                self.data_root
                / "passages_chunk/chat-example_chunks.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(output["chunk_list"], [content])
        self.assertEqual(output["chunk_title"], ["chat-example"])

    @patch("representations.passages.builder.requests.post")
    def test_passage_builder_summarizes_long_short_form_document(self, post):
        from RAG_medils.ingest.representations.passages.builder import run

        markdown_dir = self.data_root / "pdf_parsed_output"
        markdown_dir.mkdir()
        (markdown_dir / "email-example.md").write_text(
            "word " * 500,
            encoding="utf-8",
        )
        post.return_value = FakeResponse({
            "message": {"content": "Compact email summary."},
            "eval_count": 4,
        })

        result = run(self.data_root)

        self.assertEqual(result.counts, {"documents": 1, "chunks": 1})
        post.assert_called_once()
        self.assertEqual(
            post.call_args.args[0],
            "http://localhost:11434/api/chat",
        )
        self.assertEqual(
            post.call_args.kwargs["json"]["options"]["num_predict"],
            450,
        )
        output = json.loads(
            (
                self.data_root
                / "passages_chunk/email-example_chunks.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(output["chunk_list"], ["Compact email summary."])
        self.assertEqual(output["token_count"], [4])

    @patch("representations.passages.builder.requests.post")
    def test_passage_builder_reuses_existing_outputs(self, post):
        from RAG_medils.ingest.representations.passages.builder import run

        markdown_dir = self.data_root / "pdf_parsed_output"
        chunks_dir = self.data_root / "passages_chunk"
        markdown_dir.mkdir()
        chunks_dir.mkdir()
        (markdown_dir / "paper.md").write_text("Text", encoding="utf-8")
        (chunks_dir / "paper_chunks.json").write_text(
            json.dumps({"chunk_list": ["Text"]}),
            encoding="utf-8",
        )

        run(self.data_root, skip_existing=True)

        post.assert_not_called()

    @patch("representations.arguments.extractor.requests.post")
    def test_argument_ids_are_one_based(self, post):
        from representations.arguments.extractor import extract_arguments

        post.return_value = FakeResponse({
            "response": json.dumps({
                "arguments": [{"claim": "Claim", "evidence": ["Evidence"]}]
            })
        })
        output_path = self.data_root / "arguments.json"

        arguments = extract_arguments(
            ["first", "second"],
            "paper",
            output_path,
        )

        self.assertEqual(
            [argument["id"] for argument in arguments],
            ["paper_chunk_1_arg_1", "paper_chunk_2_arg_1"],
        )

    @patch("representations.arguments.extractor.extract_arguments")
    @patch("representations.arguments.extractor.chunker")
    def test_argument_builder_reuses_existing_outputs(self, chunker, extract):
        from representations.arguments.extractor import run

        markdown_dir = self.data_root / "pdf_parsed_output"
        chunks_dir = self.data_root / "arguments/chunks_for_arguments"
        arguments_dir = self.data_root / "arguments/arguments_extracted"
        markdown_dir.mkdir(parents=True)
        chunks_dir.mkdir(parents=True)
        arguments_dir.mkdir(parents=True)
        (markdown_dir / "paper.md").write_text("Text", encoding="utf-8")
        (chunks_dir / "paper_chunks.json").write_text(
            json.dumps({"chunk_list": ["Text"]}),
            encoding="utf-8",
        )
        (arguments_dir / "paper_arguments.json").write_text(
            json.dumps([{"id": "paper_chunk_1_arg_1"}]),
            encoding="utf-8",
        )

        run(self.data_root, skip_existing=True)

        chunker.assert_not_called()
        extract.assert_not_called()

    @patch("representations.graph.extractor.normalize_document_graph")
    @patch("representations.graph.extractor.extract_triplets")
    def test_graph_builder_preserves_zero_based_chunk_ids(
        self,
        extract_triplets,
        normalize,
    ):
        from representations.graph.extractor import run

        chunks_dir = self.data_root / "arguments/chunks_for_arguments"
        chunks_dir.mkdir(parents=True)
        (chunks_dir / "paper_chunks.json").write_text(
            json.dumps({
                "chunk_list": ["one", "two"],
                "chunk_title": ["One", "Two"],
            }),
            encoding="utf-8",
        )
        extract_triplets.return_value = {
            "entities": [{
                "id": "entity",
                "name": "Entity",
                "type": "OTHER",
            }],
            "relations": [],
        }
        normalize.side_effect = lambda results, **_kwargs: results

        result = run(self.data_root)

        self.assertEqual(result.counts["documents"], 1)
        saved = json.loads(
            (self.data_root / "entities/paper_chunks_entities.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual([item["chunk_id"] for item in saved], [0, 1])

    @patch("representations.graph.extractor.extract_triplets")
    def test_graph_builder_reuses_existing_output(self, extract_triplets):
        from representations.graph.extractor import run

        chunks_dir = self.data_root / "arguments/chunks_for_arguments"
        entities_dir = self.data_root / "entities"
        chunks_dir.mkdir(parents=True)
        entities_dir.mkdir()
        (chunks_dir / "paper_chunks.json").write_text("{}", encoding="utf-8")
        (entities_dir / "paper_chunks_entities.json").write_text(
            "[]",
            encoding="utf-8",
        )

        run(self.data_root, skip_existing=True)

        extract_triplets.assert_not_called()

    @patch("representations.summaries.builder.save_levels")
    @patch("representations.summaries.builder.build_catalog_summary")
    @patch("representations.summaries.builder.build_document")
    @patch("representations.summaries.builder.load_documents")
    def test_summary_builder_returns_output_counts(
        self,
        load_documents,
        build_document,
        build_catalog_summary,
        save_levels,
    ):
        from RAG_medils.ingest.representations.summaries.builder import run

        document = {"document_id": "doc", "catalog_id": "catalog"}
        document_summary = {
            "node_id": "doc-summary",
            "document_id": "doc",
            "catalog_id": "catalog",
            "embedding": [0.1],
        }
        catalog_summary = {"node_id": "catalog-summary"}
        load_documents.return_value = [document]
        build_document.return_value = ({1: [document_summary]}, document_summary)
        build_catalog_summary.return_value = catalog_summary

        result = run(self.data_root)

        self.assertEqual(result.counts["documents"], 1)
        self.assertEqual(result.counts["levels"], 2)
        self.assertEqual(result.counts["summaries"], 2)
        save_levels.assert_called_once()

    @patch("representations.summaries.builder._embed_texts")
    @patch("representations.summaries.builder.chunk_document")
    def test_summary_builder_chunks_markdown_for_level_zero(
        self,
        chunk_document,
        embed_texts,
    ):
        from RAG_medils.ingest.representations.summaries.builder import (
            build_document,
            load_documents,
        )

        markdown_dir = self.data_root / "pdf_parsed_output"
        markdown_dir.mkdir()
        markdown_file = markdown_dir / "paper.md"
        markdown_file.write_text("# Paper\n\nText", encoding="utf-8")
        chunk_document.return_value = {
            "chunk_list": ["First chunk", "Second chunk"],
            "chunk_title": ["First", "Second"],
            "token_count": [2, 2],
        }
        embed_texts.return_value = [[0.1], [0.2]]

        documents = load_documents(markdown_dir)

        chunk_document.assert_called_once_with(markdown_file)
        self.assertEqual(len(documents), 1)
        self.assertEqual(
            [chunk["content"] for chunk in documents[0]["chunks"]],
            ["First chunk", "Second chunk"],
        )

        with patch(
            "representations.summaries.builder.create_summary_node",
            return_value={"node_id": "document-summary"},
        ):
            levels, _ = build_document(documents[0])

        self.assertEqual([node["level"] for node in levels[0]], [0, 0])
        self.assertEqual(
            [node["text"] for node in levels[0]],
            ["First chunk", "Second chunk"],
        )
        self.assertEqual(
            [node["title"] for node in levels[0]],
            ["First", "Second"],
        )
        self.assertEqual(
            [node["chunk_index"] for node in levels[0]],
            [0, 1],
        )

    @patch("representations.summaries.builder.save_levels")
    @patch("representations.summaries.builder.build_catalog_summary")
    @patch("representations.summaries.builder.build_document")
    @patch("representations.summaries.builder.load_documents")
    def test_summary_builder_reuses_existing_document(
        self,
        load_documents,
        build_document,
        build_catalog_summary,
        save_levels,
    ):
        from RAG_medils.ingest.representations.summaries.builder import run

        output_dir = self.data_root / "summaries"
        output_dir.mkdir()
        document_summary = {
            "node_id": "doc-summary",
            "text": "Summary",
            "level": 1,
            "scope": "document",
            "document_id": "doc",
            "catalog_id": "catalog",
            "source_document_ids": ["doc"],
        }
        catalog_summary = {
            "node_id": "catalog-summary",
            "text": "Catalog summary",
            "level": 2,
            "scope": "catalog",
            "document_id": None,
            "catalog_id": "catalog",
            "source_document_ids": ["doc"],
        }
        (output_dir / "level_1.json").write_text(
            json.dumps({"level": 1, "nodes": [document_summary]}),
            encoding="utf-8",
        )
        level_zero = {
            "node_id": "chunk-id",
            "text": "Text",
            "level": 0,
            "scope": "passage",
            "document_id": "doc",
            "catalog_id": "catalog",
            "source_node_ids": [],
            "source_chunk_ids": ["chunk-id"],
            "source_document_ids": ["doc"],
        }
        (output_dir / "level_0.json").write_text(
            json.dumps({"level": 0, "nodes": [level_zero]}),
            encoding="utf-8",
        )
        (output_dir / "level_2.json").write_text(
            json.dumps({"level": 2, "nodes": [catalog_summary]}),
            encoding="utf-8",
        )
        load_documents.return_value = [{
            "document_id": "doc",
            "catalog_id": "catalog",
            "chunks": [],
        }]

        run(self.data_root, skip_existing=True)

        build_document.assert_not_called()
        build_catalog_summary.assert_not_called()
        save_levels.assert_called_once()

    @patch("representations.summaries.builder.save_levels")
    @patch("representations.summaries.builder.build_catalog_summary")
    @patch("representations.summaries.builder.build_document")
    @patch("representations.summaries.builder.load_documents")
    def test_summary_builder_rebuilds_hierarchy_without_level_zero(
        self,
        load_documents,
        build_document,
        build_catalog_summary,
        save_levels,
    ):
        from RAG_medils.ingest.representations.summaries.builder import run

        output_dir = self.data_root / "summaries"
        output_dir.mkdir()
        old_document_summary = {
            "node_id": "old-document-summary",
            "text": "Old summary",
            "level": 1,
            "scope": "document",
            "document_id": "doc",
            "catalog_id": "catalog",
            "source_document_ids": ["doc"],
        }
        (output_dir / "level_1.json").write_text(
            json.dumps({"level": 1, "nodes": [old_document_summary]}),
            encoding="utf-8",
        )

        document = {
            "document_id": "doc",
            "catalog_id": "catalog",
            "chunks": [{"content": "Text"}],
        }
        new_document_summary = {
            "node_id": "new-document-summary",
            "document_id": "doc",
            "catalog_id": "catalog",
            "embedding": [0.1],
        }
        load_documents.return_value = [document]
        build_document.return_value = (
            {0: [{"node_id": "chunk"}], 1: [new_document_summary]},
            new_document_summary,
        )
        build_catalog_summary.return_value = {"node_id": "catalog-summary"}

        run(self.data_root, skip_existing=True)

        self.assertEqual(
            load_documents.call_args.kwargs["skip_document_ids"],
            set(),
        )
        build_document.assert_called_once_with(document)
        build_catalog_summary.assert_called_once()
        save_levels.assert_called_once()

    @patch("representations.summaries.builder.save_levels")
    @patch("representations.summaries.builder.build_catalog_summary")
    @patch("representations.summaries.builder.build_document")
    @patch("representations.summaries.builder.load_documents")
    def test_summary_builder_processes_documents_concurrently(
        self,
        load_documents,
        build_document,
        build_catalog_summary,
        save_levels,
    ):
        from RAG_medils.ingest.representations.summaries.builder import run

        documents = [
            {"document_id": "doc-1", "catalog_id": "catalog"},
            {"document_id": "doc-2", "catalog_id": "catalog"},
        ]
        load_documents.return_value = documents
        barrier = Barrier(2)

        def build(document):
            barrier.wait(timeout=5)
            summary = {
                "node_id": f"{document['document_id']}-summary",
                "document_id": document["document_id"],
                "catalog_id": document["catalog_id"],
                "embedding": [0.1],
            }
            return {1: [summary]}, summary

        build_document.side_effect = build
        build_catalog_summary.return_value = {"node_id": "catalog-summary"}

        run(self.data_root)

        self.assertEqual(build_document.call_count, 2)
        saved_levels = save_levels.call_args.args[0]
        self.assertEqual(
            [node["node_id"] for node in saved_levels[1]],
            ["doc-1-summary", "doc-2-summary"],
        )

    @patch("representations.summaries.builder.create_summary_node")
    @patch("representations.summaries.builder.perform_clustering")
    def test_cluster_summaries_are_created_concurrently(
        self,
        perform_clustering,
        create_summary_node,
    ):
        from RAG_medils.ingest.representations.summaries.builder import create_cluster_summaries

        nodes = [
            {"node_id": "node-1", "embedding": [0.1]},
            {"node_id": "node-2", "embedding": [0.2]},
        ]
        perform_clustering.return_value = [[0], [1]]
        barrier = Barrier(2)

        def create(**kwargs):
            barrier.wait(timeout=5)
            return {"node_id": kwargs["node_id"]}

        create_summary_node.side_effect = create

        summaries = create_cluster_summaries(
            nodes,
            document_id="doc",
            catalog_id="catalog",
            level=1,
        )

        self.assertEqual(
            [summary["node_id"] for summary in summaries],
            ["doc_L1_C0", "doc_L1_C1"],
        )

if __name__ == "__main__":
    unittest.main()
