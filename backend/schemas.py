"""
Pydantic schemas for OpenSlate Mini API.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# =========================================================
# PROJECT SCHEMAS
# =========================================================

class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectListOut(BaseModel):
    projects: List[ProjectOut]
    total: int


# =========================================================
# DOCUMENT SCHEMAS
# =========================================================

class DocumentOut(BaseModel):
    id: str
    project_id: str
    filename: str
    file_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListOut(BaseModel):
    documents: List[DocumentOut]
    total: int


# =========================================================
# PIPELINE SCHEMAS
# =========================================================

class PipelineResult(BaseModel):
    document_id: str
    status: str
    steps: dict
    message: str


# =========================================================
# CHAT SCHEMAS
# =========================================================

class ChatRequest(BaseModel):
    query: str
    project_id: Optional[str] = None


class SourceDocument(BaseModel):
    content: str
    metadata: dict


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceDocument]


class MessageOut(BaseModel):
    id: int
    project_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
