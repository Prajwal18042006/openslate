"""
SQLAlchemy database models for OpenSlate.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from backend.database import Base


# =========================================================
# PROJECT
# =========================================================

class Project(Base):

    __tablename__ = "projects"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Project → Documents
    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan",
    )


# =========================================================
# DOCUMENT
# =========================================================

class Document(Base):

    __tablename__ = "documents"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        String,
        ForeignKey(
            "projects.id"
        ),
        nullable=False,
    )

    filename = Column(
        String,
        nullable=False,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        default="uploaded",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Document → Project
    project = relationship(
        "Project",
        back_populates="documents",
    )

    # Document → Chunks
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


# =========================================================
# CHUNK
# =========================================================

class Chunk(Base):

    __tablename__ = "chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        String,
        ForeignKey(
            "documents.id"
        ),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    page_number = Column(
        Integer,
        nullable=True,
    )

    content_type = Column(
        String,
        default="text",
    )

    char_count = Column(
        Integer,
        nullable=True,
    )

    chunk_index = Column(
        Integer,
        nullable=True,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    # Chunk → Document
    document = relationship(
        "Document",
        back_populates="chunks",
    )


# =========================================================
# MESSAGE
# =========================================================

class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        String,
        ForeignKey(
            "projects.id"
        ),
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )