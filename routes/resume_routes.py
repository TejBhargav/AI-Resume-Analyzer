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

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

MAX_FILE_SIZE = 5 * 1024 * 1024


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


def get_absolute_file_path(file_path):

    if not file_path:
        return None

    if os.path.isabs(file_path):
        return file_path

    file_path = file_path.replace(
        "\\",
        os.sep
    ).replace(
        "/",
        os.sep
    )

    return os.path.abspath(
        os.path.join(
            BASE_DIR,
            file_path
        )
    )


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

        if "resume" not in request.files:

            flash(
                "Please select a resume.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )

        file = request.files["resume"]

        if not file.filename:

            flash(
                "Please select a resume.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )

        if not allowed_file(file.filename):

            flash(
                "Only PDF and DOCX files are allowed.",
                "error"
            )

            return redirect(
                url_for("resume.upload_resume")
            )

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

        original_filename = secure_filename(
            file.filename
        )

        extension = original_filename.rsplit(
            ".",
            1
        )[1].lower()

        unique_filename = (
            str(uuid.uuid4())
            + "."
            + extension
        )

        absolute_file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        relative_file_path = os.path.join(
            "static",
            "uploads",
            unique_filename
        )

        file.save(
            absolute_file_path
        )

        resume = Resume(
            user_id=session["user_id"],
            resume_name=original_filename,
            file_path=relative_file_path
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

    file_path = get_absolute_file_path(
        resume.file_path
    )

    if not file_path:

        flash(
            "Resume file path is missing.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    if not os.path.isfile(file_path):

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return send_file(
            file_path,
            mimetype="application/pdf",
            as_attachment=False
        )

    if extension == ".docx":

        try:

            import mammoth

            with open(
                file_path,
                "rb"
            ) as docx_file:

                result = mammoth.convert_to_html(
                    docx_file
                )

            return render_template(
                "docx_preview.html",
                resume_name=resume.resume_name,
                content=result.value
            )

        except ImportError:

            flash(
                "Please install mammoth to preview DOCX files.",
                "error"
            )

            return redirect(
                url_for("resume.my_resumes")
            )

        except Exception:

            flash(
                "Unable to preview this DOCX file.",
                "error"
            )

            return redirect(
                url_for("resume.my_resumes")
            )

    flash(
        "Unsupported resume format.",
        "error"
    )

    return redirect(
        url_for("resume.my_resumes")
    )


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

    file_path = get_absolute_file_path(
        resume.file_path
    )

    if not file_path or not os.path.isfile(file_path):

        flash(
            "Resume file not found.",
            "error"
        )

        return redirect(
            url_for("resume.my_resumes")
        )

    return send_file(
        file_path,
        as_attachment=True,
        download_name=resume.resume_name
    )


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

    Analysis.query.filter_by(
        resume_id=resume.id
    ).delete(
        synchronize_session=False
    )

    file_path = get_absolute_file_path(
        resume.file_path
    )

    if file_path and os.path.isfile(file_path):

        try:
            os.remove(file_path)
        except OSError:
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