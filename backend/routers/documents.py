"""
Documents router - upload, list, get, and delete documents per project.
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Form,
)

from sqlalchemy.orm import Session

from supabase import create_client, Client

from backend.database import get_db
from backend.models import Document, Project, Chunk


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# =========================================================
# Supabase Configuration
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)

SUPABASE_BUCKET = os.getenv(
    "SUPABASE_BUCKET",
    "documents",
)


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing from .env"
    )


if not SUPABASE_SECRET_KEY:
    raise ValueError(
        "SUPABASE_SECRET_KEY is missing from .env"
    )


# =========================================================
# Create Supabase client
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


print("☁️ Supabase Storage configured")
print(f"📦 Bucket: {SUPABASE_BUCKET}")
print(f"🌐 URL: {SUPABASE_URL}")


# =========================================================
# Allowed file types
# =========================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".html",
    ".htm",
    ".csv",
    ".md",
    ".rtf",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
}

ALLOWED_MIME_TYPES = {
    # PDF
    "application/pdf",

    # Word
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

    # Text / Web
    "text/plain",
    "text/html",
    "text/markdown",
    "application/rtf",

    # CSV
    "text/csv",

    # Excel
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

    # PowerPoint
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


# =========================================================
# Upload Document
# =========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    project_id: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document to Supabase Storage
    and store document information in the database.
    """

    print("\n" + "=" * 60)
    print("📤 DOCUMENT UPLOAD STARTED")
    print("=" * 60)

    # =====================================================
    # Step 1: Validate project
    # =====================================================

    print("🔎 Checking project...")

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    print(f"✅ Project found: {project_id}")

    # =====================================================
    # Step 2: Validate filename
    # =====================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    print(f"📄 Filename: {file.filename}")

    # =====================================================
    # Step 3: Validate extension
    # =====================================================

    extension = Path(file.filename).suffix.lower()

    print(f"📌 Extension: {extension}")

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{extension}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    # =====================================================
    # Step 4: Validate MIME type
    # =====================================================

    print(f"📌 MIME type: {file.content_type}")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported MIME type '{file.content_type}'. "
                f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
            ),
        )

    # =====================================================
    # Step 5: Create document ID
    # =====================================================

    document_id = str(uuid.uuid4())

    # =====================================================
    # Step 6: Create Supabase Storage path
    # =====================================================

    storage_path = f"{project_id}/{document_id}{extension}"

    print(f"🆔 Document ID: {document_id}")
    print(f"☁️ Storage path: {storage_path}")

    # =====================================================
    # Step 7: Read uploaded file
    # =====================================================

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read uploaded file: {str(e)}",
        )

    # =====================================================
    # Step 8: Validate file size
    # =====================================================

    file_size = len(file_bytes)

    print(f"📦 File size: {file_size} bytes")

    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    # 50 MB limit
    MAX_FILE_SIZE = 50 * 1024 * 1024

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File is too large. Maximum allowed size is 50 MB.",
        )

    # =====================================================
    # Step 9: Upload to Supabase Storage
    # =====================================================

    print("☁️ Uploading file to Supabase...")
    print(f"📦 Bucket: {SUPABASE_BUCKET}")
    print(f"📁 Path: {storage_path}")

    try:
        upload_response = (
            supabase
            .storage
            .from_(SUPABASE_BUCKET)
            .upload(
                path=storage_path,
                file=file_bytes,
                file_options={
                    # Use the file's actual content-type instead of
                    # hardcoding application/pdf for every upload.
                    "content-type": file.content_type or "application/octet-stream",
                    "upsert": False,
                },
            )
        )

        print("✅ Supabase upload successful")
        print(f"📌 Upload response: {upload_response}")

    except Exception as e:
        print("❌ Supabase upload failed")
        print(f"❌ Error: {repr(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to Supabase Storage: {str(e)}",
        )

    # =====================================================
    # Step 10: Save document information in DB
    # =====================================================

    print("🗄️ Saving document information to database...")

    doc = Document(
        id=document_id,
        project_id=project_id,
        filename=file.filename,
        file_path=storage_path,
        status="uploaded",
    )

    try:
        db.add(doc)
        db.commit()
        db.refresh(doc)

        print("✅ Document information saved to database")

    except Exception as e:
        print("❌ Database save failed")
        print(f"❌ Error: {repr(e)}")

        # -------------------------------------------------
        # Rollback database
        # -------------------------------------------------
        db.rollback()

        # -------------------------------------------------
        # Remove uploaded Supabase file
        # -------------------------------------------------
        try:
            supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
            print("🗑️ Removed uploaded file from Supabase")
        except Exception as cleanup_error:
            print("⚠️ Failed to remove Supabase file:")
            print(repr(cleanup_error))

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save document information: {str(e)}",
        )

    # =====================================================
    # Step 11: Return response
    # =====================================================

    print("🎉 DOCUMENT UPLOAD COMPLETED")
    print("=" * 60)

    return {
        "message": "Document uploaded successfully",
        "document": {
            "id": doc.id,
            "project_id": doc.project_id,
            "filename": doc.filename,
            "file_path": doc.file_path,
            "storage": "supabase",
            "bucket": SUPABASE_BUCKET,
            "status": doc.status,
            "created_at": (
                doc.created_at.isoformat() if doc.created_at else None
            ),
        },
    }


# =========================================================
# List Documents for a Project
# =========================================================

@router.get("/project/{project_id}")
def list_documents(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Return all documents belonging to a project.
    """

    docs = (
        db.query(Document)
        .filter(Document.project_id == project_id)
        .all()
    )

    return {
        "documents": [
            {
                "id": d.id,
                "project_id": d.project_id,
                "filename": d.filename,
                "file_path": d.file_path,
                "status": d.status,
                "storage": "supabase",
                "bucket": SUPABASE_BUCKET,
                "created_at": (
                    d.created_at.isoformat() if d.created_at else None
                ),
            }
            for d in docs
        ],
        "total": len(docs),
    }


# =========================================================
# Get Document by ID
# =========================================================

@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Return a single document by ID.
    """

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "id": doc.id,
        "project_id": doc.project_id,
        "filename": doc.filename,
        "file_path": doc.file_path,
        "storage": "supabase",
        "bucket": SUPABASE_BUCKET,
        "status": doc.status,
        "created_at": (
            doc.created_at.isoformat() if doc.created_at else None
        ),
    }


# =========================================================
# Delete Document
# =========================================================

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a document from:

    1. Supabase Storage
    2. SQL Database (document + its chunks)

    Note:
    Chroma vectors also need to be deleted separately, if used.
    """

    # -----------------------------------------------------
    # Find document
    # -----------------------------------------------------

    doc = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    storage_path = doc.file_path

    # -----------------------------------------------------
    # Delete from Supabase Storage
    # -----------------------------------------------------

    if storage_path:
        try:
            print(f"🗑️ Deleting from Supabase: {storage_path}")

            supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])

            print("✅ File deleted from Supabase")

        except Exception as e:
            print(f"❌ Supabase delete failed: {repr(e)}")

            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete file from Supabase Storage: {str(e)}",
            )

    # -----------------------------------------------------
    # Delete chunks + document record from SQL
    # -----------------------------------------------------

    try:
        db.query(Chunk).filter(
            Chunk.document_id == document_id
        ).delete(synchronize_session=False)

        db.delete(doc)
        db.commit()

        print("✅ Document deleted from database")

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document from database: {str(e)}",
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
        "storage": "supabase",
        "database": "deleted",
    }