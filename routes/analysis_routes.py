import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from dotenv import load_dotenv
from google import genai

from extensions import db

from models.resume import Resume
from models.job_description import JobDescription
from models.analysis import Analysis

from utils.skill_matcher import compare_skills
from utils.feedback_parser import parse_ai_feedback


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

analysis_bp = Blueprint(
    "analysis",
    __name__
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


@analysis_bp.route(
    "/job-description",
    methods=["GET", "POST"]
)
def job_description():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    resumes = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Resume.id.desc()
    ).all()

    if request.method == "POST":

        resume_id = request.form.get(
            "resume_id"
        )

        company = request.form.get(
            "company",
            ""
        ).strip()

        role = request.form.get(
            "role",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not resume_id:

            flash(
                "Please select a resume.",
                "error"
            )

            return redirect(
                url_for("analysis.job_description")
            )

        if not description:

            flash(
                "Please enter the job description.",
                "error"
            )

            return redirect(
                url_for("analysis.job_description")
            )

        resume = Resume.query.filter_by(
            id=resume_id,
            user_id=session["user_id"]
        ).first()

        if not resume:

            flash(
                "Resume not found.",
                "error"
            )

            return redirect(
                url_for("analysis.job_description")
            )

        job = JobDescription(
            user_id=session["user_id"],
            company=company,
            role=role,
            description=description
        )

        db.session.add(job)
        db.session.commit()

        return redirect(
            url_for(
                "analysis.analysis",
                resume_id=resume.id,
                job_id=job.id
            )
        )

    return render_template(
        "job_description.html",
        resumes=resumes
    )


@analysis_bp.route("/analysis")
def analysis():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    resume_id = request.args.get(
        "resume_id",
        type=int
    )

    job_id = request.args.get(
        "job_id",
        type=int
    )

    if not resume_id or not job_id:

        flash(
            "Resume or job description not found.",
            "error"
        )

        return redirect(
            url_for("analysis.job_description")
        )

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=session["user_id"]
    ).first_or_404()

    job = JobDescription.query.filter_by(
        id=job_id,
        user_id=session["user_id"]
    ).first_or_404()

    resume_text = getattr(
        resume,
        "extracted_text",
        ""
    )

    if not resume_text:
        resume_text = ""

    result = compare_skills(
        resume_text,
        job.description
    )

    skill_score = result.get(
        "skill_score",
        0
    )

    keyword_score = result.get(
        "keyword_score",
        0
    )

    content_score = result.get(
        "content_score",
        0
    )

    ats_score = result.get(
        "match_percentage",
        0
    )

    ai_feedback = generate_ai_feedback(
        resume_text,
        job.description
    )

    parsed_feedback = parse_ai_feedback(
        ai_feedback
    )

    analysis_record = Analysis(
        resume_id=resume.id,
        job_description_id=job.id,
        ats_score=ats_score,
        matched_skills=", ".join(
            result.get(
                "matched_skills",
                []
            )
        ),
        missing_skills=", ".join(
            result.get(
                "missing_skills",
                []
            )
        ),
        suggestions=ai_feedback
    )

    db.session.add(
        analysis_record
    )

    db.session.commit()

    return render_template(
        "analysis.html",
        analysis=analysis_record,
        resume=resume,
        job=job,
        result=result,
        skill_score=skill_score,
        keyword_score=keyword_score,
        content_score=content_score,
        ats_score=ats_score,
        parsed_feedback=parsed_feedback
    )


@analysis_bp.route("/history")
def history():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    analyses = (
        Analysis.query
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == session["user_id"]
        )
        .order_by(
            Analysis.id.desc()
        )
        .all()
    )

    return render_template(
        "history.html",
        analyses=analyses
    )


@analysis_bp.route(
    "/analysis/<int:analysis_id>"
)
def analysis_details(analysis_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    analysis_record = (
        Analysis.query
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Analysis.id == analysis_id,
            Resume.user_id == session["user_id"]
        )
        .first_or_404()
    )

    return render_template(
        "analysis_details.html",
        analysis=analysis_record
    )