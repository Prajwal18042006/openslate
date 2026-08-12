"""
Database configuration for OpenSlate.

Uses:
- SQLite for local development
- PostgreSQL for production
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# =========================================================
# Load environment variables
# =========================================================

load_dotenv()

# =========================================================
# Database URL
# =========================================================

DATABASE_URL = os.getenv("DATABASE_URL")

# Local development fallback
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./backend/openslate.db"

print("🗄️ Database configuration")

if DATABASE_URL.startswith("postgresql"):
    print("🐘 Database type: PostgreSQL")
elif DATABASE_URL.startswith("sqlite"):
    print("📦 Database type: SQLite")
else:
    print("⚠️ Unknown database type")


# =========================================================
# Connection arguments
# =========================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


# =========================================================
# Engine
# =========================================================

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)


# =========================================================
# Session
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# =========================================================
# Base class
# =========================================================

Base = declarative_base()


# =========================================================
# Database dependency
# =========================================================

def get_db():
    """
    Provides a database session to FastAPI endpoints.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()