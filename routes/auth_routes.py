from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from extensions import db
from models.user import User
from models.resume import Resume
from models.analysis import Analysis

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email

            flash("Login successful.", "success")

            return redirect(url_for("auth.dashboard"))

        flash("Invalid email or password.", "error")

        return redirect(url_for("auth.login"))

    return render_template("login.html")

@auth_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    user = User.query.get(user_id)

    total_resumes = (
        Resume.query
        .filter(
            Resume.user_id == user_id
        )
        .count()
    )

    total_analyses = (
        Analysis.query
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == user_id
        )
        .count()
    )

    average_score = (
        db.session.query(
            func.avg(Analysis.ats_score)
        )
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == user_id
        )
        .scalar()
    )

    best_score = (
        db.session.query(
            func.max(Analysis.ats_score)
        )
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == user_id
        )
        .scalar()
    )

    recent_analyses = (
        Analysis.query
        .join(
            Resume,
            Analysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == user_id
        )
        .order_by(
            Analysis.id.desc()
        )
        .limit(5)
        .all()
    )

    average_score = (
        round(float(average_score), 1)
        if average_score is not None
        else 0
    )

    best_score = (
        round(float(best_score), 1)
        if best_score is not None
        else 0
    )

    return render_template(
        "dashboard.html",
        user=user,
        total_resumes=total_resumes,
        total_analyses=total_analyses,
        average_score=average_score,
        best_score=best_score,
        recent_analyses=recent_analyses
    )

@auth_bp.route("/logout")
def logout():
    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("home"))