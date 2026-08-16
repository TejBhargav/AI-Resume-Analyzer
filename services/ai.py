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
You are an expert ATS resume analyzer and career advisor.

Analyze the following resume against the job description.

RESUME:

{resume}

JOB DESCRIPTION:

{job}

Return the analysis using exactly these four headings:

STRENGTHS

MISSING SKILLS

RESUME IMPROVEMENTS

ATS RECOMMENDATIONS

Under each heading, provide 3 to 5 concise bullet points.

Focus on:

- Technical skills
- Soft skills
- Experience
- Projects
- Keywords
- ATS compatibility
- Resume clarity
- Job relevance

Do not invent experience or skills that are not present in the resume.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text