import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
from uuid import UUID, NAMESPACE_URL, uuid5

ScalarMetadata = str | int | float | bool | None

KNOWN_FIELDS = {
    "chunk_list",
    "chunk_title",
    "token_count",
    "page_start",
    "page_end",
    "chunk_language",
    "chunk_size",
    "output_path",
}


class InputValidationError(ValueError):
    """Raised when a chunk JSON file does not follow the expected format."""


@dataclass(frozen=True, slots=True)
class NormalizedChunk:
    content: str
    title: str | None
    token_count: int | None
    page_start: int | None
    page_end: int | None


@dataclass(frozen=True, slots=True)
class NormalizedDocument:
    chunks: tuple[NormalizedChunk, ...]
    language: str | None
    metadata: dict[str, ScalarMetadata]
    source_data: dict[str, Any]

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)



def _is_integer(value: object) -> bool:
    # bool is a subclass of int in Python, so reject it explicitly.
    return isinstance(value, int) and not isinstance(value, bool)


def _normalize_optional_text(
    value: object,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise InputValidationError(
            f"{field_name} must be a string or null"
        )

    normalized = value.strip()
    return normalized or None


def _get_optional_array(
    data: dict[str, Any],
    field_name: str,
    chunk_count: int,
) -> list[Any]:
    if field_name not in data:
        return [None] * chunk_count

    value = data[field_name]

    if not isinstance(value, list):
        raise InputValidationError(
            f"{field_name} must be an array when present"
        )

    if len(value) != chunk_count:
        raise InputValidationError(
            f"{field_name} has {len(value)} items; "
            f"expected {chunk_count}"
        )

    return value


def _normalize_token_count(
    value: object,
    index: int,
) -> int | None:
    if value is None:
        return None

    if not _is_integer(value) or value < 0:
        raise InputValidationError(
            f"token_count[{index}] must be a nonnegative integer or null"
        )

    return value


def _normalize_page_number(
    value: object,
    field_name: str,
    index: int,
) -> int | None:
    if value is None:
        return None

    if not _is_integer(value) or value <= 0:
        raise InputValidationError(
            f"{field_name}[{index}] must be a positive integer or null"
        )

    return value



def _build_metadata(
    data: dict[str, Any],
) -> dict[str, ScalarMetadata]:
    metadata: dict[str, ScalarMetadata] = {}

    output_path = _normalize_optional_text(
        data.get("output_path"),
        "output_path",
    )

    if output_path is not None:
        metadata["output_path"] = output_path

    for key, value in data.items():
        if key in KNOWN_FIELDS:
            continue

        # Retain scalar metadata, but do not duplicate arrays or objects.
        if value is None or isinstance(value, (str, int, float, bool)):
            metadata[key] = value

    return metadata


def normalize_document(
    data: object,
) -> NormalizedDocument:
    if not isinstance(data, dict):
        raise InputValidationError(
            "the top-level JSON value must be an object"
        )

    if "chunk_list" not in data:
        raise InputValidationError("chunk_list is required")

    chunk_list = data["chunk_list"]

    if not isinstance(chunk_list, list):
        raise InputValidationError("chunk_list must be an array")

    if not chunk_list:
        raise InputValidationError(
            "chunk_list must contain at least one chunk"
        )

    chunk_count = len(chunk_list)

    chunk_titles = _get_optional_array(
        data,
        "chunk_title",
        chunk_count,
    )
    token_counts = _get_optional_array(
        data,
        "token_count",
        chunk_count,
    )
    page_starts = _get_optional_array(
        data,
        "page_start",
        chunk_count,
    )
    page_ends = _get_optional_array(
        data,
        "page_end",
        chunk_count,
    )

    declared_chunk_count = data.get("chunk_size")

    if declared_chunk_count is not None:
        if not _is_integer(declared_chunk_count):
            raise InputValidationError(
                "chunk_size must be an integer"
            )

        if declared_chunk_count != chunk_count:
            raise InputValidationError(
                f"chunk_size is {declared_chunk_count}; "
                f"actual chunk count is {chunk_count}"
            )

    normalized_chunks = []

    for index, content in enumerate(chunk_list):
        if not isinstance(content, str):
            raise InputValidationError(
                f"chunk_list[{index}] must be a string"
            )

        if not content.strip():
            raise InputValidationError(
                f"chunk_list[{index}] must not be blank"
            )

        title = _normalize_optional_text(
            chunk_titles[index],
            f"chunk_title[{index}]",
        )
        token_count = _normalize_token_count(
            token_counts[index],
            index,
        )

        page_start = _normalize_page_number(
            page_starts[index],
            "page_start",
            index,
        )
        page_end = _normalize_page_number(
            page_ends[index],
            "page_end",
            index,
        )

        if (
            page_start is not None
            and page_end is not None
            and page_end < page_start
        ):
            raise InputValidationError(
                f"page range for chunk {index} is invalid: "
                f"{page_start} to {page_end}"
            )

        normalized_chunks.append(
            NormalizedChunk(
                content=content,
                title=title,
                token_count=token_count,
                page_start=page_start,
                page_end=page_end,
            )
        )

    language = _normalize_optional_text(
        data.get("chunk_language"),
        "chunk_language",
    )

    return NormalizedDocument(
        chunks=tuple(normalized_chunks),
        language=language,
        metadata=_build_metadata(data),
        source_data=data,
    )


def _reject_nonstandard_number(value: str) -> None:
    raise ValueError(f"non-standard JSON number: {value}")


def load_and_normalize_json(
    json_path: Path,
) -> NormalizedDocument:
    try:
        text = json_path.read_text(encoding="utf-8")
        data = json.loads(
            text,
            parse_constant=_reject_nonstandard_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise InputValidationError(
            f"{json_path}: invalid JSON: {exc}"
        ) from exc

    return normalize_document(data)

"""
################################
Identity and hashing
################################
"""

DOCUMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "https://learning-1.local/sql-rag/documents",
)


@dataclass(frozen=True, slots=True)
class PreparedChunk:
    chunk_index: int
    content: str
    title: str | None
    token_count: int | None
    page_start: int | None
    page_end: int | None
    content_hash: str


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
    warnings: tuple[str, ...]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def hash_canonical_json(data: dict[str, Any]) -> str:
    canonical_json = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    return _sha256_bytes(canonical_json.encode("utf-8"))


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            digest.update(block)

    return digest.hexdigest()


def derive_source_identity(
    json_path: Path,
    chunks_root: Path,
) -> tuple[str, str, Path]:
    resolved_json_path = json_path.resolve()
    resolved_chunks_root = chunks_root.resolve()

    try:
        relative_path = resolved_json_path.relative_to(
            resolved_chunks_root
        )
    except ValueError as exc:
        raise InputValidationError(
            f"{resolved_json_path} is outside the chunk root "
            f"{resolved_chunks_root}"
        ) from exc

    required_suffix = "_chunks.json"

    if not relative_path.name.endswith(required_suffix):
        raise InputValidationError(
            f"{relative_path} does not end with {required_suffix}"
        )

    document_name = relative_path.name.removesuffix(required_suffix)

    if not document_name:
        raise InputValidationError(
            f"{relative_path} has an empty document name"
        )

    source_key = (
        relative_path.parent / document_name
    ).as_posix()

    return source_key, document_name, relative_path.parent


def build_chunk_id(
    document_id: UUID,
    document_version: int,
    chunk_index: int,
    content_hash: str,
) -> UUID:
    if document_version <= 0:
        raise ValueError("document_version must be positive")

    if chunk_index < 0:
        raise ValueError("chunk_index must be nonnegative")

    identity = (
        f"{document_version}:"
        f"{chunk_index}:"
        f"{content_hash}"
    )

    return uuid5(document_id, identity)


def prepare_document(
    json_path: Path,
    chunks_root: Path,
    pdf_root: Path,
) -> PreparedDocument:
    resolved_json_path = json_path.resolve()
    resolved_pdf_root = pdf_root.resolve()

    source_key, document_name, relative_parent = (
        derive_source_identity(
            resolved_json_path,
            chunks_root,
        )
    )

    normalized = load_and_normalize_json(resolved_json_path)

    expected_pdf_path = (
        resolved_pdf_root
        / relative_parent
        / f"{document_name}.pdf"
    )

    warnings: list[str] = []

    if expected_pdf_path.exists() and not expected_pdf_path.is_file():
        raise InputValidationError(
            f"expected PDF path is not a file: {expected_pdf_path}"
        )

    if expected_pdf_path.is_file():
        pdf_path = str(expected_pdf_path)
        pdf_hash = hash_file(expected_pdf_path)
    else:
        pdf_path = None
        pdf_hash = None
        warnings.append(
            f"PDF not found: {expected_pdf_path}"
        )

    prepared_chunks = tuple(
        PreparedChunk(
            chunk_index=index,
            content=chunk.content,
            title=chunk.title,
            token_count=chunk.token_count,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            content_hash=_sha256_bytes(
                chunk.content.encode("utf-8")
            ),
        )
        for index, chunk in enumerate(normalized.chunks)
    )

    document_id = uuid5(
        DOCUMENT_NAMESPACE,
        source_key,
    )

    return PreparedDocument(
        id=document_id,
        source_key=source_key,
        name=document_name,
        title=document_name,
        json_path=str(resolved_json_path),
        pdf_path=pdf_path,
        language=normalized.language,
        json_hash=hash_canonical_json(
            normalized.source_data
        ),
        pdf_hash=pdf_hash,
        metadata=dict(normalized.metadata),
        chunks=prepared_chunks,
        warnings=tuple(warnings),
    )

"""
################################
Folder discovery
################################
"""

class FolderScanError(RuntimeError):
    """Raised when a chunk source directory cannot be scanned."""

def discover_chunk_files(
    chunks_root: Path,
) -> tuple[Path, ...]:
    resolved_root = chunks_root.resolve()

    if not resolved_root.exists():
        raise FolderScanError(
            f"chunk directory does not exist: {resolved_root}"
        )

    if not resolved_root.is_dir():
        raise FolderScanError(
            f"chunk path is not a directory: {resolved_root}"
        )

    discovered_files = sorted(
        (
            path
            for path in resolved_root.rglob("*_chunks.json")
            if path.is_file()
        ),
        key=lambda path: path.relative_to(
            resolved_root
        ).as_posix(),
    )

    if not discovered_files:
        raise FolderScanError(
            f"no *_chunks.json files found in {resolved_root}"
        )

    return tuple(discovered_files)