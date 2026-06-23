# State of MCP Server Quality

_Generated 2026-06-22 · scored with [mcpgauge](https://github.com/Michael-WhiteCapData/mcpgauge) methodology v0_

These grades measure **tool-definition quality** — how clearly each server describes its tools, parameters, and behavior, which is what determines whether an agent uses it correctly. They are **not** a security or runtime assessment. The scoring is deterministic and open; reproduce or argue with it via the published [methodology](https://github.com/Michael-WhiteCapData/mcpgauge/blob/main/docs/METHODOLOGY.md).

Servers evaluated: **21** — a mix of the official reference servers and popular community servers that launch headlessly.

| Rank | Server | Grade | Score | Tools |
|-----:|--------|:-----:|:-----:|------:|
| 1 | `tablebridge` | **A** | 4.78 | 6 |
| 2 | `ollama-handoff` | **A** | 4.74 | 8 |
| 3 | `whitecapdata-dev` | **A** | 4.73 | 10 |
| 4 | `arxiv-mcp-server` | **A** | 4.51 | 10 |
| 5 | `yfmcp` | **A** | 4.50 | 11 |
| 6 | `@antv/mcp-server-chart` | **A** | 4.33 | 27 |
| 7 | `mcp-server-fetch` | **A** | 4.25 | 1 |
| 8 | `@modelcontextprotocol/server-sequential-thinking` | **A** | 4.20 | 1 |
| 9 | `mcp-server-sqlite` | **A** | 4.18 | 6 |
| 10 | `@modelcontextprotocol/server-everything` | **A** | 4.00 | 13 |
| 11 | `@modelcontextprotocol/server-memory` | **B** | 3.91 | 9 |
| 12 | `@upstash/context7-mcp` | **B** | 3.88 | 2 |
| 13 | `wikipedia-mcp` | **B** | 3.82 | 22 |
| 14 | `@modelcontextprotocol/server-filesystem` | **B** | 3.74 | 14 |
| 15 | `@playwright/mcp` | **B** | 3.73 | 23 |
| 16 | `@browsermcp/mcp` | **B** | 3.73 | 12 |
| 17 | `mcp-server-time` | **B** | 3.66 | 2 |
| 18 | `mcp-server-kubernetes` | **B** | 3.63 | 23 |
| 19 | `duckduckgo-mcp-server` | **C** | 3.20 | 2 |
| 20 | `mcp-server-git` | **C** | 2.64 | 12 |
| 21 | `mcp-server-calculator` | **C** | 2.60 | 1 |

---

Want your server graded? `pipx install mcpgauge` then `mcpgauge "<launch command>"`. PRs to add servers to the list are welcome.
