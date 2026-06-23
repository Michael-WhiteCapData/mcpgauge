"""Command-line entry point for mcpgauge."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .inspect import fetch_tools
from .report import render
from .score import grade_rank, score_server


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcpgauge",
        description="Grade an MCP server's tool-definition quality (deterministic, offline).",
    )
    parser.add_argument(
        "server",
        help="Command that launches a stdio MCP server, e.g. 'uvx ollama-handoff'.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full result as JSON.")
    parser.add_argument(
        "--min",
        metavar="GRADE",
        help="Exit non-zero if the server grade is below this letter (A-F). For CI.",
    )
    parser.add_argument("--quiet", action="store_true", help="Print only the final grade line.")
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Seconds to wait for the server to start and list tools (default: 30).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        tools = asyncio.run(asyncio.wait_for(fetch_tools(args.server), args.timeout))
    except asyncio.TimeoutError:
        print(f"mcpgauge: server did not respond within {args.timeout:g}s", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - surface any launch/handshake failure to the user
        print(f"mcpgauge: failed to inspect server: {exc}", file=sys.stderr)
        return 2

    result = score_server(tools)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(render(result, quiet=args.quiet))

    if args.min and grade_rank(result.grade) < grade_rank(args.min):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
