import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config.logging import logger


class MCPClientManager:
    """
    Manages connections to multiple MCP servers and exposes
    a unified interface to discover + call tools across all of them.
    """

    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.available_tools: list[dict] = []

    async def connect_server(self, name: str, command: str, args: list[str], cwd: str | None = None):
        server_params = StdioServerParameters(command=command, args=args, cwd=cwd)
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()
        self.sessions[name] = session

        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            self.available_tools.append({
                "server": name,
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            })
        logger.info(f"Connected to '{name}' MCP server, {len(tools_response.tools)} tools discovered")


    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"No active session for server '{server_name}'")
        result = await session.call_tool(tool_name, arguments)
        return result

    def get_tools_for_llm(self) -> list[dict]:
        """Format discovered tools for the LLM's tool-calling schema."""
        return [
            {
                "name": t["name"],
                "description": t["description"],
                "input_schema": t["input_schema"],
            }
            for t in self.available_tools
        ]

    async def close(self):
        await self.exit_stack.aclose()