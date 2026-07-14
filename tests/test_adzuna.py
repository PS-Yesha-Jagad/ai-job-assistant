from mcp_servers.job_search.adzuna_client import search_jobs
from mcp_servers.job_search.mapper import map_adzuna_response

raw = search_jobs("Machine Learning Engineer", "Ahmedabad")
jobs = map_adzuna_response(raw)
print(f"Found {raw.get('count')} total jobs, showing {len(jobs)}")
for j in jobs[:3]:
    print(f"- {j.title} at {j.company} ({j.location})")