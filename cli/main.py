import asyncio
import os
from agent.orchestrator import JobMatcherOrchestrator
from agent.response_formatter import format_final_response
from mcp_servers.resume_analysis.parser import extract_resume_text
from mcp_servers.resume_analysis.extractor import extract_skills
from cli.cli_utils import print_banner, print_matches


async def run_cli():
    print_banner()

    pdf_path = input("Path to your resume PDF: ").strip().strip('"')
    if not os.path.isfile(pdf_path):
        print("File not found. Exiting.")
        return

    job_role = input("Job role you're looking for: ").strip()
    location = input("Preferred location: ").strip()

    print("\nAnalyzing resume and searching jobs... (this can take 20-60s with Mistral 7B)")

    orch = JobMatcherOrchestrator()
    try:
        result = await orch.match_jobs(pdf_path, job_role, location)
        resume_text = extract_resume_text(pdf_path)
        resume_skills = extract_skills(resume_text)
        formatted = format_final_response(result, resume_skills)

        if not formatted["success"]:
            print(f"\nError: {formatted['error']}")
        else:
            print_matches(formatted["matches"])
    finally:
        await orch.stop()


if __name__ == "__main__":
    asyncio.run(run_cli())