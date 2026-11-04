# exts.py
# exts.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()

engine = None
SessionLocal = None

def create_db_session_factory(app):
    global engine, SessionLocal
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

