"""Load and validate representation files before database ingestion."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5


ScalarMetadata = str | int | float | bool | None

DOCUMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/sql-rag/documents",
)
ARGUMENT_ID_PATTERN = re.compile(
    r"^(?P<document>.+)_chunk_(?P<chunk>[1-9][0-9]*)_arg_[1-9][0-9]*$"
)
SUMMARY_SCOPES = {"document_cluster", "document", "catalog"}
CHUNK_FIELDS = {
    "chunk_list",
    "chunk_title",
    "token_count",
    "chunk_language",
    "chunk_size",
    "output_path",
}


class InputValidationError(ValueError):
    """Raised when representation data has an invalid shape or reference."""


class FolderScanError(RuntimeError):
    """Raised when the required input directory cannot be scanned."""


@dataclass(frozen=True, slots=True)
class PreparedChunk:
    chunk_index: int
    content: str
    title: str | None
    token_count: int | None
    content_hash: str


@dataclass(frozen=True, slots=True)
class PreparedArgument:
    id: str
    chunk_index: int
    claim: str
    evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PreparedEntityBundle:
    chunk_index: int
    entities: tuple[dict[str, Any], ...]
    relations: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class PreparedDocument:
    id: UUID
    source_key: str
    name: str
    title: str
    json_path: str
    pdf_path: str | None
    language: str | None
    json_hash: str
    pdf_hash: str | None
    metadata: dict[str, ScalarMetadata]
    chunks: tuple[PreparedChunk, ...]
    argument_chunks: tuple[PreparedChunk, ...]
    arguments: tuple[PreparedArgument, ...]
    entity_bundles: tuple[PreparedEntityBundle, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PreparedSummary:
    node_id: str
    summary_text: str
    level: int
    scope: str
    document_id: UUID | None
    catalog_id: str
    source_node_ids: tuple[str, ...]
    source_chunk_ids: tuple[str, ...]
    source_document_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PreparedDataset:
    documents: tuple[PreparedDocument, ...]
    summaries: tuple[PreparedSummary, ...]


@dataclass(frozen=True, slots=True)
class _ChunkData:
    chunks: tuple[PreparedChunk, ...]
    language: str | None
    metadata: dict[str, ScalarMetadata]
    raw: dict[str, Any]


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(f"{field} must be a non-blank string")
    return value.strip()


def _optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise InputValidationError(f"{field} must be a string or null")
    return value.strip() or None


def _load_json(path: Path) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON number: {value}")

    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise InputValidationError(f"{path}: invalid JSON: {exc}") from exc


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_json(data: Any) -> str:
    canonical = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return _sha256(canonical.encode("utf-8"))


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def build_chunk_id(
    document_id: UUID,
    document_version: int,
    chunk_index: int,
    content_hash: str,
    *,
    representation: str = "passage",
) -> UUID:
    """Build stable IDs and preserve the original passage-ID algorithm."""

    if document_version <= 0:
        raise ValueError("document_version must be positive")
    if chunk_index < 0:
        raise ValueError("chunk_index must be nonnegative")
    if representation not in {"passage", "argument"}:
        raise ValueError(f"unknown chunk representation: {representation}")

    identity = f"{document_version}:{chunk_index}:{content_hash}"
    if representation == "argument":
        identity = f"argument:{identity}"
    return uuid5(document_id, identity)


def build_entity_bundle_id(chunk_id: UUID) -> UUID:
    return uuid5(chunk_id, "entities")


def _parallel_array(
    data: dict[str, Any],
    field: str,
    count: int,
) -> list[Any]:
    if field not in data:
        return [None] * count
    value = data[field]
    if not isinstance(value, list):
        raise InputValidationError(f"{field} must be an array")
    if len(value) != count:
        raise InputValidationError(
            f"{field} has {len(value)} items; expected {count}"
        )
    return value


def _optional_integer(
    value: object,
    field: str,
    *,
    positive: bool,
) -> int | None:
    if value is None:
        return None
    valid = _is_integer(value) and (
        value > 0 if positive else value >= 0
    )
    if not valid:
        description = "positive" if positive else "nonnegative"
        raise InputValidationError(
            f"{field} must be a {description} integer or null"
        )
    return value


def _parse_chunks(path: Path) -> _ChunkData:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise InputValidationError(
            f"{path}: top-level value must be an object"
        )
    contents = data.get("chunk_list")
    if not isinstance(contents, list) or not contents:
        raise InputValidationError(
            f"{path}: chunk_list must be a non-empty array"
        )

    count = len(contents)
    declared_count = data.get("chunk_size")
    if declared_count is not None and (
        not _is_integer(declared_count)
        or declared_count != count
    ):
        raise InputValidationError(
            f"{path}: chunk_size must equal {count}"
        )

    titles = _parallel_array(data, "chunk_title", count)
    tokens = _parallel_array(data, "token_count", count)
    chunks: list[PreparedChunk] = []
    for index, raw_content in enumerate(contents):
        content = _text(
            raw_content,
            f"{path}: chunk_list[{index}]",
        )
        chunks.append(
            PreparedChunk(
                chunk_index=index,
                content=content,
                title=_optional_text(
                    titles[index],
                    f"{path}: chunk_title[{index}]",
                ),
                token_count=_optional_integer(
                    tokens[index],
                    f"{path}: token_count[{index}]",
                    positive=False,
                ),
                content_hash=_sha256(content.encode("utf-8")),
            )
        )

    metadata: dict[str, ScalarMetadata] = {
        key: value
        for key, value in data.items()
        if key not in CHUNK_FIELDS
        and (
            value is None
            or isinstance(value, (str, int, float, bool))
        )
    }
    output_path = _optional_text(
        data.get("output_path"),
        f"{path}: output_path",
    )
    if output_path is not None:
        metadata["output_path"] = output_path

    return _ChunkData(
        chunks=tuple(chunks),
        language=_optional_text(
            data.get("chunk_language"),
            f"{path}: chunk_language",
        ),
        metadata=metadata,
        raw=data,
    )


def _discover(
    root: Path,
    pattern: str,
    *,
    required: bool = False,
) -> tuple[Path, ...]:
    if not root.exists():
        if required:
            raise FolderScanError(
                f"input directory does not exist: {root}"
            )
        return ()
    if not root.is_dir():
        raise FolderScanError(
            f"input path is not a directory: {root}"
        )
    files = tuple(sorted(
        path for path in root.rglob(pattern) if path.is_file()
    ))
    if required and not files:
        raise FolderScanError(
            f"no {pattern} files found in {root}"
        )
    return files


def _source_key(
    path: Path,
    root: Path,
    suffix: str,
) -> tuple[str, str, Path]:
    relative = path.resolve().relative_to(root.resolve())
    if not relative.name.endswith(suffix):
        raise InputValidationError(
            f"{relative} does not end with {suffix}"
        )
    name = relative.name.removesuffix(suffix)
    if not name:
        raise InputValidationError(
            f"{relative} has an empty document name"
        )
    return (
        (relative.parent / name).as_posix(),
        name,
        relative.parent,
    )


def _index_files(
    root: Path,
    pattern: str,
    suffix: str,
) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in _discover(root, pattern):
        source_key, _, _ = _source_key(path, root, suffix)
        if source_key in result:
            raise InputValidationError(
                f"duplicate source key {source_key} under {root}"
            )
        result[source_key] = path
    return result


def _parse_arguments(
    path: Path,
    document_name: str,
    chunk_count: int,
    seen_ids: set[str],
) -> tuple[PreparedArgument, ...]:
    data = _load_json(path)
    if not isinstance(data, list):
        raise InputValidationError(
            f"{path}: top-level value must be an array"
        )

    prepared: list[PreparedArgument] = []
    for position, item in enumerate(data):
        if not isinstance(item, dict):
            raise InputValidationError(
                f"{path}: item {position} must be an object"
            )
        argument_id = _text(
            item.get("id"),
            f"{path}: item {position}.id",
        )
        if argument_id in seen_ids:
            raise InputValidationError(
                f"duplicate argument id: {argument_id}"
            )
        seen_ids.add(argument_id)

        match = ARGUMENT_ID_PATTERN.fullmatch(argument_id)
        if (
            match is None
            or match.group("document") != document_name
        ):
            raise InputValidationError(
                f"{path}: argument id {argument_id!r} "
                f"does not match document {document_name!r}"
            )
        chunk_index = int(match.group("chunk")) - 1
        if chunk_index >= chunk_count:
            raise InputValidationError(
                f"{path}: {argument_id} references missing "
                f"chunk {chunk_index + 1}"
            )

        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            raise InputValidationError(
                f"{path}: {argument_id}.evidence must be an array"
            )
        prepared.append(
            PreparedArgument(
                id=argument_id,
                chunk_index=chunk_index,
                claim=_text(
                    item.get("claim"),
                    f"{path}: {argument_id}.claim",
                ),
                evidence=tuple(
                    _text(
                        value,
                        f"{path}: {argument_id}.evidence",
                    )
                    for value in evidence
                ),
            )
        )
    return tuple(prepared)


def _parse_entities(
    path: Path,
    chunk_count: int,
) -> tuple[PreparedEntityBundle, ...]:
    data = _load_json(path)
    if not isinstance(data, list):
        raise InputValidationError(
            f"{path}: top-level value must be an array"
        )

    prepared: list[PreparedEntityBundle] = []
    seen_chunks: set[int] = set()
    for position, item in enumerate(data):
        if not isinstance(item, dict):
            raise InputValidationError(
                f"{path}: item {position} must be an object"
            )
        chunk_index = item.get("chunk_id")
        if (
            not _is_integer(chunk_index)
            or not 0 <= chunk_index < chunk_count
        ):
            raise InputValidationError(
                f"{path}: item {position}.chunk_id must reference "
                "an existing zero-based chunk"
            )
        if chunk_index in seen_chunks:
            raise InputValidationError(
                f"{path}: duplicate entity bundle for chunk "
                f"{chunk_index}"
            )
        seen_chunks.add(chunk_index)

        entities = item.get("entities")
        relations = item.get("relations")
        if not isinstance(entities, list) or not isinstance(relations, list):
            raise InputValidationError(
                f"{path}: chunk {chunk_index} entities and "
                "relations must be arrays"
            )

        entity_ids: set[str] = set()
        for entity_position, entity in enumerate(entities):
            if not isinstance(entity, dict):
                raise InputValidationError(
                    f"{path}: entity {entity_position} must be an object"
                )
            entity_id = _text(
                entity.get("id"),
                f"{path}: chunk {chunk_index} entity id",
            )
            if entity_id in entity_ids:
                raise InputValidationError(
                    f"{path}: duplicate entity id {entity_id} "
                    f"in chunk {chunk_index}"
                )
            entity_ids.add(entity_id)
            _text(entity.get("name"), f"{path}: {entity_id}.name")
            _text(entity.get("type"), f"{path}: {entity_id}.type")

        for relation_position, relation in enumerate(relations):
            if not isinstance(relation, dict):
                raise InputValidationError(
                    f"{path}: relation {relation_position} "
                    "must be an object"
                )
            subject = _text(
                relation.get("subject_id"),
                f"{path}: relation subject_id",
            )
            object_id = _text(
                relation.get("object_id"),
                f"{path}: relation object_id",
            )
            _text(
                relation.get("relation"),
                f"{path}: relation name",
            )
            if subject not in entity_ids or object_id not in entity_ids:
                raise InputValidationError(
                    f"{path}: chunk {chunk_index} relation "
                    "references an unknown entity"
                )
            confidence = relation.get("confidence")
            if confidence is not None and (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not 0 <= confidence <= 1
            ):
                raise InputValidationError(
                    f"{path}: relation confidence must be "
                    "between 0 and 1"
                )
            if (
                "negated" in relation
                and not isinstance(relation["negated"], bool)
            ):
                raise InputValidationError(
                    f"{path}: relation negated must be boolean"
                )
            if (
                "qualifiers" in relation
                and not isinstance(relation["qualifiers"], dict)
            ):
                raise InputValidationError(
                    f"{path}: relation qualifiers must be an object"
                )

        prepared.append(
            PreparedEntityBundle(
                chunk_index=chunk_index,
                entities=tuple(entities),
                relations=tuple(relations),
            )
        )
    return tuple(prepared)


def _string_array(
    value: object,
    field: str,
) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise InputValidationError(f"{field} must be an array")
    result = tuple(_text(item, field) for item in value)
    if len(result) != len(set(result)):
        raise InputValidationError(
            f"{field} must not contain duplicates"
        )
    return result


def _parse_summaries(
    root: Path,
) -> tuple[PreparedSummary, ...]:
    prepared: list[PreparedSummary] = []
    seen_ids: set[str] = set()

    for path in _discover(root, "level_*.json"):
        match = re.fullmatch(
            r"level_([1-9][0-9]*)\.json",
            path.name,
        )
        if match is None:
            continue
        file_level = int(match.group(1))
        data = _load_json(path)
        if (
            not isinstance(data, dict)
            or data.get("level") != file_level
        ):
            raise InputValidationError(
                f"{path}: top-level level must match its filename"
            )
        nodes = data.get("nodes")
        if not isinstance(nodes, list):
            raise InputValidationError(
                f"{path}: nodes must be an array"
            )

        for position, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise InputValidationError(
                    f"{path}: node {position} must be an object"
                )
            node_id = _text(
                node.get("node_id"),
                f"{path}: node_id",
            )
            if node_id in seen_ids:
                raise InputValidationError(
                    f"duplicate summary node_id: {node_id}"
                )
            seen_ids.add(node_id)

            level = node.get("level")
            if not _is_integer(level) or level != file_level:
                raise InputValidationError(
                    f"{path}: {node_id}.level must equal "
                    f"{file_level}"
                )
            scope = _text(
                node.get("scope"),
                f"{path}: {node_id}.scope",
            )
            if scope not in SUMMARY_SCOPES:
                raise InputValidationError(
                    f"{path}: invalid summary scope {scope}"
                )

            raw_document_id = node.get("document_id")
            try:
                document_id = (
                    None
                    if raw_document_id is None
                    else UUID(_text(
                        raw_document_id,
                        f"{path}: {node_id}.document_id",
                    ))
                )
            except ValueError as exc:
                raise InputValidationError(
                    f"{path}: {node_id}.document_id must "
                    "be a UUID or null"
                ) from exc
            if (
                (scope == "catalog" and document_id is not None)
                or (scope != "catalog" and document_id is None)
            ):
                raise InputValidationError(
                    f"{path}: {node_id} has an invalid "
                    "document_id for its scope"
                )

            prepared.append(
                PreparedSummary(
                    node_id=node_id,
                    summary_text=_text(
                        node.get("text"),
                        f"{path}: {node_id}.text",
                    ),
                    level=level,
                    scope=scope,
                    document_id=document_id,
                    catalog_id=_text(
                        node.get("catalog_id"),
                        f"{path}: {node_id}.catalog_id",
                    ),
                    source_node_ids=_string_array(
                        node.get("source_node_ids"),
                        f"{path}: {node_id}.source_node_ids",
                    ),
                    source_chunk_ids=_string_array(
                        node.get("source_chunk_ids"),
                        f"{path}: {node_id}.source_chunk_ids",
                    ),
                    source_document_ids=_string_array(
                        node.get("source_document_ids"),
                        f"{path}: {node_id}.source_document_ids",
                    ),
                )
            )
    return tuple(prepared)


def prepare_dataset(data_root: Path) -> PreparedDataset:
    """Read and structurally validate the complete input snapshot."""

    data_root = data_root.resolve()
    if not data_root.is_dir():
        raise FolderScanError(
            f"data directory does not exist: {data_root}"
        )

    passages_root = data_root / "passages_chunk"
    argument_chunks_root = (
        data_root / "arguments" / "chunks_for_arguments"
    )
    arguments_root = (
        data_root / "arguments" / "arguments_extracted"
    )
    entities_root = data_root / "entities"

    passage_paths = _discover(
        passages_root,
        "*_chunks.json",
        required=True,
    )
    argument_chunk_files = _index_files(
        argument_chunks_root,
        "*_chunks.json",
        "_chunks.json",
    )
    argument_files = _index_files(
        arguments_root,
        "*_arguments.json",
        "_arguments.json",
    )
    entity_files = _index_files(
        entities_root,
        "*_chunks_entities.json",
        "_chunks_entities.json",
    )

    documents: list[PreparedDocument] = []
    passage_keys: set[str] = set()
    seen_argument_ids: set[str] = set()

    for passage_path in passage_paths:
        source_key, name, relative_parent = _source_key(
            passage_path,
            passages_root,
            "_chunks.json",
        )
        if source_key in passage_keys:
            raise InputValidationError(
                f"duplicate passage source key: {source_key}"
            )
        passage_keys.add(source_key)
        passage = _parse_chunks(passage_path)
        document_id = uuid5(DOCUMENT_NAMESPACE, source_key)

        expected_pdf = (
            data_root / "pdf_docs" / relative_parent / f"{name}.pdf"
        )
        if expected_pdf.exists() and not expected_pdf.is_file():
            raise InputValidationError(
                f"expected PDF path is not a file: {expected_pdf}"
            )
        if expected_pdf.is_file():
            pdf_path = str(expected_pdf.resolve())
            pdf_hash = _hash_file(expected_pdf)
            warnings: tuple[str, ...] = ()
        else:
            pdf_path = None
            pdf_hash = None
            warnings = (f"PDF not found: {expected_pdf}",)

        argument_chunks = (
            _parse_chunks(argument_chunk_files[source_key]).chunks
            if source_key in argument_chunk_files
            else ()
        )
        if source_key in argument_files and not argument_chunks:
            raise InputValidationError(
                f"{argument_files[source_key]} has no matching "
                "argument chunk file"
            )
        if source_key in entity_files and not argument_chunks:
            raise InputValidationError(
                f"{entity_files[source_key]} has no matching "
                "argument chunk file"
            )

        documents.append(
            PreparedDocument(
                id=document_id,
                source_key=source_key,
                name=name,
                title=name,
                json_path=str(passage_path.resolve()),
                pdf_path=pdf_path,
                language=passage.language,
                json_hash=_hash_json(passage.raw),
                pdf_hash=pdf_hash,
                metadata=passage.metadata,
                chunks=passage.chunks,
                argument_chunks=argument_chunks,
                arguments=(
                    _parse_arguments(
                        argument_files[source_key],
                        name,
                        len(argument_chunks),
                        seen_argument_ids,
                    )
                    if source_key in argument_files
                    else ()
                ),
                entity_bundles=(
                    _parse_entities(
                        entity_files[source_key],
                        len(argument_chunks),
                    )
                    if source_key in entity_files
                    else ()
                ),
                warnings=warnings,
            )
        )

    for label, indexed in (
        ("argument chunk", argument_chunk_files),
        ("argument", argument_files),
        ("entity", entity_files),
    ):
        orphaned = sorted(set(indexed) - passage_keys)
        if orphaned:
            raise InputValidationError(
                f"orphan {label} files without passages: "
                f"{', '.join(orphaned)}"
            )

    return PreparedDataset(
        documents=tuple(sorted(
            documents,
            key=lambda item: item.source_key,
        )),
        summaries=_parse_summaries(
            data_root / "summaries"
        ),
    )


def validate_summary_references(
    dataset: PreparedDataset,
    document_versions: dict[str, int],
) -> None:
    """Validate summary provenance against IDs about to be stored."""

    document_ids = {
        str(document.id)
        for document in dataset.documents
    }
    passage_ids = {
        str(build_chunk_id(
            document.id,
            document_versions[document.source_key],
            chunk.chunk_index,
            chunk.content_hash,
        ))
        for document in dataset.documents
        for chunk in document.chunks
    }
    summaries_by_id = {
        summary.node_id: summary
        for summary in dataset.summaries
    }

    for summary in dataset.summaries:
        if (
            summary.document_id is not None
            and str(summary.document_id) not in document_ids
        ):
            raise InputValidationError(
                f"summary {summary.node_id} references unknown "
                f"document {summary.document_id}"
            )
        unknown_documents = (
            set(summary.source_document_ids) - document_ids
        )
        if unknown_documents:
            raise InputValidationError(
                f"summary {summary.node_id} has unknown source "
                f"documents: {', '.join(sorted(unknown_documents))}"
            )
        unknown_chunks = (
            set(summary.source_chunk_ids) - passage_ids
        )
        if unknown_chunks:
            raise InputValidationError(
                f"summary {summary.node_id} has unknown source "
                f"chunks: {', '.join(sorted(unknown_chunks))}"
            )

        for source_node_id in summary.source_node_ids:
            if source_node_id in passage_ids:
                continue
            source_summary = summaries_by_id.get(source_node_id)
            if source_summary is None:
                raise InputValidationError(
                    f"summary {summary.node_id} references unknown "
                    f"source node {source_node_id}"
                )
            if source_summary.level >= summary.level:
                raise InputValidationError(
                    f"summary {summary.node_id} must reference a "
                    "lower-level source node"
                )
