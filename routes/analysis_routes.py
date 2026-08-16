from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from extensions import db

from models.job_description import JobDescription
from models.resume import Resume
from models.analysis import Analysis

from utils.skill_matcher import compare_skills
from utils.feedback_parser import parse_ai_feedback
from services.ai import generate_ai_feedback


analysis_bp = Blueprint(
    "analysis",
    __name__
)


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

    if request.method == "POST":

        company = request.form["company"]
        role = request.form["role"]
        description = request.form["description"]

        job = JobDescription(
            user_id=session["user_id"],
            company=company,
            role=role,
            description=description
        )

        db.session.add(job)
        db.session.commit()

        flash(
            "Job description saved successfully.",
            "success"
        )

        return redirect(
            url_for("analysis.analysis")
        )

    return render_template(
        "job_description.html"
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

    resume = (
        Resume.query
        .filter_by(
            user_id=session["user_id"]
        )
        .order_by(
            Resume.id.desc()
        )
        .first()
    )

    job = (
        JobDescription.query
        .filter_by(
            user_id=session["user_id"]
        )
        .order_by(
            JobDescription.id.desc()
        )
        .first()
    )

    if not resume:

        flash(
            "Please upload a resume first.",
            "error"
        )

        return redirect(
            url_for("resume.upload_resume")
        )

    if not job:

        flash(
            "Please add a job description first.",
            "error"
        )

        return redirect(
            url_for("analysis.job_description")
        )

    if not resume.resume_text:

        flash(
            "Resume text is empty.",
            "error"
        )

        return redirect(
            url_for("resume.upload_resume")
        )

    result = compare_skills(
        resume.resume_text,
        job.description
    )

    ai_feedback = generate_ai_feedback(
        resume.resume_text,
        job.description
    )

    feedback_sections = parse_ai_feedback(
        ai_feedback
    )

    skill_score = result.get(
        "skill_score",
        result.get(
            "match_percentage",
            0
        )
    )

    keyword_score = result.get(
        "keyword_score",
        0
    )

    content_score = result.get(
        "content_score",
        0
    )

    match_percentage = result.get(
        "match_percentage",
        0
    )

    analysis_record = Analysis(
        resume_id=resume.id,
        job_description_id=job.id,
        ats_score=round(
            match_percentage
        ),
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
        resume=resume,
        job=job,
        result=result,
        ai_feedback=ai_feedback,
        feedback_sections=feedback_sections,
        skill_score=skill_score,
        keyword_score=keyword_score,
        content_score=content_score
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
        .join(Resume)
        .join(JobDescription)
        .filter(
            Resume.user_id
            == session["user_id"]
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
def analysis_details(
    analysis_id
):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    analysis_record = (
        Analysis.query.get_or_404(
            analysis_id
        )
    )

    if (
        analysis_record.resume.user_id
        != session["user_id"]
    ):

        return "Unauthorized access", 403

    return render_template(
        "analysis_details.html",
        analysis=analysis_record
    )