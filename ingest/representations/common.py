"""Shared types for representation builders."""

from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DocumentInput:
    """A registered document and the Markdown used to represent it."""

    id: UUID
    source_key: str
    markdown_path: Path
    catalog_id: str
    title: str
    has_summary: bool = False


@dataclass(frozen=True, slots=True)
class StageResult:
    """Summary returned by one representation stage."""

    stage: str
    duration_seconds: float
    counts: dict[str, int] = field(default_factory=dict)
