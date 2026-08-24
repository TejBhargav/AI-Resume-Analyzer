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

Your task is to compare the candidate's resume with the job description and provide a precise, evidence-based analysis.

Do not praise the resume unnecessarily.
Do not invent information.
Do not assume the candidate has a skill unless it is clearly present.
Every recommendation must be useful for improving the candidate's chances for THIS specific job.

RESUME:
{resume}

JOB DESCRIPTION:
{job}

Return ONLY these five sections using EXACTLY these headings:

SUMMARY

STRENGTHS

MISSING SKILLS

RESUME IMPROVEMENTS

ATS RECOMMENDATIONS

SUMMARY:
- Write exactly 2 short sentences.
- Give a direct assessment of how well the resume matches the job.
- Mention the most important alignment or gap.
- Do not use generic statements.

STRENGTHS:
- Provide a maximum of 3 points.
- Each point must be one short sentence.
- Mention only strengths clearly supported by the resume.
- Prioritize skills, projects, experience, achievements, and technologies relevant to the job.
- Do not repeat the same strength.

MISSING SKILLS:
- Provide a maximum of 4 points.
- Include only skills, technologies, tools, qualifications, or keywords clearly required or strongly indicated by the job description and absent from the resume.
- Do not list a skill as missing when an equivalent skill is already present.
- If there are no meaningful missing skills, write:
  - No major skill gaps identified for this role.

RESUME IMPROVEMENTS:
- Provide exactly 3 points.
- Each point must identify a specific weakness and give a practical improvement.
- Focus on:
  measurable achievements,
  project impact,
  experience descriptions,
  clarity,
  relevance,
  wording,
  and job-specific tailoring.
- Do not repeat ATS recommendations.

ATS RECOMMENDATIONS:
- Provide exactly 3 points.
- Each point must be actionable.
- Focus on:
  job-specific keywords,
  keyword placement,
  section structure,
  ATS readability,
  formatting,
  and relevant terminology.
- Do not recommend unnecessary formatting changes.
- Do not repeat RESUME IMPROVEMENTS.

QUALITY RULES:
- Use simple "-" bullet points only.
- Each bullet must be one short sentence.
- Keep bullets concise and easy to scan.
- Do not use numbered lists.
- Do not use Markdown headings.
- Do not use "**", "***", tables, or long paragraphs.
- Do not repeat information between sections.
- Do not invent skills, experience, qualifications, projects, metrics, or achievements.
- Do not recommend adding a skill unless the job description supports it.
- Use terminology from the job description when appropriate.
- Prioritize high-value observations over generic advice.
- Base every conclusion only on the supplied resume and job description.

The final response must contain ONLY:

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