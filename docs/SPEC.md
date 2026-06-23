# mcpgauge — MVP spec (Phase 1)

## The one job
Point `mcpgauge` at an MCP server and get a transparent, reproducible **quality
grade** for its tool definitions — the thing that actually determines whether an
agent uses the server correctly. Runs locally, no account, no LLM required.

```
pipx install mcpgauge
mcpgauge "uvx ollama-handoff"        # human-readable graded report
mcpgauge "uvx ollama-handoff" --json # machine output
mcpgauge "uvx ollama-handoff" --min B   # non-zero exit if below grade B (for CI)
```

## Why anyone uses it
- MCP server *authors* want their tools to be picked correctly by agents; today
  there is no fast, CI-runnable, **transparent** way to check description quality.
- The only comparable score (Glama) is opaque and requires claiming the server on
  their site. `mcpgauge` is open-methodology, offline, and runs in seconds.
- A public **"State of MCP Server Quality"** leaderboard (scoring the top servers
  from `awesome-mcp-servers`) is the launch wedge and the demand test.

## Surface area (v1 — keep it this small)
- `mcpgauge <server-command>` — launch a **stdio** MCP server, handshake, list
  tools, score, print a graded report.
- `--json` — emit the full scored result as JSON.
- `--min <grade>` — exit non-zero if the server grade is below the threshold (CI).
- `--quiet` — only print the final grade line.

## Non-goals (v1)
- No security scanning (that's Snyk's lane). No OAuth/remote-HTTP servers.
- No GUI, no hosted service, no database.
- No required LLM call — the core score is 100% deterministic and documented.
  (An optional `--llm` "would an agent pick the right tool?" pass is a v2 idea.)

## Scoring (summary — full rubric in METHODOLOGY.md)
Each tool is scored 0–5 on six deterministic dimensions (Purpose Clarity,
Parameter Semantics, Behavioral Transparency, Schema Validity, Naming,
Conciseness). The server score is `0.6 * mean(tool scores) + 0.4 * min(tool
scores)` so one badly-described tool meaningfully drags the server down. Scores
map to letter grades A–F. The methodology is published and versioned so the score
is reproducible and arguable — that transparency is the product's edge.

## Definition of done / definition of "used"
- **Done:** a stranger can `pipx install mcpgauge` and grade a real server in
  under 10 minutes from the README alone; deterministic, stable scores; green CI.
- **Used (success metrics, measured):**
  - The "State of MCP Server Quality" report gets shared (HN/Reddit/X reach).
  - PyPI installs (download stats) and GitHub stars from MCP authors.
  - Real issues / "score my server" requests from strangers.
  - At least one external repo adds `mcpgauge` to its CI or README badge.

## Riskiest assumption & cheapest test
- **Assumption:** server authors will run a quality gate (the ones with weak
  servers are least motivated).
- **Test:** the leaderboard decouples validation from adoption — we score the top
  ~100 servers and publish; if the report is shared, demand is proven before we
  build the CI/badge layer. Build order reflects this: scorer → leaderboard →
  (only if it lands) CI action + badge service.
