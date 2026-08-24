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
    "rest api"
]

RESUME_SECTIONS = [
    "summary",
    "objective",
    "profile",
    "experience",
    "work experience",
    "employment",
    "education",
    "skills",
    "projects",
    "certifications",
    "achievements",
    "internship",
    "internships"
]

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def extract_keywords(text):
    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower()
    )

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
        "team",
        "role",
        "responsibilities",
        "skills",
        "ability",
        "including",
        "preferred",
        "knowledge",
        "strong",
        "good",
        "years",
        "develop",
        "development",
        "working",
        "position",
        "company"
    }

    return {
        word
        for word in words
        if word not in stop_words
    }


def calculate_content_score(resume_text):
    text = resume_text.lower().strip()

    if not text:
        return 0

    words = text.split()
    word_count = len(words)

    if word_count >= 500:
        length_score = 100
    elif word_count >= 400:
        length_score = 90
    elif word_count >= 300:
        length_score = 80
    elif word_count >= 200:
        length_score = 70
    elif word_count >= 100:
        length_score = 55
    else:
        length_score = 40

    sections_found = 0

    for section in RESUME_SECTIONS:
        if section in text:
            sections_found += 1

    section_score = min(
        (sections_found / 6) * 100,
        100
    )

    content_score = (
        length_score * 0.60
        +
        section_score * 0.40
    )

    return round(
        min(content_score, 100),
        2
    )


def compare_skills(resume_text, job_description):

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    missing_skills = [
        skill
        for skill in job_skills
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

    matched_keywords = (
        resume_keywords.intersection(job_keywords)
    )

    if job_keywords:
        keyword_score = (
            len(matched_keywords) / len(job_keywords)
        ) * 100
    else:
        keyword_score = 0

    content_score = calculate_content_score(
        resume_text
    )

    ats_score = (
        skill_score * 0.60
        +
        keyword_score * 0.20
        +
        content_score * 0.20
    )

    skill_score = round(
        min(skill_score, 100),
        1
    )

    keyword_score = round(
        min(keyword_score, 100),
        1
    )

    content_score = round(
        min(content_score, 100),
        1
    )

    ats_score = round(
        min(ats_score, 100),
        1
    )

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "content_score": content_score,
        "match_percentage": ats_score
    }