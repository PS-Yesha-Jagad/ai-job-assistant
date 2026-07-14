from pydantic import BaseModel
from typing import List, Optional

class JobListing(BaseModel):
    title: str
    company: Optional[str]
    location: str
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    url: str

class JobSearchResult(BaseModel):
    jobs: List[JobListing]
    total_found: int