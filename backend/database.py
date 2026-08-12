"""
Database configuration for OpenSlate.

Uses SQLAlchemy with SQLite for local development.

Later, DATABASE_URL can be changed to PostgreSQL
for production deployment.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------------
# Database URL
# ---------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./backend/openslate.db"
)


# ---------------------------------------------------------
# SQLite configuration
# ---------------------------------------------------------

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# ---------------------------------------------------------
# Engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


# ---------------------------------------------------------
# Session
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ---------------------------------------------------------
# Base class
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# Database dependency
# ---------------------------------------------------------

def get_db():
    """
    Provides a database session to FastAPI endpoints.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()