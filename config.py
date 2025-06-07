import os

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://postgres:2233@localhost/mini_db"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:2233@localhost/mini_db"
# SQLALCHEMY_TRACK_MODIFICATIONS = False
