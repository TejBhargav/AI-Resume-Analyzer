from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from extensions import db
from models.resume import Resume
from models.analysis import Analysis
import os
from werkzeug.utils import secure_filename

resume_bp = Blueprint("resume", __name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@resume_bp.route("/my-resumes")
def my_resumes():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    resumes = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Resume.id.desc()
    ).all()

    return render_template(
        "resumes.html",
        resumes=resumes
    )


@resume_bp.route("/upload", methods=["GET", "POST"])
def upload_resume():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        if "resume" not in request.files:
            flash("Please select a resume.", "error")
            return redirect(url_for("resume.upload_resume"))

        file = request.files["resume"]

        if file.filename == "":
            flash("Please select a resume.", "error")
            return redirect(url_for("resume.upload_resume"))

        filename = secure_filename(file.filename)

        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(file_path)

        resume = Resume(
            user_id=session["user_id"],
            resume_name=filename,
            file_path=file_path
        )

        db.session.add(resume)
        db.session.commit()

        flash(
            "Resume uploaded successfully.",
            "success"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    return render_template(
        "upload.html"
    )


@resume_bp.route("/delete-resume/<int:resume_id>", methods=["POST"])
def delete_resume(resume_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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
            url_for("resume.my_resumes")
        )

    Analysis.query.filter_by(
        resume_id=resume.id
    ).delete(
        synchronize_session=False
    )

    if resume.file_path and os.path.exists(
        resume.file_path
    ):

        try:
            os.remove(resume.file_path)
        except:
            pass

    db.session.delete(resume)

    db.session.commit()

    flash(
        "Resume deleted successfully.",
        "success"
    )

    return redirect(
        url_for("resume.my_resumes")
    )


@resume_bp.route("/view-resume/<int:resume_id>")
def view_resume(resume_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=session["user_id"]
    ).first_or_404()

    if not os.path.exists(resume.file_path):

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    return send_file(
        resume.file_path,
        as_attachment=False
    )


@resume_bp.route("/download-resume/<int:resume_id>")
def download_resume(resume_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=session["user_id"]
    ).first_or_404()

    if not os.path.exists(resume.file_path):

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    return send_file(
        resume.file_path,
        as_attachment=True,
        download_name=os.path.basename(
            resume.file_path
        )
    )