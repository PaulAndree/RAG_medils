"""Turn JSON corpus records into the text that is chunked and embedded.

* documents and chats  -> RAPTOR hierarchy (chats: all messages merged)
* emails, events, notes, tasks -> one independent unit with a plain-text
  metadata header above the body
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

CORPUS_FILES = {
    "chat": "chats.json",
    "document": "documents.json",
    "email": "emails.json",
    "event": "events.json",
    "note": "notes.json",
    "task": "tasks.json",
}
RAPTOR_TYPES = frozenset({"document", "chat"})
SINGLE_UNIT_TYPES = frozenset({"email", "event", "note", "task"})

# Leading "**Key:** value" lines that only repeat fields already in the header.
_REDUNDANT_PREAMBLE_KEYS = frozenset({
    "fecha", "asunto", "título", "titulo", "autor", "evento", "tarea", "creada por",
})
_PREAMBLE_LINE = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*?)\s*$")


def load_records(
    data_dir: Path,
    types: Iterable[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Read records of the selected types; ``limit`` applies per type."""

    selected = list(CORPUS_FILES) if types is None else list(types)
    unknown = set(selected) - set(CORPUS_FILES)
    if unknown:
        raise ValueError(f"unknown record types: {sorted(unknown)}")
    records: list[dict[str, Any]] = []
    for doc_type in selected:
        path = Path(data_dir) / CORPUS_FILES[doc_type]
        items = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError(f"{path}: expected a JSON array")
        records.extend(items[:limit] if limit is not None else items)
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("record ids must be unique across the corpus")
    return records


def is_single_unit(record: dict[str, Any]) -> bool:
    doc_type = record.get("type")
    if doc_type in SINGLE_UNIT_TYPES:
        return True
    if doc_type in RAPTOR_TYPES:
        return False
    raise ValueError(f"{record.get('id')}: unsupported type {doc_type!r}")


def _person(value: Any) -> str:
    if isinstance(value, dict):
        name, email = value.get("name"), value.get("email")
        if name and email:
            return f"{name} ({email})"
        status = value.get("status")
        if name and status:
            return f"{name} ({status})"
        return str(name or email or "")
    return str(value)


def _people(values: Any) -> str:
    if isinstance(values, list):
        return ", ".join(_person(value) for value in values)
    return _person(values)


def strip_redundant_preamble(body: str) -> str:
    """Drop leading bold "Key: value" lines that the header already carries."""

    lines = body.split("\n")
    index = 0
    kept: list[str] = []
    while index < len(lines):
        line = lines[index]
        match = _PREAMBLE_LINE.match(line.strip())
        if match is None:
            break
        if match.group(1).strip().lower() not in _REDUNDANT_PREAMBLE_KEYS:
            kept.append(line.rstrip())
        index += 1
    rest = "\n".join(lines[index:]).strip("\n")
    return "\n".join([*kept, "", rest]).strip() if kept else rest.strip()


def _unit_body(record: dict[str, Any]) -> str:
    content = record["content"]
    for key in ("body", "text", "description"):
        if isinstance(content.get(key), str):
            return content[key]
    raise ValueError(f"{record['id']}: no body/text/description in content")


def render_unit(record: dict[str, Any]) -> str:
    """Metadata header + body for email, event, note, and task records."""

    metadata = record.get("metadata") or {}
    content = record.get("content") or {}
    lines = [
        f"ID: {record['id']}",
        f"Type: {record['type']}",
        f"Title: {record.get('title', '')}",
        f"Language: {record.get('language', '')}",
        f"Tags: {', '.join(record.get('tags') or [])}",
        f"Created Date: {metadata.get('createdDateTime', '')}",
    ]
    doc_type = record["type"]
    if doc_type == "email":
        lines += [
            f"From: {_person(metadata.get('from', ''))}",
            f"To: {_people(metadata.get('to', []))}",
            f"Thread ID: {metadata.get('thread_id', '')}",
        ]
    elif doc_type == "event":
        lines += [
            f"Author: {metadata.get('author', '')}",
            f"Start: {content.get('start', '')}",
            f"End: {content.get('end', '')}",
            f"Location: {metadata.get('location', '')}",
            f"Attendees: {_people(metadata.get('attendees', []))}",
        ]
    elif doc_type == "note":
        lines.append(f"Author: {metadata.get('author', '')}")
    elif doc_type == "task":
        lines += [
            f"Author: {metadata.get('author', '')}",
            f"Assignee: {metadata.get('assignee', '')}",
            f"Status: {metadata.get('status', '')}",
        ]
    if record.get("related"):
        lines.append(f"Related: {', '.join(map(str, record['related']))}")
    lines.append("Body:")
    lines.append(strip_redundant_preamble(_unit_body(record)))
    return "\n".join(lines).strip() + "\n"


def _clock(timestamp: str) -> str:
    match = re.search(r"T(\d{2}:\d{2})", timestamp or "")
    return match.group(1) if match else (timestamp or "")


def render_chat(record: dict[str, Any]) -> str:
    """Merge all messages into one document, one ``[HH:MM] Author: text`` line each."""

    metadata = record.get("metadata") or {}
    messages = (record.get("content") or {}).get("messages") or []
    if not messages:
        raise ValueError(f"{record['id']}: chat has no messages")
    header = [
        f"# {record.get('title', record['id'])}",
        "",
        f"Participants: {', '.join(metadata.get('participants') or [])}",
        f"Date: {metadata.get('createdDateTime', '')}",
        "",
    ]
    body = [
        f"[{_clock(message.get('date', ''))}] {message.get('author', '')}: {message.get('message', '')}"
        for message in messages
    ]
    return "\n".join([*header, *body]).strip() + "\n"


def render_document(record: dict[str, Any]) -> str:
    text = (record.get("content") or {}).get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{record['id']}: document has no text")
    return text.strip() + "\n"


def render(record: dict[str, Any]) -> str:
    doc_type = record.get("type")
    if doc_type == "document":
        return render_document(record)
    if doc_type == "chat":
        return render_chat(record)
    if doc_type in SINGLE_UNIT_TYPES:
        return render_unit(record)
    raise ValueError(f"{record.get('id')}: unsupported type {doc_type!r}")


def document_metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Metadata stored in documents.metadata (JSONB) and copied to the payload.

    ``createdDateTime`` stays top-level so summary timestamps are filled in.
    """

    metadata = record.get("metadata") or {}
    return {
        "dataset_id": record["id"],
        "type": record.get("type"),
        "title": record.get("title") or record["id"],
        "language": record.get("language"),
        "tags": record.get("tags") or [],
        "related": record.get("related") or [],
        "createdDateTime": metadata.get("createdDateTime"),
        "metadata": metadata,
    }


def iter_rendered(records: Iterable[dict[str, Any]]) -> Iterator[tuple[dict[str, Any], str]]:
    for record in records:
        yield record, render(record)
