import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_SSL_CA = os.getenv("DB_SSL_CA")

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    if DB_SSL_CA:
        SQLALCHEMY_ENGINE_OPTIONS["connect_args"] = {
            "ssl_ca": os.path.abspath(DB_SSL_CA),
            "ssl_verify_cert": True,
            "ssl_verify_identity": True
        }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"