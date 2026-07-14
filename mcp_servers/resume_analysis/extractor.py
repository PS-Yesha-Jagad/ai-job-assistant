import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Starter skill list — expand this over time based on your target roles
KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "sql", "nosql",
    "fastapi", "flask", "django", "react", "node.js", "express",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "docker", "kubernetes", "aws", "gcp", "azure", "git", "github",
    "mongodb", "postgresql", "mysql", "redis", "qdrant", "langchain",
    "langgraph", "rag", "llm", "rest api", "graphql", "html", "css",
]

def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = [skill for skill in KNOWN_SKILLS if skill in text_lower]
    return sorted(set(found))

def extract_experience_years(text: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text.lower())
    if matches:
        return max(float(m) for m in matches)
    return 0.0

def extract_education(text: str) -> list[str]:
    doc = nlp(text)
    edu_keywords = ["b.tech", "bachelor", "master", "m.tech", "phd", "b.sc", "m.sc", "mba"]
    lines = text.split("\n")
    education = [line.strip() for line in lines if any(k in line.lower() for k in edu_keywords)]
    return education[:5]  # cap noise