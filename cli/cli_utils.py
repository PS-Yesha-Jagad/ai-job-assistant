def print_banner():
    print("=" * 50)
    print("   AI Job Matcher — MCP Powered Agent")
    print("=" * 50)

def print_matches(matches: list[dict]):
    if not matches:
        print("No matching jobs found. Try a different role or location.")
        return
    for i, m in enumerate(matches, start=1):
        print(f"\n[{i}] {m['title']} — {m['company']} ({m['location']})")
        print(f"    Match: {m['match_percentage']}%")
        print(f"    Matching skills: {', '.join(m['matching_skills']) or 'None'}")
        print(f"    Missing skills:  {', '.join(m['missing_skills']) or 'None'}")
        print(f"    Why: {m['explanation']}")
        print(f"    Apply: {m['url']}")