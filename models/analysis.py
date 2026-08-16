from datetime import datetime
from extensions import db


class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resumes.id"),
        nullable=False
    )

    job_description_id = db.Column(
        db.Integer,
        db.ForeignKey("job_descriptions.id"),
        nullable=False
    )

    ats_score = db.Column(
        db.Integer,
        nullable=False
    )

    matched_skills = db.Column(
        db.Text,
        nullable=True
    )

    missing_skills = db.Column(
        db.Text,
        nullable=True
    )

    suggestions = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resume = db.relationship(
        "Resume",
        backref="analyses"
    )

    job_description = db.relationship(
        "JobDescription",
        backref="analyses"
    )