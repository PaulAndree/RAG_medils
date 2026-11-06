"""Load and validate representation files before database ingestion."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5


DOCUMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/sql-rag/documents",
)
SUMMARY_SCOPES = {"passage", "document_cluster", "document", "catalog"}


class InputValidationError(ValueError):
    """Raised when representation data has an invalid shape or reference."""


class FolderScanError(RuntimeError):
    """Raised when the required input directory cannot be scanned."""


@dataclass(frozen=True, slots=True)
class PreparedDocument:
    id: UUID
    source_key: str
    name: str
    title: str
    doc_path: str | None
    language: str | None
    doc_hash: str | None
    metadata: dict[str, Any]
    tenant_id: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PreparedSummary:
    node_id: str
    summary_text: str
    level: int
    scope: str
    document_id: UUID | None
    document_title: str | None
    catalog_id: str
    source_node_ids: tuple[str, ...]
    source_chunk_ids: tuple[str, ...]
    source_document_ids: tuple[str, ...]
    source_key: str | None = None
    chunk_index: int | None = None
    title: str | None = None
    token_count: int | None = None


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


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


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


def prepare_summaries(
    root: Path,
) -> tuple[PreparedSummary, ...]:
    prepared: list[PreparedSummary] = []
    seen_ids: set[str] = set()

    for path in _discover(root, "level_*.json", required=True):
        match = re.fullmatch(
            r"level_(0|[1-9][0-9]*)\.json",
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

            document_title = node.get("document_title")
            if scope == "catalog":
                if document_title is not None:
                    raise InputValidationError(
                        f"{path}: {node_id}.document_title must be null for catalog summaries"
                    )
            else:
                document_title = _text(
                    document_title,
                    f"{path}: {node_id}.document_title",
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
                    document_title=document_title,
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
                    source_key=_optional_text(
                        node.get("source_key"),
                        f"{path}: {node_id}.source_key",
                    ),
                    chunk_index=_optional_integer(
                        node.get("chunk_index"),
                        f"{path}: {node_id}.chunk_index",
                        positive=False,
                    ),
                    title=_optional_text(
                        node.get("title"),
                        f"{path}: {node_id}.title",
                    ),
                    token_count=_optional_integer(
                        node.get("token_count"),
                        f"{path}: {node_id}.token_count",
                        positive=False,
                    ),
                )
            )
    return tuple(prepared)


def validate_metadata(metadata: object) -> dict[str, Any]:
    """Accept JSON objects, preserving custom and nested metadata fields."""
    if not isinstance(metadata, dict):
        raise InputValidationError("metadata must be a JSON object")
    try:
        json.dumps(metadata, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise InputValidationError("metadata must contain valid JSON values") from exc
    for field in ("title", "language"):
        _optional_text(metadata.get(field), field)
    return dict(metadata)


def prepare_document(
    file_path: Path,
    metadata: Mapping[str, Any] | None = None,
    *,
    tenant_id: str | None = None,
    document_id: UUID | None = None,
    source_key: str | None = None,
) -> PreparedDocument:
    """Prepare an original file without requiring OCR or representations."""
    file_path = file_path.resolve()
    if not file_path.is_file() or file_path.stat().st_size == 0:
        raise InputValidationError("document must be a non-empty file")
    if file_path.suffix.lower() not in {".pdf", ".md"}:
        raise InputValidationError("only PDF and Markdown files are supported")
    if file_path.suffix.lower() == ".md":
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise InputValidationError("Markdown must use UTF-8 encoding") from exc
        if not content.strip():
            raise InputValidationError("Markdown must contain text")
    if tenant_id is not None:
        _text(tenant_id, "tenant_id")
    values = validate_metadata({} if metadata is None else dict(metadata))
    document_id = document_id or uuid4()
    return PreparedDocument(
        id=document_id,
        source_key=source_key or f"{document_id}/{file_path.stem}",
        name=file_path.name,
        title=_optional_text(values.get("title"), "title") or file_path.stem,
        doc_path=str(file_path),
        language=_optional_text(values.get("language"), "language"),
        doc_hash=_hash_file(file_path),
        metadata=values,
        tenant_id=tenant_id,
    )


def catalog_id_for_tenant(tenant_id: str) -> str:
    return f"tenant:{tenant_id}"


def validate_summary_references(
    summaries: tuple[PreparedSummary, ...],
    documents: Mapping[UUID, str],
) -> None:
    """Validate complete catalog hierarchies against registered IDs/source keys."""
    if not summaries:
        raise InputValidationError("no summary nodes found")
    document_ids = {str(document_id) for document_id in documents}
    nodes = {summary.node_id: summary for summary in summaries}
    if len(nodes) != len(summaries):
        raise InputValidationError("duplicate summary node_id")
    passage_ids = {node.node_id for node in summaries if node.scope == "passage"}
    by_document: dict[UUID, list[PreparedSummary]] = defaultdict(list)
    by_catalog: dict[str, list[PreparedSummary]] = defaultdict(list)

    for node in summaries:
        by_catalog[node.catalog_id].append(node)
        if node.document_id is not None:
            if str(node.document_id) not in document_ids:
                raise InputValidationError(
                    f"summary {node.node_id} references unknown document {node.document_id}"
                )
            by_document[node.document_id].append(node)
            if set(node.source_document_ids) != {str(node.document_id)}:
                raise InputValidationError(f"{node.node_id}: inconsistent document provenance")
        unknown = set(node.source_document_ids) - document_ids
        if unknown:
            raise InputValidationError(f"{node.node_id}: unknown source documents: {sorted(unknown)}")
        unknown = set(node.source_chunk_ids) - passage_ids
        if unknown:
            raise InputValidationError(f"{node.node_id}: unknown source chunks: {sorted(unknown)}")
        if node.scope == "passage":
            if node.level != 0 or node.source_key is None or node.chunk_index is None:
                raise InputValidationError(f"{node.node_id}: passage requires level 0, source_key and chunk_index")
            if node.source_key != documents[node.document_id]:
                raise InputValidationError(f"{node.node_id}: source_key does not match registered document")
            if node.source_node_ids or node.source_chunk_ids != (node.node_id,):
                raise InputValidationError(f"{node.node_id}: inconsistent passage provenance")
            continue
        if node.level == 0 or not node.source_node_ids:
            raise InputValidationError(f"{node.node_id}: summary must reference lower-level nodes")
        source_documents: set[str] = set()
        source_chunks: set[str] = set()
        for source_id in node.source_node_ids:
            source = nodes.get(source_id)
            if source is None:
                raise InputValidationError(f"{node.node_id}: unknown source node {source_id}")
            if source.level >= node.level or source.catalog_id != node.catalog_id:
                raise InputValidationError(f"{node.node_id}: source must be lower-level and in the same catalog")
            source_documents.update(source.source_document_ids)
            source_chunks.update(source.source_chunk_ids)
        if source_documents != set(node.source_document_ids) or source_chunks != set(node.source_chunk_ids):
            raise InputValidationError(f"{node.node_id}: provenance does not match source nodes")

    for document_id, document_nodes in by_document.items():
        passages = [node for node in document_nodes if node.scope == "passage"]
        roots = [node for node in document_nodes if node.scope == "document"]
        if not passages or len(roots) != 1:
            raise InputValidationError(f"{document_id}: require passages and exactly one document summary")
        if len({node.catalog_id for node in document_nodes}) != 1:
            raise InputValidationError(f"{document_id}: document spans multiple catalogs")
        if len({node.chunk_index for node in passages}) != len(passages):
            raise InputValidationError(f"{document_id}: duplicate chunk_index")
        if set(roots[0].source_chunk_ids) != {node.node_id for node in passages}:
            raise InputValidationError(f"{document_id}: document summary does not cover all passages")

    for catalog_id, catalog_nodes in by_catalog.items():
        roots = [node for node in catalog_nodes if node.scope == "catalog"]
        document_roots = {node.node_id for node in catalog_nodes if node.scope == "document"}
        if len(roots) != 1 or not document_roots or set(roots[0].source_node_ids) != document_roots:
            raise InputValidationError(f"{catalog_id}: require one catalog summary covering all document summaries")
