import sys
import os
from agent.mcp_client import MCPClientManager
from agent.react_agent import ReActAgent
from config.logging import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class JobMatcherOrchestrator:
    def __init__(self):
        self.mcp_manager = MCPClientManager()
        self.agent: ReActAgent | None = None
        self._connected = False

    async def start(self):
        if self._connected:
            return
        python_exe = sys.executable

        await self.mcp_manager.connect_server(
            name="resume-analysis",
            command=python_exe,
            args=["-m", "mcp_servers.resume_analysis.server"],
            cwd=PROJECT_ROOT,
        )
        await self.mcp_manager.connect_server(
            name="job-search",
            command=python_exe,
            args=["-m", "mcp_servers.job_search.server"],
            cwd=PROJECT_ROOT,
        )

        self.agent = ReActAgent(self.mcp_manager)
        self._connected = True
        logger.info("Orchestrator started — both MCP servers connected.")

    async def match_jobs(self, resume_pdf_path: str, job_role: str, location: str) -> dict:
        if not self._connected:
            await self.start()

        user_request = (
            f"Analyze the resume at '{resume_pdf_path}', then search for "
            f"'{job_role}' jobs in '{location}'. Compare the resume skills against "
            f"each job, rank the jobs by match percentage, list matching and missing "
            f"skills, and explain each recommendation. Return Final Answer as JSON "
            f"with a 'matches' array, each item having: title, company, location, url, "
            f"match_percentage, matching_skills, missing_skills, explanation."
        )
        result = await self.agent.run(user_request)
        return result

    async def stop(self):
        if self._connected:
            await self.mcp_manager.close()
            self._connected = False