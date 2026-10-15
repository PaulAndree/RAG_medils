import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from representations.common import StageResult
from representations.main import (
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
                output = data_root / "passages_chunk" / f"{name}.txt"
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
        self.assertEqual(
            (self.data_root / "keep.txt").read_text(encoding="utf-8"),
            "keep",
        )
        self.assertFalse(any(self.data_root.rglob("old.txt")))

    def test_resume_mode_keeps_existing_outputs(self):
        existing = self.data_root / "passages_chunk" / "old.txt"

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
        invalid_target = self.data_root / "entities"
        shutil.rmtree(invalid_target)
        invalid_target.write_text("not a directory", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "not a directory"):
            clean_generated_outputs(self.data_root)

        self.assertTrue(
            (self.data_root / "passages_chunk" / "old.txt").exists()
        )

    def test_stage_failure_stops_pipeline_and_keeps_partial_outputs(self):
        calls = []

        def passages(data_root):
            calls.append("passages")
            (data_root / "passages_chunk" / "partial.json").write_text(
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
            (self.data_root / "passages_chunk" / "partial.json").exists()
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
        from representations.passages.builder import run

        pdf_dir = self.data_root / "pdf_docs"
        pdf_dir.mkdir()
        (pdf_dir / "paper.pdf").write_bytes(b"pdf")
        post.side_effect = [
            FakeResponse({"content_parsed": "# Title\n\nText"}),
            FakeResponse({
                "chunk_list": ["Text"],
                "chunk_size": 1,
                "chunk_title": ["Title"],
                "token_count": [1],
            }),
        ]

        result = run(self.data_root)

        self.assertEqual(result.counts, {"documents": 1, "chunks": 1})
        self.assertTrue((self.data_root / "pdf_parsed_output/paper.md").exists())
        output = json.loads(
            (self.data_root / "passages_chunk/paper_chunks.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(output["chunk_list"], ["Text"])

    @patch("representations.passages.builder.requests.post")
    def test_passage_builder_reuses_existing_outputs(self, post):
        from representations.passages.builder import run

        pdf_dir = self.data_root / "pdf_docs"
        markdown_dir = self.data_root / "pdf_parsed_output"
        chunks_dir = self.data_root / "passages_chunk"
        pdf_dir.mkdir()
        markdown_dir.mkdir()
        chunks_dir.mkdir()
        (pdf_dir / "paper.pdf").write_bytes(b"pdf")
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
        from representations.summaries.builder import run

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
        from representations.summaries.builder import run

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

if __name__ == "__main__":
    unittest.main()
