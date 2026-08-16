from flask import Flask, render_template
from extensions import db
from config import Config

from models.user import User
from models.resume import Resume
from models.job_description import JobDescription
from models.analysis import Analysis

from routes.auth_routes import auth_bp
from routes.resume_routes import resume_bp
from routes.analysis_routes import analysis_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(resume_bp)
app.register_blueprint(analysis_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/test-db")
def test_db():
    try:
        db.session.execute(db.text("SELECT 1"))
        return "MySQL Database Connected Successfully!"
    except Exception as e:
        return f"MySQL Connection Failed: {e}"


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)