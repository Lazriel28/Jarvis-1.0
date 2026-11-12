from __future__ import annotations

import asyncio
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.safe_access import load_mcp_servers


class MCPManager:
    """Connects only to explicitly configured servers, on user request."""

    async def _with_server(self, name: str, operation):
        servers = load_mcp_servers()
        if name not in servers:
            raise ValueError(f"MCP server '{name}' is not configured.")
        spec = servers[name]
        params = StdioServerParameters(
            command=spec["command"],
            args=spec.get("args", []),
            env=spec.get("env"),
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await operation(session)

    async def list_tools(self, name: str) -> list[dict[str, Any]]:
        async def operation(session):
            result = await session.list_tools()
            return [
                {"name": tool.name, "description": tool.description or "", "input_schema": tool.inputSchema}
                for tool in result.tools
            ]
        return await self._with_server(name, operation)

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> str:
        async def operation(session):
            result = await session.call_tool(tool_name, arguments)
            parts = []
            for item in result.content:
                text = getattr(item, "text", None)
                parts.append(text if isinstance(text, str) else str(item))
            return "\n".join(parts) or "MCP tool returned no text."
        return await self._with_server(server_name, operation)


def list_tools_sync(name: str) -> list[dict[str, Any]]:
    return asyncio.run(MCPManager().list_tools(name))


def call_tool_sync(server_name: str, tool_name: str, arguments: dict) -> str:
    return asyncio.run(MCPManager().call_tool(server_name, tool_name, arguments))
