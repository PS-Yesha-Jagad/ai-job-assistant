from mcp_servers.job_search.models import JobListing

def map_adzuna_response(raw: dict) -> list[JobListing]:
    listings = []
    for item in raw.get("results", []):
        listings.append(JobListing(
            title=item.get("title", "Unknown"),
            company=item.get("company", {}).get("display_name"),
            location=item.get("location", {}).get("display_name", "Unknown"),
            description=item.get("description", ""),
            salary_min=item.get("salary_min"),
            salary_max=item.get("salary_max"),
            url=item.get("redirect_url", ""),
        ))
    return listings