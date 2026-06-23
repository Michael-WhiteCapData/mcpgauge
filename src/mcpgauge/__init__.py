"""mcpgauge — a deterministic, offline quality grader for MCP servers."""

from __future__ import annotations

from .score import (
    METHODOLOGY_VERSION,
    ServerScore,
    ToolScore,
    grade_for,
    score_server,
    score_tool,
)

__version__ = "0.1.0"

__all__ = [
    "METHODOLOGY_VERSION",
    "ServerScore",
    "ToolScore",
    "__version__",
    "grade_for",
    "score_server",
    "score_tool",
]
