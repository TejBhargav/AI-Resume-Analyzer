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


# =========================================================
# JOB DESCRIPTION
# =========================================================

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


        if not description:

            flash(
                "Please enter a job description.",
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


# =========================================================
# RESUME TEXT EXTRACTION
# =========================================================

def extract_resume_text(resume):

    """
    Extract text from PDF or DOCX if resume_text
    was not already saved in the database.
    """

    # -----------------------------------------------------
    # Already available
    # -----------------------------------------------------

    if resume.resume_text:

        return resume.resume_text


    # -----------------------------------------------------
    # Check file path
    # -----------------------------------------------------

    if not resume.file_path:

        return ""


    if not os.path.exists(
        resume.file_path
    ):

        return ""


    extension = os.path.splitext(
        resume.file_path
    )[1].lower()


    # =====================================================
    # PDF
    # =====================================================

    if extension == ".pdf":

        try:

            from pypdf import PdfReader


            reader = PdfReader(
                resume.file_path
            )


            pages = []


            for page in reader.pages:

                text = page.extract_text()


                if text:

                    pages.append(
                        text
                    )


            return "\n".join(
                pages
            ).strip()


        except Exception as e:

            print(
                "PDF extraction error:",
                e
            )

            return ""


    # =====================================================
    # DOCX
    # =====================================================

    if extension == ".docx":

        try:

            from docx import Document


            document = Document(
                resume.file_path
            )


            paragraphs = []


            for paragraph in document.paragraphs:

                text = paragraph.text.strip()


                if text:

                    paragraphs.append(
                        text
                    )


            return "\n".join(
                paragraphs
            ).strip()


        except Exception as e:

            print(
                "DOCX extraction error:",
                e
            )

            return ""


    return ""


# =========================================================
# ANALYSIS
# =========================================================

@analysis_bp.route(
    "/analysis"
)
def analysis():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    # =====================================================
    # GET LATEST RESUME
    # =====================================================

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


    # =====================================================
    # GET LATEST JOB DESCRIPTION
    # =====================================================

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


    # =====================================================
    # CHECK RESUME
    # =====================================================

    if not resume:

        flash(
            "Please upload a resume first.",
            "error"
        )

        return redirect(
            url_for("resume.upload_resume")
        )


    # =====================================================
    # CHECK JOB DESCRIPTION
    # =====================================================

    if not job:

        flash(
            "Please add a job description first.",
            "error"
        )

        return redirect(
            url_for("analysis.job_description")
        )


    # =====================================================
    # EXTRACT RESUME TEXT
    # =====================================================

    resume_text = extract_resume_text(
        resume
    )


    # =====================================================
    # CHECK EXTRACTED TEXT
    # =====================================================

    if not resume_text:

        flash(
            "Unable to extract text from the uploaded resume. "
            "Please upload a readable PDF or DOCX file.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )


    # =====================================================
    # SAVE EXTRACTED TEXT
    # =====================================================

    if not resume.resume_text:

        resume.resume_text = resume_text

        db.session.commit()


    # =====================================================
    # SKILL MATCHING
    # =====================================================

    try:

        result = compare_skills(
            resume_text,
            job.description
        )

    except Exception as e:

        print(
            "Skill matching error:",
            e
        )

        flash(
            "Unable to compare resume skills.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )


    # =====================================================
    # AI FEEDBACK
    # =====================================================

    try:

        ai_feedback = generate_ai_feedback(
            resume_text,
            job.description
        )

    except Exception as e:

        print(
            "AI feedback error:",
            e
        )

        ai_feedback = (
            "AI feedback could not be generated."
        )


    # =====================================================
    # PARSE AI FEEDBACK
    # =====================================================

    try:

        feedback_sections = parse_ai_feedback(
            ai_feedback
        )

    except Exception as e:

        print(
            "Feedback parser error:",
            e
        )

        feedback_sections = {}


    # =====================================================
    # SCORES
    # =====================================================

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
        skill_score
    )


    # =====================================================
    # MAKE SURE SCORE IS A NUMBER
    # =====================================================

    try:

        match_percentage = float(
            match_percentage
        )

    except (
        TypeError,
        ValueError
    ):

        match_percentage = 0


    # Keep score between 0 and 100

    match_percentage = max(
        0,
        min(
            100,
            match_percentage
        )
    )


    # =====================================================
    # MATCHED SKILLS
    # =====================================================

    matched_skills = result.get(
        "matched_skills",
        []
    )


    if not isinstance(
        matched_skills,
        list
    ):

        matched_skills = [
            str(matched_skills)
        ]


    # =====================================================
    # MISSING SKILLS
    # =====================================================

    missing_skills = result.get(
        "missing_skills",
        []
    )


    if not isinstance(
        missing_skills,
        list
    ):

        missing_skills = [
            str(missing_skills)
        ]


    # =====================================================
    # SAVE ANALYSIS
    # =====================================================

    try:

        analysis_record = Analysis(

            resume_id=resume.id,

            job_description_id=job.id,

            ats_score=round(
                match_percentage
            ),

            matched_skills=", ".join(
                matched_skills
            ),

            missing_skills=", ".join(
                missing_skills
            ),

            suggestions=ai_feedback

        )


        db.session.add(
            analysis_record
        )

        db.session.commit()


    except Exception as e:

        db.session.rollback()

        print(
            "Analysis database error:",
            e
        )

        flash(
            "Analysis was generated but could not be saved.",
            "error"
        )


    # =====================================================
    # SHOW ANALYSIS
    # =====================================================

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


# =========================================================
# HISTORY
# =========================================================

@analysis_bp.route(
    "/history"
)
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


# =========================================================
# ANALYSIS DETAILS
# =========================================================

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

        Analysis.query

        .get_or_404(
            analysis_id
        )

    )


    if (
        analysis_record.resume.user_id
        != session["user_id"]
    ):

        return (
            "Unauthorized access",
            403
        )


    return render_template(

        "analysis_details.html",

        analysis=analysis_record

    )