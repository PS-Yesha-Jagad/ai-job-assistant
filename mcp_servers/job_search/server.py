from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import json

from mcp_servers.job_search.adzuna_client import search_jobs
from mcp_servers.job_search.mapper import map_adzuna_response

server = Server("job-search")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_jobs",
            description="Searches live job listings by role and location using the Adzuna API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_role": {"type": "string"},
                    "location": {"type": "string"},
                },
                "required": ["job_role", "location"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "search_jobs":
        raise ValueError(f"Unknown tool: {name}")

    raw = search_jobs(arguments["job_role"], arguments["location"])
    jobs = map_adzuna_response(raw)
    result = {
        "total_found": raw.get("count", 0),
        "jobs": [j.model_dump() for j in jobs],
    }
    return [TextContent(type="text", text=json.dumps(result))]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())