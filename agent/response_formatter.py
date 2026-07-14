from agent.ranking import compute_match_percentage


def format_final_response(agent_result: dict, resume_skills: list[str]) -> dict:
    if "error" in agent_result:
        return {"success": False, "error": agent_result["error"], "matches": []}

    matches = agent_result.get("matches", [])
    cleaned = []
    for m in matches:
        entry = {
            "title": m.get("title", "Unknown role"),
            "company": m.get("company", "Unknown"),
            "location": m.get("location", ""),
            "url": m.get("url", ""),
            "match_percentage": m.get("match_percentage"),
            "matching_skills": m.get("matching_skills", []),
            "missing_skills": m.get("missing_skills", []),
            "explanation": m.get("explanation", ""),
        }
        if entry["match_percentage"] is None:
            pct, matching, missing = compute_match_percentage(resume_skills, entry["explanation"])
            entry["match_percentage"] = pct
            entry["matching_skills"] = entry["matching_skills"] or matching
            entry["missing_skills"] = entry["missing_skills"] or missing
        cleaned.append(entry)

    cleaned.sort(key=lambda x: x["match_percentage"] or 0, reverse=True)
    return {"success": True, "matches": cleaned}