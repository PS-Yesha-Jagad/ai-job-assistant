from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import json

from mcp_servers.resume_analysis.parser import extract_resume_text
from mcp_servers.resume_analysis.extractor import (
    extract_skills, extract_experience_years, extract_education
)

server = Server("resume-analysis")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="analyze_resume",
            description="Parses a resume PDF and extracts skills, experience years, and education.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Absolute path to the resume PDF"}
                },
                "required": ["pdf_path"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "analyze_resume":
        raise ValueError(f"Unknown tool: {name}")

    pdf_path = arguments["pdf_path"]
    text = extract_resume_text(pdf_path)
    result = {
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text),
    }
    return [TextContent(type="text", text=json.dumps(result))]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())