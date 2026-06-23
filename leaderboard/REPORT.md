# State of MCP Server Quality

_Generated 2026-06-22 · scored with [mcpgauge](https://github.com/Michael-WhiteCapData/mcpgauge) methodology v0_

These grades measure **tool-definition quality** — how clearly each server describes its tools, parameters, and behavior, which is what determines whether an agent uses it correctly. They are **not** a security or runtime assessment. The scoring is deterministic and open; reproduce or argue with it via the published [methodology](https://github.com/Michael-WhiteCapData/mcpgauge/blob/main/docs/METHODOLOGY.md).

Servers evaluated: **9** (plus 0 that could not be launched headlessly).

| Rank | Server | Grade | Score | Tools |
|-----:|--------|:-----:|:-----:|------:|
| 1 | `tablebridge` | **A** | 4.78 | 6 |
| 2 | `ollama-handoff` | **A** | 4.74 | 8 |
| 3 | `whitecapdata-dev` | **A** | 4.73 | 10 |
| 4 | `mcp-server-fetch` | **A** | 4.25 | 1 |
| 5 | `@modelcontextprotocol/server-sequential-thinking` | **A** | 4.20 | 1 |
| 6 | `@modelcontextprotocol/server-everything` | **A** | 4.00 | 13 |
| 7 | `@modelcontextprotocol/server-memory` | **B** | 3.91 | 9 |
| 8 | `@modelcontextprotocol/server-filesystem` | **B** | 3.74 | 14 |
| 9 | `mcp-server-time` | **B** | 3.66 | 2 |

---

Want your server graded? `pipx install mcpgauge` then `mcpgauge "<launch command>"`. PRs to add servers to the list are welcome.
