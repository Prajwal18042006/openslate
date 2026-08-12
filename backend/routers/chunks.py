"""
Chunks router — list and inspect document chunks.
"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Chunk, Document


router = APIRouter(
    prefix="/documents",
    tags=["Chunks"],
)


@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: str,
    q: Optional[str] = Query(None, description="Search chunk content"),
    type: Optional[str] = Query(None, alias="type", description="Filter by content type"),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    query = db.query(Chunk).filter(Chunk.document_id == document_id)

    if type:
        query = query.filter(Chunk.content_type.ilike(f"%{type}%"))

    if q:
        query = query.filter(Chunk.content.ilike(f"%{q}%"))

    chunks = query.order_by(Chunk.chunk_index.asc(), Chunk.id.asc()).all()

    return {
        "document_id": document_id,
        "filename": doc.filename,
        "status": doc.status,
        "chunks": [
            {
                "id": c.id,
                "index": c.chunk_index if c.chunk_index is not None else i,
                "type": c.content_type or "text",
                "page_number": c.page_number,
                "content": c.content,
                "summary": c.summary,
                "char_count": c.char_count or len(c.content or ""),
            }
            for i, c in enumerate(chunks)
        ],
        "total": len(chunks),
    }


@router.get("/{document_id}/chunks/{chunk_id}")
def get_chunk_detail(
    document_id: str,
    chunk_id: int,
    db: Session = Depends(get_db),
):
    chunk = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id, Chunk.id == chunk_id)
        .first()
    )

    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")

    return {
        "id": chunk.id,
        "document_id": document_id,
        "index": chunk.chunk_index,
        "type": chunk.content_type or "text",
        "page_number": chunk.page_number,
        "content": chunk.content,
        "summary": chunk.summary,
        "char_count": chunk.char_count or len(chunk.content or ""),
        "created_at": chunk.created_at.isoformat() if chunk.created_at else None,
    }
