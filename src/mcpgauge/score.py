"""Deterministic MCP tool-definition quality scoring.

This module implements exactly the rubric documented in docs/METHODOLOGY.md. No
LLM, no network. Given the tools a server exposes, it produces per-tool and
server-level scores that are stable and reproducible.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

METHODOLOGY_VERSION = "0"

# Dimension weights (must sum to 1.0).
WEIGHTS: dict[str, float] = {
    "purpose_clarity": 0.25,
    "parameter_semantics": 0.20,
    "behavioral_transparency": 0.20,
    "schema_validity": 0.15,
    "naming": 0.10,
    "conciseness": 0.10,
}

_GENERIC_NAMES = {
    "run",
    "do",
    "execute",
    "tool",
    "call",
    "handler",
    "main",
    "go",
    "invoke",
    "action",
    "func",
    "function",
}
_RETURN_SIGNALS = (
    "return",
    "returns",
    "output",
    "outputs",
    "writes",
    "write",
    "deletes",
    "delete",
    "creates",
    "create",
    "list of",
    "json",
    "yields",
    "produces",
    "reports",
    "report",
    "responds",
    "result",
)
_STOPWORDS = {"a", "an", "the", "this", "tool", "of", "to", "for", "and", "or"}
_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")

_GRADES = (("A", 4.0), ("B", 3.3), ("C", 2.6), ("D", 1.8), ("F", 0.0))


def grade_for(score: float) -> str:
    for letter, cutoff in _GRADES:
        if score >= cutoff:
            return letter
    return "F"


def grade_rank(grade: str) -> int:
    """Higher is better; used to compare grades for the --min CI gate."""
    order = {"F": 0, "D": 1, "C": 2, "B": 3, "A": 4}
    return order.get(grade.upper(), -1)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@dataclass
class ToolScore:
    name: str
    score: float
    grade: str
    dimensions: dict[str, float]
    notes: list[str] = field(default_factory=list)


@dataclass
class ServerScore:
    score: float
    grade: str
    methodology_version: str
    tool_count: int
    mean_tool_score: float
    min_tool_score: float
    tools: list[ToolScore]
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# -- per-dimension scorers (each returns 0..5) -------------------------------


def _purpose_clarity(name: str, desc: str) -> float:
    if not desc:
        return 0.0
    n = len(desc.split())
    if n < 4:
        base = 1.5
    elif n < 8:
        base = 3.0
    elif n <= 45:
        base = 5.0
    elif n <= 90:
        base = 4.0
    else:
        base = 3.0
    # Does the first sentence add information beyond the tool name's words?
    name_words = set(name.lower().split("_"))
    first_sentence = re.split(r"[.!?]", desc)[0]
    novel = (set(_words(first_sentence)) - _STOPWORDS) - name_words
    if not novel:
        base = min(base, 1.5)
    return base


def _parameter_semantics(schema: dict[str, Any]) -> float:
    props = (schema or {}).get("properties") or {}
    if not props:
        return 5.0  # nothing to document
    documented = sum(
        1
        for p in props.values()
        if isinstance(p, dict) and len((p.get("description") or "").strip()) >= 3
    )
    return round(5.0 * documented / len(props), 2)


def _behavioral_transparency(desc: str) -> float:
    if not desc:
        return 0.0
    low = desc.lower()
    if any(sig in low for sig in _RETURN_SIGNALS):
        return 5.0
    return 2.5 if len(desc.split()) >= 8 else 1.5


def _schema_validity(schema: dict[str, Any]) -> float:
    if not isinstance(schema, dict):
        return 2.0
    score = 5.0
    if schema.get("type") != "object":
        score -= 1.5
    props = schema.get("properties") or {}
    for prop in props.values():
        if not isinstance(prop, dict):
            score -= 1.0
        elif not ({"type", "anyOf", "oneOf", "allOf", "$ref", "enum"} & set(prop)):
            score -= 1.0
    required = schema.get("required") or []
    if any(r not in props for r in required):
        score -= 1.0
    return max(0.0, min(5.0, score))


def _naming(name: str) -> float:
    if not _NAME_RE.match(name):
        return 2.5
    if name in _GENERIC_NAMES:
        return 2.0
    if len(name) < 3:
        return 3.0
    return 5.0


def _conciseness(desc: str) -> float:
    n = len(desc.split())
    if n == 0:
        return 0.0
    if n == 1:
        return 1.0
    if n < 6:
        return 3.0
    if n <= 60:
        return 5.0
    if n <= 120:
        return 3.5
    return 2.0


def score_tool(name: str, description: str | None, input_schema: dict | None) -> ToolScore:
    desc = (description or "").strip()
    schema = input_schema or {}
    dims = {
        "purpose_clarity": _purpose_clarity(name, desc),
        "parameter_semantics": _parameter_semantics(schema),
        "behavioral_transparency": _behavioral_transparency(desc),
        "schema_validity": _schema_validity(schema),
        "naming": _naming(name),
        "conciseness": _conciseness(desc),
    }
    total = round(sum(dims[k] * WEIGHTS[k] for k in WEIGHTS), 3)
    notes: list[str] = []
    if not desc:
        notes.append("missing description")
    props = schema.get("properties") or {}
    undocumented = [
        k
        for k, p in props.items()
        if not (isinstance(p, dict) and (p.get("description") or "").strip())
    ]
    if undocumented:
        notes.append("undocumented parameters: " + ", ".join(sorted(undocumented)))
    if name in _GENERIC_NAMES:
        notes.append(f"generic tool name: {name!r}")
    return ToolScore(name=name, score=total, grade=grade_for(total), dimensions=dims, notes=notes)


def score_server(tools: list[dict[str, Any]]) -> ServerScore:
    tool_scores = [
        score_tool(t.get("name", ""), t.get("description"), t.get("inputSchema")) for t in tools
    ]
    notes: list[str] = []
    if not tool_scores:
        return ServerScore(
            score=0.0,
            grade="F",
            methodology_version=METHODOLOGY_VERSION,
            tool_count=0,
            mean_tool_score=0.0,
            min_tool_score=0.0,
            tools=[],
            notes=["server exposes no tools"],
        )

    values = [t.score for t in tool_scores]
    mean = sum(values) / len(values)
    minimum = min(values)
    server = 0.6 * mean + 0.4 * minimum

    # Coherence: duplicate tool names hurt agent disambiguation.
    names = [t.name for t in tool_scores]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        server -= 0.3 * len(dupes)
        notes.append("duplicate tool names: " + ", ".join(sorted(dupes)))

    server = round(max(0.0, min(5.0, server)), 3)
    return ServerScore(
        score=server,
        grade=grade_for(server),
        methodology_version=METHODOLOGY_VERSION,
        tool_count=len(tool_scores),
        mean_tool_score=round(mean, 3),
        min_tool_score=round(minimum, 3),
        tools=tool_scores,
        notes=notes,
    )
