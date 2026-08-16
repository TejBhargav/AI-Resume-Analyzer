from datetime import datetime
from extensions import db


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    company = db.Column(
        db.String(150),
        nullable=True
    )

    role = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref("job_descriptions", lazy=True)
    )

    def __repr__(self):
        return f"<JobDescription {self.role}>"