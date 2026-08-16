from flask import Blueprint, render_template, session, redirect, url_for, flash

from extensions import db
from models.resume import Resume
from models.analysis import Analysis


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    user_id = session["user_id"]

    total_resumes = (
        Resume.query
        .filter_by(
            user_id=user_id
        )
        .count()
    )

    analyses = (
        Analysis.query
        .join(Resume)
        .filter(
            Resume.user_id == user_id
        )
        .order_by(
            Analysis.id.desc()
        )
        .all()
    )

    total_analyses = len(analyses)

    if analyses:

        scores = [
            analysis.ats_score
            for analysis in analyses
            if analysis.ats_score is not None
        ]

        if scores:
            average_score = round(
                sum(scores) / len(scores)
            )

            best_score = max(scores)

        else:
            average_score = 0
            best_score = 0

    else:

        average_score = 0
        best_score = 0

    recent_analyses = analyses[:5]

    return render_template(
        "dashboard.html",
        total_resumes=total_resumes,
        total_analyses=total_analyses,
        average_score=average_score,
        best_score=best_score,
        recent_analyses=recent_analyses
    )