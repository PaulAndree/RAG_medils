import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import uuid5

from RAG_medils.ingest.stores.ingestion import (
    DOCUMENT_NAMESPACE,
    InputValidationError,
    prepare_document,
    prepare_summaries,
    validate_summary_references,
)


def write_raptor_fixture(root: Path, *, source_key="paper", document_id=None, catalog_id="catalog") -> str:
    markdown_dir = root / "pdf_parsed_output"
    summaries_dir = root / "summaries"
    markdown_dir.mkdir(parents=True, exist_ok=True)
    summaries_dir.mkdir(exist_ok=True)
    markdown_path = markdown_dir / f"{source_key}.md"
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        "# Paper\n\nOriginal content.",
        encoding="utf-8",
    )

    document_id = str(document_id or uuid5(DOCUMENT_NAMESPACE, source_key))
    chunk_id = f"{document_id}:chunk-0"
    level_zero = {
        "node_id": chunk_id,
        "text": "Original content.",
        "level": 0,
        "scope": "passage",
        "document_id": document_id,
        "document_title": "Document title",
        "catalog_id": catalog_id,
        "source_key": source_key,
        "chunk_index": 0,
        "title": "Paper",
        "token_count": 2,
        "source_node_ids": [],
        "source_chunk_ids": [chunk_id],
        "source_document_ids": [document_id],
    }
    document_summary = {
        "node_id": f"{document_id}:document-summary",
        "text": "Document summary.",
        "level": 1,
        "scope": "document",
        "document_id": document_id,
        "document_title": "Document title",
        "catalog_id": catalog_id,
        "source_node_ids": [chunk_id],
        "source_chunk_ids": [chunk_id],
        "source_document_ids": [document_id],
    }
    catalog_summary = {
        "node_id": f"{catalog_id}:catalog-summary",
        "text": "Catalog summary.",
        "level": 2,
        "scope": "catalog",
        "document_id": None,
        "document_title": None,
        "catalog_id": catalog_id,
        "source_node_ids": [document_summary["node_id"]],
        "source_chunk_ids": [chunk_id],
        "source_document_ids": [document_id],
    }
    for level, nodes in (
        (0, [level_zero]),
        (1, [document_summary]),
        (2, [catalog_summary]),
    ):
        (summaries_dir / f"level_{level}.json").write_text(
            json.dumps({"level": level, "nodes": nodes}),
            encoding="utf-8",
        )
    return document_id


class RaptorParsingTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        document_id = write_raptor_fixture(self.root)
        from uuid import UUID
        self.documents = {UUID(document_id): "paper"}

    def test_document_preparation_does_not_require_representations(self):
        import shutil
        shutil.rmtree(self.root / "summaries")
        document = prepare_document(
            self.root / "pdf_parsed_output/paper.md",
            {"title": "My title", "author": "Ada", "custom": {"tags": ["test"]}},
            tenant_id="company",
        )
        self.assertEqual(document.title, "My title")
        self.assertEqual(document.tenant_id, "company")
        self.assertEqual(document.metadata["custom"], {"tags": ["test"]})
        self.assertEqual(len(document.doc_hash), 64)

    def test_summaries_do_not_require_originals_or_markdown(self):
        import shutil
        shutil.rmtree(self.root / "pdf_parsed_output")
        summaries = prepare_summaries(self.root / "summaries")
        self.assertEqual(len(summaries), 3)
        validate_summary_references(summaries, self.documents)

    def test_unknown_source_chunk_is_rejected(self):
        summaries = list(prepare_summaries(self.root / "summaries"))
        summaries[1] = replace(summaries[1], source_chunk_ids=("missing",))
        with self.assertRaisesRegex(InputValidationError, "unknown source chunks"):
            validate_summary_references(tuple(summaries), self.documents)

    def test_document_title_is_distinct_from_passage_title(self):
        passage, document, catalog = prepare_summaries(self.root / "summaries")
        self.assertEqual(passage.document_title, "Document title")
        self.assertEqual(passage.title, "Paper")
        self.assertEqual(document.document_title, "Document title")
        self.assertIsNone(catalog.document_title)
        self.assertEqual({node.catalog_id for node in (passage, document, catalog)}, {"catalog"})

    def test_document_title_is_required_for_each_document_level(self):
        for level in (0, 1):
            path = self.root / "summaries" / f"level_{level}.json"
            original = path.read_text()
            for value in (None, "", "   ", 123, ["title"]):
                with self.subTest(level=level, value=value):
                    data = json.loads(original)
                    data["nodes"][0]["document_title"] = value
                    path.write_text(json.dumps(data))
                    with self.assertRaisesRegex(InputValidationError, "document_title"):
                        prepare_summaries(self.root / "summaries")
            path.write_text(original)

    def test_catalog_cannot_claim_one_document_title(self):
        path = self.root / "summaries" / "level_2.json"
        data = json.loads(path.read_text())
        data["nodes"][0]["document_title"] = "Misleading title"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(InputValidationError, "document_title must be null"):
            prepare_summaries(self.root / "summaries")

    def test_passage_requires_registered_source_key(self):
        summaries = list(prepare_summaries(self.root / "summaries"))
        summaries[0] = replace(summaries[0], source_key="different")
        with self.assertRaisesRegex(InputValidationError, "source_key"):
            validate_summary_references(tuple(summaries), self.documents)

    def test_passage_only_is_not_a_complete_representation(self):
        summaries = prepare_summaries(self.root / "summaries")
        with self.assertRaisesRegex(InputValidationError, "document summary"):
            validate_summary_references(summaries[:1], self.documents)

    def test_unknown_document_is_rejected(self):
        summaries = prepare_summaries(self.root / "summaries")
        with self.assertRaisesRegex(InputValidationError, "unknown document"):
            validate_summary_references(summaries, {})

    def test_document_summary_must_cover_all_passages(self):
        summaries = list(prepare_summaries(self.root / "summaries"))
        passage = replace(summaries[0], node_id="extra", chunk_index=1, source_chunk_ids=("extra",))
        with self.assertRaisesRegex(InputValidationError, "all passages"):
            validate_summary_references(tuple(summaries + [passage]), self.documents)

    def test_metadata_must_be_an_object_with_finite_values(self):
        from RAG_medils.ingest.stores.ingestion import validate_metadata
        for metadata in ([], {"number": float("nan")}, {"title": ["wrong"]}):
            with self.subTest(metadata=metadata), self.assertRaises(InputValidationError):
                validate_metadata(metadata)


if __name__ == "__main__":
    unittest.main()
