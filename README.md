# mcpgauge

**Grade an MCP server's tool definitions in seconds — deterministic, offline, no account.**

[![CI](https://github.com/Michael-WhiteCapData/mcpgauge/actions/workflows/ci.yml/badge.svg)](https://github.com/Michael-WhiteCapData/mcpgauge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mcpgauge?color=3775A9&logo=pypi&logoColor=white)](https://pypi.org/project/mcpgauge/)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An agent only uses an [MCP](https://modelcontextprotocol.io/) server well if its
**tool definitions** are clear — good names, real descriptions, documented
parameters. `mcpgauge` launches a server, reads its tools, and scores their
definition quality against a [published, deterministic rubric](docs/METHODOLOGY.md).
No LLM, no network beyond the server you point it at, no sign-up.

## Quickstart

```bash
pipx install mcpgauge          # or: uvx mcpgauge ...
mcpgauge "uvx ollama-handoff"
```

```
Grade A  (4.18/5)  —  8 tools
mean 4.31 · min 3.72 · methodology v0

  [B] summarize_local  3.72/5
      purpose █████  params █████  behavior █████  schema █████  naming █████  concise ████·
  [A] query  4.80/5
      ...
```

- `--json` — machine-readable output for tooling.
- `--min B` — exit non-zero if the server grades below `B` (drop it in CI).
- `--quiet` — print only the final grade line.

## Why it exists

Most MCP servers are thin wrappers with vague tool descriptions, and agents pick
the wrong tool as a result. The only comparable quality score is closed and
requires registering your server on a third-party site. `mcpgauge` is the
opposite: **open methodology, offline, reproducible, and CI-runnable.** You can
read exactly how every point is awarded in [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
and argue with it.

## How scoring works (short version)

Each tool is scored 0–5 on six dimensions — Purpose Clarity, Parameter Semantics,
Behavioral Transparency, Schema Validity, Naming, Conciseness. The server score is
`0.6 · mean + 0.4 · min` across tools, so one badly-described tool drags the whole
server down (which is exactly how agents fail). Full rubric:
[docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Status

Early and honest: v0 of the rubric, stdio servers, deterministic checks only. An
optional LLM "would an agent pick the right tool?" pass and remote-HTTP support are
on the roadmap. Issues and rubric critiques welcome.

## Development

```bash
uv pip install -e ".[dev]"
pytest
ruff check src tests
```

## License

MIT — see [LICENSE](LICENSE).
