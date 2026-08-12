"""
OpenSlate Mini - FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, DATABASE_URL
from backend.routers import projects, documents, chat, chunks


# =========================================================
# Database Migration
# =========================================================

def _migrate_sqlite_columns():
    """
    Add missing SQLite columns if they do not already exist.
    """

    if not DATABASE_URL.startswith("sqlite"):
        return

    migrations = [
        ("chunks", "char_count", "INTEGER"),
        ("chunks", "chunk_index", "INTEGER"),
        ("chunks", "summary", "TEXT"),
    ]

    with engine.connect() as conn:

        for table, column, col_type in migrations:

            try:
                conn.exec_driver_sql(
                    f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
                )

            except Exception:
                # Column probably already exists
                pass

        conn.commit()


# =========================================================
# Application Lifespan
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    print("🚀 Starting OpenSlate Mini API...")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")

    # SQLite migrations
    try:
        _migrate_sqlite_columns()
        print("✅ Database migrations checked")
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")

    print("✅ OpenSlate Mini startup completed")

    yield

    print("🛑 OpenSlate Mini shutting down...")


# =========================================================
# FastAPI Application
# =========================================================

app = FastAPI(
    title="OpenSlate Mini API",
    description="RAG Pipeline - Extract, Chunk, Embed, Retrieve, Answer",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)


# =========================================================
# CORS Configuration
# =========================================================

# Production frontend URL
FRONTEND_URL = os.getenv("FRONTEND_URL")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# Add deployed frontend URL if available
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

print("🌐 CORS allowed origins:")
for origin in allowed_origins:
    print(f"   - {origin}")


app.add_middleware(
    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# Register Basic Routers
# =========================================================

app.include_router(
    projects.router,
    prefix="/api",
)

app.include_router(
    documents.router,
    prefix="/api",
)

app.include_router(
    chunks.router,
    prefix="/api",
)

app.include_router(
    chat.router,
    prefix="/api",
)


# =========================================================
# Pipeline Router
# =========================================================

# Import pipeline after FastAPI application setup.
#
# This prevents the heavy PDF / Unstructured dependencies
# from being imported before the application itself is created.

try:

    from backend.routers import pipeline

    app.include_router(
        pipeline.router,
        prefix="/api",
    )

    print("✅ Pipeline router loaded")

except Exception as e:

    print(
        f"⚠️ Pipeline router could not be loaded: {e}"
    )


# =========================================================
# Root Endpoint
# =========================================================

@app.get("/")
def root():
    return {
        "message": "OpenSlate Mini API is running",
        "docs": "/api/docs",
        "health": "/api/health",
        "version": "1.0.0",
    }


# =========================================================
# Health Check
# =========================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "OpenSlate Mini API",
    }