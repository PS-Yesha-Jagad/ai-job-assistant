import asyncio
from agent.orchestrator import JobMatcherOrchestrator

async def main():
    orch = JobMatcherOrchestrator()
    result = await orch.match_jobs(
        resume_pdf_path="tests/sample_resume.pdf",  # put a real resume PDF here
        job_role="Machine Learning Engineer",
        location="Ahmedabad",
    )
    print(result)
    await orch.stop()

if __name__ == "__main__":
    asyncio.run(main())