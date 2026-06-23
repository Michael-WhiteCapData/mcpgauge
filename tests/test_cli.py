"""Tests for the CLI, with the network (server inspection) mocked out."""

import json

import pytest

from mcpgauge import cli, inspect

A_GRADE_TOOLS = [
    {
        "name": "cluster_summary",
        "description": "Summarize cluster health and return a JSON object listing unhealthy pods.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]
LOW_TOOLS = [
    {"name": "run", "description": "", "inputSchema": {"type": "object", "properties": {"x": {}}}},
]


@pytest.fixture
def fake_fetch(monkeypatch):
    """Patch cli.fetch_tools with a controllable async stub."""

    def _install(tools):
        async def _fetch(_command, env=None):
            return tools

        monkeypatch.setattr(cli, "fetch_tools", _fetch)

    return _install


def test_cli_prints_grade_and_returns_zero(fake_fetch, capsys):
    fake_fetch(A_GRADE_TOOLS)
    rc = cli.main(["echo placeholder"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Grade" in out


def test_cli_json_output_is_valid(fake_fetch, capsys):
    fake_fetch(A_GRADE_TOOLS)
    rc = cli.main(["echo placeholder", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["grade"] in {"A", "B", "C", "D", "F"}
    assert payload["tool_count"] == 1


def test_cli_min_gate_fails_below_threshold(fake_fetch, capsys):
    fake_fetch(LOW_TOOLS)
    rc = cli.main(["echo placeholder", "--min", "A", "--quiet"])
    assert rc == 1  # a low-grade server must fail the A gate


def test_cli_min_gate_passes_when_met(fake_fetch, capsys):
    fake_fetch(A_GRADE_TOOLS)
    rc = cli.main(["echo placeholder", "--min", "F"])
    assert rc == 0


def test_cli_reports_inspection_failure(monkeypatch, capsys):
    async def _boom(_command, env=None):
        raise RuntimeError("could not start server")

    monkeypatch.setattr(cli, "fetch_tools", _boom)
    rc = cli.main(["bogus-server"])
    err = capsys.readouterr().err
    assert rc == 2
    assert "failed to inspect server" in err


def test_inspect_rejects_empty_command():
    import asyncio

    with pytest.raises(ValueError):
        asyncio.run(inspect.fetch_tools(""))
