"""Shared types for representation builders."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class StageResult:
    """Summary returned by one representation stage."""

    stage: str
    duration_seconds: float
    counts: dict[str, int] = field(default_factory=dict)
