import requests
from config.settings import settings

ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"

def search_jobs(job_role: str, location: str, country: str = "in", results_per_page: int = 10) -> dict:
    url = f"{ADZUNA_BASE_URL}/{country}/search/1"
    params = {
        "app_id": settings.ADZUNA_APP_ID,
        "app_key": settings.ADZUNA_APP_KEY,
        "what": job_role,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return response.json()