from pydantic import BaseModel
from typing import List

class ResumeData(BaseModel):
    raw_text: str
    skills: List[str]
    experience_years: float
    education: List[str]