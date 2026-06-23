"""Tests for the terminal report renderer."""

from mcpgauge.report import lowest_tools, render
from mcpgauge.score import score_server

TOOLS = [
    {
        "name": "good_tool",
        "description": "Do a useful thing and return a JSON object describing the result.",
        "inputSchema": {
            "type": "object",
            "properties": {"x": {"type": "string", "description": "the input value"}},
        },
    },
    {"name": "run", "description": "", "inputSchema": {"type": "object", "properties": {}}},
]


def test_render_includes_headline_and_each_tool():
    result = score_server(TOOLS)
    text = render(result)
    assert text.startswith(f"Grade {result.grade}")
    assert "good_tool" in text
    assert "run" in text
    assert "methodology v" in text


def test_quiet_render_is_single_line():
    result = score_server(TOOLS)
    text = render(result, quiet=True)
    assert "\n" not in text
    assert text.startswith("Grade")


def test_render_surfaces_notes():
    result = score_server(TOOLS)
    text = render(result)
    # The empty-description tool should surface its warning.
    assert "missing description" in text


def test_lowest_tools_orders_by_score():
    result = score_server(TOOLS)
    lowest = lowest_tools(result, n=1)
    assert len(lowest) == 1
    assert lowest[0].name == "run"  # the worst tool
