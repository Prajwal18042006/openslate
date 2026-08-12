"""
OpenSlate Mini - FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base, DATABASE_URL
from backend.routers import projects, documents, pipeline, chat, chunks


# ---------------------------------------------------------
# Create tables on startup
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


def _migrate_sqlite_columns():
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
                pass
        conn.commit()


_migrate_sqlite_columns()


# ---------------------------------------------------------
# App
# ---------------------------------------------------------

app = FastAPI(
    title="OpenSlate Mini API",
    description="RAG Pipeline - Extract, Chunk, Embed, Retrieve, Answer",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# ---------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------

app.include_router(projects.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chunks.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "OpenSlate Mini API is running",
        "docs": "/api/docs",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}