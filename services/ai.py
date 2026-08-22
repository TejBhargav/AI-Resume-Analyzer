import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured in .env"
    )

client = genai.Client(
    api_key=API_KEY
)


def generate_ai_feedback(resume, job):

    prompt = f"""
You are an expert ATS resume analyzer and professional career advisor.

Analyze the resume against the job description carefully.

RESUME:
{resume}

JOB DESCRIPTION:
{job}

Return ONLY the following sections and use EXACTLY these headings:

SUMMARY

STRENGTHS

MISSING SKILLS

RESUME IMPROVEMENTS

ATS RECOMMENDATIONS

Follow these rules strictly:

SUMMARY:
- Write exactly 2 concise sentences.
- Give an overall assessment of the resume's relevance to the job.
- Do not use generic statements.

STRENGTHS:
- Provide a maximum of 3 points.
- Each point must be short and specific.
- Mention only genuine strengths found in the resume.
- Focus on relevant skills, projects, experience, achievements, and job alignment.

MISSING SKILLS:
- Provide a maximum of 4 points.
- Mention only skills or keywords clearly required by the job description but not found in the resume.
- Do not invent skills.
- Do not recommend a skill as missing if an equivalent skill is already clearly present.

RESUME IMPROVEMENTS:
- Provide exactly 3 points.
- Identify actual weaknesses in the resume.
- Focus on measurable impact, clarity, wording, project descriptions, experience, and relevance.
- Give an actionable improvement rather than a generic statement.

ATS RECOMMENDATIONS:
- Provide exactly 3 points.
- Focus on ATS keywords, section structure, formatting, keyword alignment, and readability.
- Make every recommendation actionable.
- Do not repeat the same advice from RESUME IMPROVEMENTS.

FORMATTING RULES:
- Use simple bullet points beginning with "-".
- Keep each bullet to one short sentence.
- Do not use "***".
- Do not use Markdown headings.
- Do not use numbered lists.
- Do not repeat the same point.
- Do not write long paragraphs.
- Do not invent experience, qualifications, projects, skills, or achievements.
- Base every observation only on the resume and job description.

The final response must contain ONLY these five sections:

SUMMARY
STRENGTHS
MISSING SKILLS
RESUME IMPROVEMENTS
ATS RECOMMENDATIONS
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text