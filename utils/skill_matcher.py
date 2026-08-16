import re


SKILLS = [
    "python",
    "java",
    "c++",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "flask",
    "django",
    "fastapi",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "machine learning",
    "deep learning",
    "nlp",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "power bi",
    "tableau",
    "excel",
    "rest api",
]


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def extract_keywords(text):
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

    stop_words = {
        "with",
        "this",
        "that",
        "from",
        "your",
        "have",
        "will",
        "they",
        "their",
        "about",
        "into",
        "using",
        "looking",
        "experience",
        "required",
        "candidate",
        "should",
        "work",
        "team"
    }

    return set(
        word for word in words
        if word not in stop_words
    )


def compare_skills(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    if job_skills:
        skill_score = (
            len(matched_skills) / len(job_skills)
        ) * 100
    else:
        skill_score = 0

    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)

    matched_keywords = resume_keywords.intersection(job_keywords)

    if job_keywords:
        keyword_score = (
            len(matched_keywords) / len(job_keywords)
        ) * 100
    else:
        keyword_score = 0

    content_score = 100 if len(resume_text.strip()) >= 500 else 50

    ats_score = (
        skill_score * 0.60
        + keyword_score * 0.20
        + content_score * 0.20
    )

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 2),
        "keyword_score": round(keyword_score, 2),
        "content_score": round(content_score, 2),
        "match_percentage": round(ats_score, 2)
    }