"""Normalize and validate one document's extracted graph."""

from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("GRAPH_MODEL", "qwen3:14b")
NUM_CTX = int(os.getenv("GRAPH_NUM_CTX", "16384"))
PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "document_normalization_sys.txt"
)
UPPER_SNAKE_CASE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
CERTAINTY_VALUES = {"certain", "probable", "uncertain"}
MIN_CONFIDENCE = 0.75


class GraphValidationError(ValueError):
    """Raised when extracted or normalized graph data is invalid."""


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GraphValidationError(f"{field} must be a non-blank string")
    return value.strip()


def _evidence_is_grounded(evidence: str, chunk_text: str) -> bool:
    if evidence in chunk_text:
        return True
    normalized_evidence = " ".join(evidence.split())
    normalized_chunk = " ".join(chunk_text.split())
    return normalized_evidence in normalized_chunk


def validate_document_graph(
    results: list[dict[str, Any]],
    chunk_texts: list[str],
    *,
    normalized: bool,
    check_references: bool = True,
) -> None:
    """Validate structure, references, evidence, and normalized labels."""

    if len(results) != len(chunk_texts):
        raise GraphValidationError(
            f"found {len(results)} extraction results for "
            f"{len(chunk_texts)} chunks"
        )

    for expected_chunk_id, (result, chunk_text) in enumerate(
        zip(results, chunk_texts, strict=True)
    ):
        if not isinstance(result, dict):
            raise GraphValidationError(
                f"chunk {expected_chunk_id} result must be an object"
            )
        if result.get("chunk_id") != expected_chunk_id:
            raise GraphValidationError(
                f"chunk {expected_chunk_id} has an invalid chunk_id"
            )

        entities = result.get("entities")
        relations = result.get("relations")
        if not isinstance(entities, list) or not isinstance(relations, list):
            raise GraphValidationError(
                f"chunk {expected_chunk_id} entities and relations "
                "must be arrays"
            )

        entity_ids: set[str] = set()
        for position, entity in enumerate(entities):
            if not isinstance(entity, dict):
                raise GraphValidationError(
                    f"chunk {expected_chunk_id} entity {position} "
                    "must be an object"
                )
            entity_id = _required_text(
                entity.get("id"),
                f"chunk {expected_chunk_id} entity {position}.id",
            )
            if entity_id in entity_ids:
                raise GraphValidationError(
                    f"chunk {expected_chunk_id} has duplicate entity "
                    f"ID {entity_id!r}"
                )
            entity_ids.add(entity_id)
            _required_text(
                entity.get("name"),
                f"chunk {expected_chunk_id} {entity_id}.name",
            )
            entity_type = _required_text(
                entity.get("type"),
                f"chunk {expected_chunk_id} {entity_id}.type",
            )
            if normalized and not UPPER_SNAKE_CASE.fullmatch(entity_type):
                raise GraphValidationError(
                    f"chunk {expected_chunk_id} {entity_id}.type "
                    f"{entity_type!r} must use UPPER_SNAKE_CASE"
                )

        relation_keys: set[tuple[Any, ...]] = set()
        for position, relation in enumerate(relations):
            prefix = f"chunk {expected_chunk_id} relation {position}"
            if not isinstance(relation, dict):
                raise GraphValidationError(f"{prefix} must be an object")

            subject_id = _required_text(
                relation.get("subject_id"),
                f"{prefix}.subject_id",
            )
            object_id = _required_text(
                relation.get("object_id"),
                f"{prefix}.object_id",
            )
            relation_name = _required_text(
                relation.get("relation"),
                f"{prefix}.relation",
            )
            if check_references and (
                subject_id not in entity_ids
                or object_id not in entity_ids
            ):
                raise GraphValidationError(
                    f"{prefix} references an unknown entity"
                )
            if normalized and not UPPER_SNAKE_CASE.fullmatch(relation_name):
                raise GraphValidationError(
                    f"{prefix}.relation {relation_name!r} must use "
                    "UPPER_SNAKE_CASE"
                )

            evidence = _required_text(
                relation.get("evidence"),
                f"{prefix}.evidence",
            )
            if normalized and not _evidence_is_grounded(
                evidence,
                chunk_text,
            ):
                raise GraphValidationError(
                    f"{prefix}.evidence is not grounded in the chunk"
                )

            confidence = relation.get("confidence")
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not 0 <= confidence <= 1
            ):
                raise GraphValidationError(
                    f"{prefix}.confidence must be between 0 and 1"
                )
            if not isinstance(relation.get("negated"), bool):
                raise GraphValidationError(
                    f"{prefix}.negated must be boolean"
                )
            if relation.get("certainty") not in CERTAINTY_VALUES:
                raise GraphValidationError(
                    f"{prefix}.certainty must be one of "
                    f"{sorted(CERTAINTY_VALUES)}"
                )
            qualifiers = relation.get("qualifiers")
            if not isinstance(qualifiers, dict):
                raise GraphValidationError(
                    f"{prefix}.qualifiers must be an object"
                )

            relation_key = (
                subject_id,
                relation_name,
                object_id,
                relation["negated"],
                json.dumps(qualifiers, sort_keys=True),
            )
            if relation_key in relation_keys:
                raise GraphValidationError(
                    f"{prefix} duplicates another relation in the chunk"
                )
            relation_keys.add(relation_key)


def _prune_unreferenced_entities(results: list[dict[str, Any]]) -> None:
    """Keep only entities that participate in a retained relation."""

    for result in results:
        referenced_ids = {
            relation[key]
            for relation in result["relations"]
            for key in ("subject_id", "object_id")
        }
        result["entities"] = [
            entity
            for entity in result["entities"]
            if entity["id"] in referenced_ids
        ]


def _prune_unknown_entity_relations(
    results: list[dict[str, Any]],
) -> None:
    """Remove relations whose subject or object was not extracted."""

    for result in results:
        entity_ids = {
            entity["id"]
            for entity in result["entities"]
        }
        result["relations"] = [
            relation
            for relation in result["relations"]
            if relation["subject_id"] in entity_ids
            and relation["object_id"] in entity_ids
        ]


def _fill_relation_defaults(results: list[dict[str, Any]]) -> None:
    """Fill representation defaults that do not change relation meaning."""

    for result in results:
        relations = result.get("relations")
        if not isinstance(relations, list):
            continue
        for relation in relations:
            if (
                isinstance(relation, dict)
                and relation.get("qualifiers") is None
            ):
                relation["qualifiers"] = {}


def _to_upper_snake_case(value: str) -> str:
    """Convert a model-produced label to deterministic UPPER_SNAKE_CASE."""

    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()


def _prune_low_confidence_relations(results: list[dict[str, Any]]) -> None:
    """Remove relations below the extraction confidence threshold."""

    for result in results:
        result["relations"] = [
            relation
            for relation in result["relations"]
            if relation["confidence"] >= MIN_CONFIDENCE
        ]


def _prune_ungrounded_relations(
    results: list[dict[str, Any]],
    chunk_texts: list[str],
) -> None:
    """Remove relations whose evidence is not present in the source chunk."""

    for result, chunk_text in zip(results, chunk_texts, strict=True):
        result["relations"] = [
            relation
            for relation in result["relations"]
            if _evidence_is_grounded(relation["evidence"], chunk_text)
        ]


def build_normalization_catalog(
    results: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[tuple[str, str], str], dict[str, str]]:
    """Build compact document-level entity and relation vocabularies."""

    entity_ids: dict[tuple[str, str], str] = {}
    relation_ids: dict[str, str] = {}
    entity_variants: list[dict[str, str]] = []
    relation_variants: list[dict[str, str]] = []

    for result in results:
        for entity in result["entities"]:
            key = (entity["name"].strip(), entity["type"].strip())
            if key not in entity_ids:
                mapping_id = f"ENTITY_{len(entity_ids) + 1}"
                entity_ids[key] = mapping_id
                entity_variants.append({
                    "mapping_id": mapping_id,
                    "name": key[0],
                    "type": key[1],
                })
        for relation in result["relations"]:
            name = relation["relation"].strip()
            if name not in relation_ids:
                mapping_id = f"RELATION_{len(relation_ids) + 1}"
                relation_ids[name] = mapping_id
                relation_variants.append({
                    "mapping_id": mapping_id,
                    "relation": name,
                })

    return (
        {
            "entity_variants": entity_variants,
            "relation_variants": relation_variants,
        },
        entity_ids,
        relation_ids,
    )


def _request_normalization(
    document_id: str,
    catalog: dict[str, Any],
) -> dict[str, Any]:
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "document_id": document_id,
                            **catalog,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
            "stream": False,
            "format": "json",
            "think": False,
            "options": {
                "temperature": 0,
                "num_ctx": NUM_CTX,
            },
        },
        timeout=(10, 900),
    )
    response.raise_for_status()
    content = response.json()["message"]["content"]
    try:
        data = json.loads(content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise GraphValidationError(
            "normalization model returned invalid JSON"
        ) from exc
    if not isinstance(data, dict):
        raise GraphValidationError(
            "normalization model response must be an object"
        )
    return data


def _mapping_by_id(
    values: object,
    expected_ids: set[str],
    label: str,
) -> dict[str, dict[str, Any]]:
    if not isinstance(values, list):
        raise GraphValidationError(
            f"normalization response {label} must be an array"
        )

    mappings: dict[str, dict[str, Any]] = {}
    for position, value in enumerate(values):
        if not isinstance(value, dict):
            raise GraphValidationError(
                f"normalization response {label}[{position}] "
                "must be an object"
            )
        mapping_id = _required_text(
            value.get("mapping_id"),
            f"normalization response {label}[{position}].mapping_id",
        )
        if mapping_id in mappings:
            raise GraphValidationError(
                f"normalization response repeats {mapping_id}"
            )
        mappings[mapping_id] = value

    actual_ids = set(mappings)
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        unknown = sorted(actual_ids - expected_ids)
        raise GraphValidationError(
            f"normalization response {label} mappings do not match; "
            f"missing={missing}, unknown={unknown}"
        )
    return mappings


def _apply_normalization(
    results: list[dict[str, Any]],
    response: dict[str, Any],
    entity_ids: dict[tuple[str, str], str],
    relation_ids: dict[str, str],
) -> None:
    entity_mappings = _mapping_by_id(
        response.get("entities"),
        set(entity_ids.values()),
        "entities",
    )
    relation_mappings = _mapping_by_id(
        response.get("relations"),
        set(relation_ids.values()),
        "relations",
    )

    for result in results:
        for entity in result["entities"]:
            original_name = entity["name"].strip()
            original_type = entity["type"].strip()
            mapping = entity_mappings[
                entity_ids[(original_name, original_type)]
            ]
            canonical_name = _required_text(
                mapping.get("canonical_name"),
                "canonical_name",
            )
            canonical_type = _required_text(
                mapping.get("canonical_type"),
                "canonical_type",
            )
            canonical_type = _to_upper_snake_case(canonical_type)
            if canonical_name != original_name:
                entity.setdefault("original_name", original_name)
            if canonical_type != original_type:
                entity.setdefault("original_type", original_type)
            entity["name"] = canonical_name
            entity["type"] = canonical_type

        for relation in result["relations"]:
            original_relation = relation["relation"].strip()
            mapping = relation_mappings[relation_ids[original_relation]]
            canonical_relation = _required_text(
                mapping.get("canonical_relation"),
                "canonical_relation",
            )
            canonical_relation = _to_upper_snake_case(canonical_relation)
            if canonical_relation != original_relation:
                relation.setdefault(
                    "original_relation",
                    original_relation,
                )
            relation["relation"] = canonical_relation


def normalize_document_graph(
    results: list[dict[str, Any]],
    chunk_texts: list[str],
    document_id: str,
) -> list[dict[str, Any]]:
    """Normalize one document while preserving local IDs and provenance."""

    normalized_results = copy.deepcopy(results)
    _fill_relation_defaults(normalized_results)
    validate_document_graph(
        normalized_results,
        chunk_texts,
        normalized=False,
        check_references=False,
    )
    _prune_unknown_entity_relations(normalized_results)
    _prune_ungrounded_relations(normalized_results, chunk_texts)
    _prune_low_confidence_relations(normalized_results)
    _prune_unreferenced_entities(normalized_results)

    catalog, entity_ids, relation_ids = build_normalization_catalog(
        normalized_results
    )
    if entity_ids or relation_ids:
        response = _request_normalization(document_id, catalog)
        _apply_normalization(
            normalized_results,
            response,
            entity_ids,
            relation_ids,
        )

    validate_document_graph(
        normalized_results,
        chunk_texts,
        normalized=True,
    )
    return normalized_results
