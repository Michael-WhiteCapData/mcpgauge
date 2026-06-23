#!/usr/bin/env python3
"""Generate the "State of MCP Server Quality" leaderboard.

Reads ``leaderboard/servers.json`` (a list of ``{name, command, env?}`` entries),
scores each server with mcpgauge, and writes ``leaderboard/REPORT.md``.

Usage:
    python scripts/leaderboard.py [--timeout 60]
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import os
import pathlib
import sys

from mcpgauge.inspect import fetch_tools
from mcpgauge.score import METHODOLOGY_VERSION, score_server

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVERS = ROOT / "leaderboard" / "servers.json"
REPORT = ROOT / "leaderboard" / "REPORT.md"


async def evaluate(entry: dict, timeout: float) -> dict:
    name = entry["name"]
    try:
        env = {**os.environ, **entry["env"]} if entry.get("env") else None
        tools = await asyncio.wait_for(fetch_tools(entry["command"], env=env), timeout)
        result = score_server(tools)
        return {"name": name, "ok": True, "result": result}
    except Exception as exc:  # noqa: BLE001 - record the failure, keep going
        return {
            "name": name,
            "ok": False,
            "error": str(exc).splitlines()[0][:160] or type(exc).__name__,
        }


def render(rows: list[dict], date_str: str) -> str:
    ok = sorted((r for r in rows if r["ok"]), key=lambda r: r["result"].score, reverse=True)
    failed = [r for r in rows if not r["ok"]]

    lines = [
        "# State of MCP Server Quality",
        "",
        f"_Generated {date_str} · scored with "
        f"[mcpgauge](https://github.com/Michael-WhiteCapData/mcpgauge) methodology "
        f"v{METHODOLOGY_VERSION}_",
        "",
        "These grades measure **tool-definition quality** — how clearly each server "
        "describes its tools, parameters, and behavior, which is what determines "
        "whether an agent uses it correctly. They are **not** a security or runtime "
        "assessment. The scoring is deterministic and open; reproduce or argue with it "
        "via the published "
        "[methodology](https://github.com/Michael-WhiteCapData/mcpgauge/blob/main/docs/METHODOLOGY.md).",
        "",
        f"Servers evaluated: **{len(ok)}** (plus {len(failed)} that could not be launched headlessly).",
        "",
        "| Rank | Server | Grade | Score | Tools |",
        "|-----:|--------|:-----:|:-----:|------:|",
    ]
    for rank, row in enumerate(ok, 1):
        res = row["result"]
        lines.append(
            f"| {rank} | `{row['name']}` | **{res.grade}** | {res.score:.2f} | {res.tool_count} |"
        )

    if failed:
        lines += [
            "",
            "### Not evaluated",
            "",
            "Could not be launched without credentials/arguments in this run:",
            "",
        ]
        lines += [f"- `{row['name']}` — {row['error']}" for row in failed]

    lines += [
        "",
        "---",
        "",
        "Want your server graded? `pipx install mcpgauge` then "
        '`mcpgauge "<launch command>"`. PRs to add servers to the list are welcome.',
        "",
    ]
    return "\n".join(lines)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    servers = json.loads(SERVERS.read_text())
    rows: list[dict] = []
    for entry in servers:
        print(f"scoring {entry['name']} ...", file=sys.stderr, flush=True)
        rows.append(await evaluate(entry, args.timeout))

    REPORT.write_text(render(rows, datetime.date.today().isoformat()))
    graded = sum(1 for r in rows if r["ok"])
    print(f"wrote {REPORT} — {graded}/{len(rows)} servers graded", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
