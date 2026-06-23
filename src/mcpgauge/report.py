"""Render a ServerScore as a human-readable terminal report."""

from __future__ import annotations

from .score import ServerScore, ToolScore

_DIM_LABELS = {
    "purpose_clarity": "purpose",
    "parameter_semantics": "params",
    "behavioral_transparency": "behavior",
    "schema_validity": "schema",
    "naming": "naming",
    "conciseness": "concise",
}


def _bar(score: float) -> str:
    filled = round(score)
    return "█" * filled + "·" * (5 - filled)


def render(result: ServerScore, quiet: bool = False) -> str:
    headline = f"Grade {result.grade}  ({result.score:.2f}/5)  —  {result.tool_count} tools"
    if quiet:
        return headline

    lines = [
        headline,
        f"mean {result.mean_tool_score:.2f} · min {result.min_tool_score:.2f} · "
        f"methodology v{result.methodology_version}",
        "",
    ]
    for tool in sorted(result.tools, key=lambda t: t.score):
        lines.append(f"  [{tool.grade}] {tool.name}  {tool.score:.2f}/5")
        dims = "  ".join(f"{_DIM_LABELS[k]} {_bar(v)}" for k, v in tool.dimensions.items())
        lines.append(f"      {dims}")
        for note in tool.notes:
            lines.append(f"      ⚠ {note}")
    if result.notes:
        lines.append("")
        for note in result.notes:
            lines.append(f"  ⚠ {note}")
    return "\n".join(lines)


def lowest_tools(result: ServerScore, n: int = 3) -> list[ToolScore]:
    return sorted(result.tools, key=lambda t: t.score)[:n]
