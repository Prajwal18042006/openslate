"""
Pipeline router - runs the full document ingestion pipeline.

Steps:

1. Download document from Supabase Storage
2. Extract   → Unstructured elements
3. Chunk     → Semantic chunks by title
4. Summarize → AI-enhanced summaries
5. Embed     → Sentence-transformer vectors
6. Store     → ChromaDB / Chroma Cloud

Also supports:

POST /process/{document_id}
    → Process one document

POST /process-project/{project_id}
    → Process all documents of a project
"""

import json
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from supabase import create_client, Client

from backend.database import get_db
from backend.models import Document, Chunk


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"],
)


# =========================================================
# Supabase Configuration
# =========================================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)

SUPABASE_BUCKET = os.getenv(
    "SUPABASE_BUCKET",
    "documents",
)


if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing from environment variables"
    )


if not SUPABASE_SECRET_KEY:
    raise ValueError(
        "SUPABASE_SECRET_KEY is missing from environment variables"
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)


print(
    "☁️ Pipeline Supabase Storage configured"
)

print(
    f"📦 Bucket: {SUPABASE_BUCKET}"
)


# =========================================================
# Parse Content Type
# =========================================================

def _parse_content_type(
    metadata: dict,
) -> str:
    """
    Extract a simple content type from metadata.
    """

    raw = metadata.get(
        "content_types",
        "text",
    )

    if isinstance(raw, str):

        try:

            types = json.loads(raw)

            if types:
                return types[0]

        except json.JSONDecodeError:

            return raw

    return "text"


# =========================================================
# Persist Processed Chunks
# =========================================================

def persist_chunks(
    db: Session,
    document_id: str,
    processed_documents,
) -> int:
    """
    Save processed chunks to SQL for UI inspection.
    """

    # -----------------------------------------------------
    # Delete old chunks
    # -----------------------------------------------------

    db.query(Chunk).filter(
        Chunk.document_id == document_id
    ).delete()

    stored_count = 0

    # -----------------------------------------------------
    # Store new chunks
    # -----------------------------------------------------

    for index, doc in enumerate(
        processed_documents
    ):

        metadata = dict(
            doc.metadata or {}
        )

        content = str(
            doc.page_content or ""
        ).strip()

        if not content:
            continue

        db.add(
            Chunk(
                document_id=document_id,
                content=content,
                page_number=metadata.get(
                    "page_number"
                ),
                content_type=_parse_content_type(
                    metadata
                ),
                char_count=len(content),
                chunk_index=index,
                summary=(
                    content[:500]
                    if len(content) > 500
                    else content
                ),
            )
        )

        stored_count += 1

    db.commit()

    return stored_count


# =========================================================
# Download Document From Supabase
# =========================================================

def download_document_from_supabase(
    storage_path: str,
    document_id: str,
) -> str:
    """
    Download a document from Supabase Storage
    into a temporary local file.

    Returns:
        Temporary file path.
    """

    if not storage_path:

        raise ValueError(
            "Document storage path is empty."
        )

    print("\n" + "-" * 60)

    print(
        "☁️ Downloading document from Supabase"
    )

    print(
        f"📦 Bucket: {SUPABASE_BUCKET}"
    )

    print(
        f"📁 Storage path: {storage_path}"
    )

    print("-" * 60)

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    try:

        file_bytes = (
            supabase
            .storage
            .from_(SUPABASE_BUCKET)
            .download(storage_path)
        )

    except Exception as e:

        print(
            "❌ Failed to download document "
            "from Supabase"
        )

        print(
            f"❌ Error: {repr(e)}"
        )

        raise RuntimeError(
            "Could not download document "
            f"from Supabase Storage: {str(e)}"
        )

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file_bytes:

        raise RuntimeError(
            "Downloaded document is empty."
        )

    print(
        f"✅ Downloaded {len(file_bytes)} bytes"
    )

    # -----------------------------------------------------
    # Determine file extension
    # -----------------------------------------------------

    suffix = Path(
        storage_path
    ).suffix.lower()

    if not suffix:
        suffix = ".pdf"

    # -----------------------------------------------------
    # Create temporary file
    # -----------------------------------------------------

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        prefix=f"openslate_{document_id}_",
    )

    try:

        temp_file.write(
            file_bytes
        )

        temp_file.flush()

    finally:

        temp_file.close()

    print(
        f"📄 Temporary file created: "
        f"{temp_file.name}"
    )

    return temp_file.name


# =========================================================
# Process ONE Document
# =========================================================

@router.post(
    "/process/{document_id}"
)
def process_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Run the complete document ingestion pipeline
    for a single document stored in Supabase.

    Flow:

    Supabase
        ↓
    Temporary local file
        ↓
    Extract
        ↓
    Chunk
        ↓
    Summarize
        ↓
    Embed
        ↓
    Chroma Cloud
    """

    # =====================================================
    # IMPORTANT:
    # Lazy imports
    #
    # These heavy dependencies are imported ONLY when
    # the user actually processes a document.
    #
    # This keeps FastAPI startup lightweight on Render.
    # =====================================================

    from backend.services.extractor import (
        extract_document
    )

    from backend.services.chunker import (
        chunk_document
    )

    from backend.services.summarizer import (
        summarize_chunks
    )

    from backend.services.embedder import (
        create_embedding_model
    )

    from backend.services.vector_store import (
        create_vector_store
    )

    # =====================================================
    # Find Document in DB
    # =====================================================

    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not doc:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # =====================================================
    # Storage Path
    # =====================================================

    storage_path = doc.file_path

    if not storage_path:

        raise HTTPException(
            status_code=404,
            detail=(
                "Document has no Supabase "
                "storage path"
            ),
        )

    print("\n" + "=" * 70)

    print(
        "🚀 STARTING DOCUMENT PIPELINE"
    )

    print("=" * 70)

    print(
        f"🆔 Document ID: {document_id}"
    )

    print(
        f"📄 Filename: {doc.filename}"
    )

    print(
        f"☁️ Storage path: {storage_path}"
    )

    temp_file_path = None

    steps = {}

    try:

        # =================================================
        # Step 0: Download
        # =================================================

        doc.status = "downloading"

        db.commit()

        temp_file_path = (
            download_document_from_supabase(
                storage_path=storage_path,
                document_id=document_id,
            )
        )

        steps["download"] = {
            "status": "done",
            "storage": "supabase",
            "bucket": SUPABASE_BUCKET,
            "storage_path": storage_path,
        }

        # =================================================
        # Step 1: Extract
        # =================================================

        doc.status = "extracting"

        db.commit()

        print(
            "\n📄 Step 1: Extracting..."
        )

        print(
            f"📂 Local temporary file: "
            f"{temp_file_path}"
        )

        elements = extract_document(
            temp_file_path
        )

        steps["extract"] = {
            "status": "done",
            "elements": len(elements),
            "element_types": list(
                set(
                    type(e).__name__
                    for e in elements
                )
            ),
        }

        print(
            f"✅ Extracted "
            f"{len(elements)} elements"
        )

        # =================================================
        # Step 2: Chunk
        # =================================================

        doc.status = "chunking"

        db.commit()

        print(
            "\n✂️ Step 2: Chunking..."
        )

        chunks = chunk_document(
            elements
        )

        # -------------------------------------------------
        # Chunk Statistics
        # -------------------------------------------------

        chunk_sizes = [
            len(
                str(
                    getattr(
                        c,
                        "text",
                        "",
                    )
                    or ""
                )
            )
            for c in chunks
        ]

        steps["chunk"] = {
            "status": "done",
            "total_chunks": len(chunks),

            "avg_chars": (
                round(
                    sum(chunk_sizes)
                    / len(chunk_sizes),
                    1,
                )
                if chunk_sizes
                else 0
            ),

            "max_chars": (
                max(chunk_sizes)
                if chunk_sizes
                else 0
            ),

            "min_chars": (
                min(chunk_sizes)
                if chunk_sizes
                else 0
            ),
        }

        print(
            f"✅ Created "
            f"{len(chunks)} chunks"
        )

        # =================================================
        # Step 3: Summarize
        # =================================================

        doc.status = "summarizing"

        db.commit()

        print(
            "\n🧠 Step 3: Summarizing..."
        )

        processed_documents = (
            summarize_chunks(chunks)
        )

        steps["summarize"] = {
            "status": "done",
            "processed": len(
                processed_documents
            ),
        }

        print(
            f"✅ Summarized "
            f"{len(processed_documents)} chunks"
        )

        # =================================================
        # Save Chunks to SQL
        # =================================================

        stored_count = persist_chunks(
            db,
            document_id,
            processed_documents,
        )

        steps["chunk"][
            "stored_in_db"
        ] = stored_count

        # =================================================
        # Step 4: Embed
        # =================================================

        doc.status = "embedding"

        db.commit()

        print(
            "\n🔢 Step 4: Loading "
            "embedding model..."
        )

        embedding_model = (
            create_embedding_model()
        )

        steps["embed"] = {
            "status": "done",
            "model": (
                "sentence-transformers/"
                "all-MiniLM-L6-v2"
            ),
            "dimension": 384,
        }

        print(
            "✅ Embedding model loaded"
        )

        # =================================================
        # Step 5: Chroma Cloud
        # =================================================

        doc.status = "storing"

        db.commit()

        print(
            "\n🗄️ Step 5: Creating "
            "vector store..."
        )

        db_chroma = create_vector_store(
            chunks=processed_documents,
            embedding_model=embedding_model,
        )

        steps["store"] = {
            "status": "done",
            "collection": (
                "openslate_documents"
            ),
            "vectors_stored": len(
                processed_documents
            ),
        }

        print(
            "🎉 Pipeline completed!"
        )

        # =================================================
        # Mark Ready
        # =================================================

        doc.status = "ready"

        db.commit()

        return {
            "message": (
                "Document processed successfully"
            ),
            "document_id": document_id,
            "filename": doc.filename,
            "status": "ready",
            "steps": steps,
        }

    # =====================================================
    # HTTP Exception
    # =====================================================

    except HTTPException:

        doc.status = "error"

        db.commit()

        raise

    # =====================================================
    # General Exception
    # =====================================================

    except Exception as e:

        print(
            f"❌ Pipeline failed: {repr(e)}"
        )

        doc.status = "error"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Pipeline failed: {str(e)}"
            ),
        )

    # =====================================================
    # Cleanup Temporary File
    # =====================================================

    finally:

        if temp_file_path:

            try:

                temp_path = Path(
                    temp_file_path
                )

                if temp_path.exists():

                    temp_path.unlink()

                    print(
                        "🧹 Temporary file deleted"
                    )

            except Exception as cleanup_error:

                print(
                    "⚠️ Failed to delete "
                    "temporary file:"
                )

                print(
                    repr(cleanup_error)
                )


# =========================================================
# Process ALL Documents of a Project
# =========================================================

@router.post(
    "/process-project/{project_id}"
)
def process_project_documents(
    project_id: str,
    db: Session = Depends(get_db),
):
    """
    Process all uploaded documents
    belonging to a project.

    Each document uses the existing
    single-document pipeline.
    """

    # =====================================================
    # Find All Project Documents
    # =====================================================

    documents = (
        db.query(Document)
        .filter(
            Document.project_id == project_id
        )
        .all()
    )

    if not documents:

        raise HTTPException(
            status_code=404,
            detail=(
                "No documents found "
                "for this project"
            ),
        )

    print("\n" + "=" * 70)

    print(
        "🚀 PROCESSING ALL PROJECT DOCUMENTS"
    )

    print("=" * 70)

    print(
        f"📁 Project ID: {project_id}"
    )

    print(
        f"📄 Total documents: "
        f"{len(documents)}"
    )

    results = []

    # =====================================================
    # Process Every Document
    # =====================================================

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"📄 DOCUMENT "
            f"{index}/{len(documents)}"
        )

        print(
            f"📝 Filename: "
            f"{document.filename}"
        )

        print(
            f"🆔 ID: "
            f"{document.id}"
        )

        print("-" * 70)

        try:

            # -------------------------------------------------
            # Reuse Existing Pipeline
            # -------------------------------------------------

            result = process_document(
                document_id=document.id,
                db=db,
            )

            results.append({
                "document_id": document.id,
                "filename": document.filename,
                "status": "ready",
                "result": result,
            })

        except HTTPException as e:

            print(
                f"❌ Failed: "
                f"{document.filename}"
            )

            results.append({
                "document_id": document.id,
                "filename": document.filename,
                "status": "error",
                "error": e.detail,
            })

        except Exception as e:

            print(
                f"❌ Failed: "
                f"{document.filename}"
            )

            print(
                f"❌ Error: {repr(e)}"
            )

            results.append({
                "document_id": document.id,
                "filename": document.filename,
                "status": "error",
                "error": str(e),
            })

    # =====================================================
    # Summary
    # =====================================================

    successful = sum(
        1
        for item in results
        if item["status"] == "ready"
    )

    failed = (
        len(results) - successful
    )

    print("\n" + "=" * 70)

    print(
        "🎉 PROJECT PROCESSING COMPLETED"
    )

    print("=" * 70)

    print(
        f"📄 Total: {len(results)}"
    )

    print(
        f"✅ Successful: {successful}"
    )

    print(
        f"❌ Failed: {failed}"
    )

    return {
        "message": (
            "Project documents processed"
        ),
        "project_id": project_id,
        "total_documents": len(documents),
        "successful": successful,
        "failed": failed,
        "documents": results,
    }


# =========================================================
# Pipeline Status
# =========================================================

@router.get(
    "/status/{document_id}"
)
def get_pipeline_status(
    document_id: str,
    db: Session = Depends(get_db),
):
    """
    Get current processing status
    for a document.
    """

    doc = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not doc:

        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return {
        "document_id": document_id,
        "filename": doc.filename,
        "status": doc.status,
    }