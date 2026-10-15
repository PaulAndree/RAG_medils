import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from stores.ingestion import (
    InputValidationError,
    build_chunk_id,
    prepare_dataset,
    validate_summary_references,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RepresentationParsingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = prepare_dataset(PROJECT_ROOT / "data")

    def test_current_data_counts_and_summary_references(self) -> None:
        document = self.dataset.documents[0]
        self.assertEqual(len(self.dataset.documents), 1)
        self.assertEqual(len(document.chunks), 37)
        self.assertEqual(len(document.argument_chunks), 28)
        self.assertEqual(len(document.arguments), 14)
        self.assertEqual(len(document.entity_bundles), 28)
        self.assertEqual(len(self.dataset.summaries), 25)

        validate_summary_references(
            self.dataset,
            {document.source_key: 1},
        )

    def test_chunk_namespaces_are_stable_and_distinct(self) -> None:
        document = self.dataset.documents[0]
        passage = document.chunks[0]
        argument = document.argument_chunks[0]

        passage_id = build_chunk_id(
            document.id,
            1,
            passage.chunk_index,
            passage.content_hash,
        )
        self.assertEqual(
            passage_id,
            build_chunk_id(
                document.id,
                1,
                passage.chunk_index,
                passage.content_hash,
            ),
        )
        self.assertNotEqual(
            passage_id,
            build_chunk_id(
                document.id,
                1,
                argument.chunk_index,
                argument.content_hash,
                representation="argument",
            ),
        )

    def test_missing_optional_representations_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            passages = root / "passages_chunk"
            passages.mkdir()
            (passages / "small_chunks.json").write_text(
                json.dumps({
                    "chunk_list": ["one valid chunk"],
                    "chunk_size": 1,
                    "page_start": ["ignored"],
                    "page_end": ["ignored"],
                }),
                encoding="utf-8",
            )

            dataset = prepare_dataset(root)
            document = dataset.documents[0]
            self.assertEqual(document.source_key, "small")
            self.assertEqual(document.argument_chunks, ())
            self.assertEqual(document.arguments, ())
            self.assertEqual(document.entity_bundles, ())
            self.assertEqual(dataset.summaries, ())
            self.assertFalse(hasattr(document.chunks[0], "page_start"))
            self.assertFalse(hasattr(document.chunks[0], "page_end"))

    def test_mismatched_parallel_chunk_array_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            passages = root / "passages_chunk"
            passages.mkdir()
            (passages / "bad_chunks.json").write_text(
                json.dumps({
                    "chunk_list": ["one", "two"],
                    "chunk_title": ["only one title"],
                }),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                InputValidationError,
                "chunk_title has 1 items",
            ):
                prepare_dataset(root)

    def test_unknown_summary_chunk_is_rejected(self) -> None:
        bad_summary = replace(
            self.dataset.summaries[0],
            source_chunk_ids=("missing-chunk",),
        )
        bad_dataset = replace(
            self.dataset,
            summaries=(bad_summary,) + self.dataset.summaries[1:],
        )
        document = bad_dataset.documents[0]

        with self.assertRaisesRegex(
            InputValidationError,
            "unknown source chunks",
        ):
            validate_summary_references(
                bad_dataset,
                {document.source_key: 1},
            )

    def test_duplicate_argument_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            passages = root / "passages_chunk"
            argument_chunks = (
                root / "arguments" / "chunks_for_arguments"
            )
            arguments = (
                root / "arguments" / "arguments_extracted"
            )
            passages.mkdir(parents=True)
            argument_chunks.mkdir(parents=True)
            arguments.mkdir(parents=True)
            chunk_data = {"chunk_list": ["a chunk"]}
            (passages / "doc_chunks.json").write_text(
                json.dumps(chunk_data),
                encoding="utf-8",
            )
            (argument_chunks / "doc_chunks.json").write_text(
                json.dumps(chunk_data),
                encoding="utf-8",
            )
            duplicate = {
                "id": "doc_chunk_1_arg_1",
                "claim": "claim",
                "evidence": [],
            }
            (arguments / "doc_arguments.json").write_text(
                json.dumps([duplicate, duplicate]),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                InputValidationError,
                "duplicate argument id",
            ):
                prepare_dataset(root)


if __name__ == "__main__":
    unittest.main()
