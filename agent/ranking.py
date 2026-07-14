def compute_match_percentage(resume_skills: list[str], job_description: str) -> tuple[float, list[str], list[str]]:
    """
    Fallback deterministic ranking, used if the LLM's JSON is malformed
    or as a sanity check alongside the LLM's own reasoning.
    """
    desc_lower = job_description.lower()
    matching = [s for s in resume_skills if s.lower() in desc_lower]
    missing = [s for s in resume_skills if s.lower() not in desc_lower]

    if not resume_skills:
        return 0.0, [], []

    percentage = round((len(matching) / len(resume_skills)) * 100, 1)
    return percentage, matching, missing