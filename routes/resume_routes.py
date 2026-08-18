import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

from werkzeug.utils import secure_filename

from extensions import db
from models.resume import Resume
from models.analysis import Analysis


resume_bp = Blueprint("resume", __name__)


# =========================================================
# FOLDERS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    "static",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}


# Maximum file size = 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


# =========================================================
# CHECK FILE EXTENSION
# =========================================================

def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# MY RESUMES
# =========================================================

@resume_bp.route("/my-resumes")
def my_resumes():

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    resumes = Resume.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Resume.id.desc()
    ).all()

    return render_template(
        "resumes.html",
        resumes=resumes
    )


# =========================================================
# UPLOAD RESUME
# =========================================================

@resume_bp.route(
    "/upload",
    methods=["GET", "POST"]
)
def upload_resume():

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        # ---------------------------------------------
        # CHECK FILE EXISTS
        # ---------------------------------------------

        if "resume" not in request.files:

            flash(
                "Please select a resume.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )

        file = request.files["resume"]


        # ---------------------------------------------
        # CHECK EMPTY FILE
        # ---------------------------------------------

        if file.filename == "":

            flash(
                "Please select a resume.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )


        # ---------------------------------------------
        # CHECK FILE TYPE
        # ---------------------------------------------

        if not allowed_file(file.filename):

            flash(
                "Only PDF and DOCX files are allowed.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )


        # ---------------------------------------------
        # CHECK FILE SIZE
        # ---------------------------------------------

        file.seek(
            0,
            os.SEEK_END
        )

        file_size = file.tell()

        file.seek(0)


        if file_size > MAX_FILE_SIZE:

            flash(
                "File size must be less than 5 MB.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )


        # ---------------------------------------------
        # ORIGINAL FILE NAME
        # ---------------------------------------------

        original_filename = secure_filename(
            file.filename
        )


        # ---------------------------------------------
        # FILE EXTENSION
        # ---------------------------------------------

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()


        # ---------------------------------------------
        # UNIQUE FILE NAME
        # ---------------------------------------------

        unique_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )


        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )


        # ---------------------------------------------
        # SAVE FILE
        # ---------------------------------------------

        file.save(file_path)


        # ---------------------------------------------
        # SAVE DATABASE RECORD
        # ---------------------------------------------

        resume = Resume(
            user_id=session["user_id"],
            resume_name=original_filename,
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


    # ---------------------------------------------
    # GET REQUEST
    # ---------------------------------------------

    return render_template(
        "upload.html"
    )


# =========================================================
# VIEW RESUME
# =========================================================

@resume_bp.route(
    "/view-resume/<int:resume_id>"
)
def view_resume(resume_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )


    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=session["user_id"]
    ).first_or_404()


    # ---------------------------------------------
    # CHECK FILE PATH
    # ---------------------------------------------

    if not resume.file_path:

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )


    # ---------------------------------------------
    # CHECK FILE EXISTS
    # ---------------------------------------------

    if not os.path.exists(
        resume.file_path
    ):

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )


    # ---------------------------------------------
    # GET FILE EXTENSION
    # ---------------------------------------------

    extension = os.path.splitext(
        resume.file_path
    )[1].lower()


    # =================================================
    # PDF
    # =================================================

    if extension == ".pdf":

        return send_file(
            resume.file_path,
            mimetype="application/pdf",
            as_attachment=False
        )


    # =================================================
    # DOCX
    # =================================================

    if extension == ".docx":

        try:

            import mammoth


            # -----------------------------------------
            # OPEN DOCX
            # -----------------------------------------

            with open(
                resume.file_path,
                "rb"
            ) as docx_file:

                result = mammoth.convert_to_html(
                    docx_file
                )


            # -----------------------------------------
            # GET HTML
            # -----------------------------------------

            html_content = result.value


            # -----------------------------------------
            # SHOW DOCX PREVIEW
            # -----------------------------------------

            return render_template(
                "docx_preview.html",
                resume_name=resume.resume_name,
                content=html_content
            )


        except Exception as e:

            print(
                "DOCX preview error:",
                e
            )

            flash(
                "Unable to preview this DOCX file.",
                "error"
            )

            return redirect(
                url_for("resume.my_resumes")
            )


    # =================================================
    # UNSUPPORTED FILE
    # =================================================

    flash(
        "Unsupported resume format.",
        "error"
    )

    return redirect(
        url_for("resume.my_resumes")
    )


# =========================================================
# DOWNLOAD ORIGINAL RESUME
# =========================================================

@resume_bp.route(
    "/download-resume/<int:resume_id>"
)
def download_resume(resume_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )


    resume = Resume.query.filter_by(
        id=resume_id,
        user_id=session["user_id"]
    ).first_or_404()


    if not resume.file_path:

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )


    if not os.path.exists(
        resume.file_path
    ):

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
        download_name=resume.resume_name
    )


# =========================================================
# DELETE RESUME
# =========================================================

@resume_bp.route(
    "/delete-resume/<int:resume_id>",
    methods=["POST"]
)
def delete_resume(resume_id):

    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
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
            url_for("resume.my_resumes")
        )


    # ---------------------------------------------
    # DELETE RELATED ANALYSES FIRST
    # ---------------------------------------------

    Analysis.query.filter_by(
        resume_id=resume.id
    ).delete(
        synchronize_session=False
    )


    # ---------------------------------------------
    # DELETE FILE
    # ---------------------------------------------

    if resume.file_path:

        if os.path.exists(
            resume.file_path
        ):

            try:

                os.remove(
                    resume.file_path
                )

            except Exception as e:

                print(
                    "File deletion error:",
                    e
                )


    # ---------------------------------------------
    # DELETE DATABASE RECORD
    # ---------------------------------------------

    db.session.delete(
        resume
    )

    db.session.commit()


    flash(
        "Resume deleted successfully.",
        "success"
    )


    return redirect(
        url_for("resume.my_resumes")
    )