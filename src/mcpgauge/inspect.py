"""Launch a stdio MCP server and read its tool definitions.

Thin wrapper over the MCP client SDK. Returns plain dicts so the scorer never
depends on SDK types.
"""

from __future__ import annotations

import os
import shlex
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def fetch_tools(
    command: str | list[str],
    env: dict[str, str] | None = None,
    *,
    show_server_stderr: bool = False,
) -> list[dict[str, Any]]:
    """Start the stdio server, complete the MCP handshake, and list its tools.

    Args:
        command: The command that launches the server, e.g. ``"uvx ollama-handoff"``
            (a string is split with shell-like quoting) or an argv list.
        env: Optional extra environment variables for the server process.
        show_server_stderr: If False (default), the server's stderr is discarded so
            its logging does not pollute mcpgauge's report. Set True to debug a
            server that won't start.

    Returns:
        A list of ``{"name", "description", "inputSchema"}`` dicts.
    """
    parts = shlex.split(command) if isinstance(command, str) else list(command)
    if not parts:
        raise ValueError("empty server command")

    params = StdioServerParameters(command=parts[0], args=parts[1:], env=env)
    errlog = None if show_server_stderr else open(os.devnull, "w")  # noqa: SIM115
    kwargs = {} if errlog is None else {"errlog": errlog}
    try:
        async with stdio_client(params, **kwargs) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "inputSchema": tool.inputSchema or {},
                    }
                    for tool in result.tools
                ]
    finally:
        if errlog is not None:
            errlog.close()
