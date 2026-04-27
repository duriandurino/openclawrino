#!/usr/bin/env python3
"""Helpers for normalizing report-facing CVSS v4.0 finding payloads."""

from __future__ import annotations

from typing import Any

CVSS_V4_VERSION = "4.0"
CVSS_V4_LABEL = "CVSS-B"
CVSS_V4_VERSION_LABEL = "CVSS v4.0 Base"


SEVERITY_BANDS = [
    (9.0, "Critical"),
    (7.0, "High"),
    (4.0, "Medium"),
    (0.1, "Low"),
    (0.0, "None"),
]


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_score(value: Any) -> float | None:
    if value in (None, "", "N/A"):
        return None
    try:
        score = round(float(value), 1)
    except (TypeError, ValueError):
        return None
    if score < 0 or score > 10:
        return None
    return score


def severity_from_score(score: Any) -> str | None:
    normalized = _normalize_score(score)
    if normalized is None:
        return None
    for threshold, label in SEVERITY_BANDS:
        if normalized >= threshold:
            return label
    return None


def make_cvss_v4(*, score: Any = None, vector: Any = None, severity: Any = None,
                 rationale: Any = None, assumptions: Any = None,
                 version: Any = CVSS_V4_VERSION, label: Any = CVSS_V4_LABEL) -> dict:
    payload = {
        "version": _clean_text(version) or CVSS_V4_VERSION,
        "label": _clean_text(label) or CVSS_V4_LABEL,
        "score": _normalize_score(score),
        "vector": _clean_text(vector),
        "severity": _clean_text(severity),
        "rationale": _clean_text(rationale),
        "assumptions": _clean_text(assumptions),
    }
    if payload["severity"] is None and payload["score"] is not None:
        payload["severity"] = severity_from_score(payload["score"])
    return payload


def coerce_legacy_cvss_v4(finding: dict | None) -> dict | None:
    if not isinstance(finding, dict):
        return finding

    normalized = dict(finding)
    existing = normalized.get("cvss_v4")
    if isinstance(existing, dict):
        merged = make_cvss_v4(
            score=existing.get("score", existing.get("baseScore", normalized.get("cvss"))),
            vector=existing.get("vector", existing.get("vectorString", normalized.get("cvss_vector"))),
            severity=existing.get("severity", normalized.get("cvss_severity", normalized.get("severity"))),
            rationale=existing.get("rationale", existing.get("justification", normalized.get("cvss_rationale"))),
            assumptions=existing.get("assumptions", existing.get("note", existing.get("scoring_note", existing.get("scoringNote", normalized.get("cvss_note"))))),
            version=existing.get("version", normalized.get("cvss_version") or CVSS_V4_VERSION),
            label=existing.get("label", normalized.get("cvss_label") or CVSS_V4_LABEL),
        )
    else:
        merged = make_cvss_v4(
            score=normalized.get("cvss"),
            vector=normalized.get("cvss_vector"),
            severity=normalized.get("cvss_severity", normalized.get("severity")),
            rationale=normalized.get("cvss_rationale"),
            assumptions=normalized.get("cvss_assumptions", normalized.get("cvss_note")),
            version=normalized.get("cvss_version") or CVSS_V4_VERSION,
            label=normalized.get("cvss_label") or CVSS_V4_LABEL,
        )

    normalized["cvss_v4"] = merged
    if merged["score"] is not None and normalized.get("cvss") in (None, "", "N/A"):
        normalized["cvss"] = merged["score"]
    normalized.setdefault("cvss_version", CVSS_V4_VERSION_LABEL if merged["score"] is not None or merged["vector"] else merged["version"])
    if merged["vector"] and not _clean_text(normalized.get("cvss_vector")):
        normalized["cvss_vector"] = merged["vector"]
    if merged["severity"] and not _clean_text(normalized.get("cvss_severity")):
        normalized["cvss_severity"] = merged["severity"]
    if merged["label"] and not _clean_text(normalized.get("cvss_label")):
        normalized["cvss_label"] = merged["label"]
    if merged["rationale"] and not _clean_text(normalized.get("cvss_rationale")):
        normalized["cvss_rationale"] = merged["rationale"]
    if merged["assumptions"] and not _clean_text(normalized.get("cvss_assumptions")):
        normalized["cvss_assumptions"] = merged["assumptions"]
    if merged["assumptions"] and not _clean_text(normalized.get("cvss_note")):
        normalized["cvss_note"] = merged["assumptions"]
    return normalized
