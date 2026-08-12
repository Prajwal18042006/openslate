"""
Projects router - CRUD with SQLAlchemy persistence.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from backend.database import get_db
from backend.models import Project, Document
from backend.schemas import ProjectCreate, ProjectOut, ProjectListOut


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)


# ---------------------------------------------------------
# Create Project
# ---------------------------------------------------------

@router.post("/", response_model=dict)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    db_project = Project(
        id=str(uuid.uuid4()),
        name=project.name,
        description=project.description,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return {
        "message": "Project created successfully",
        "project": {
            "id": db_project.id,
            "name": db_project.name,
            "description": db_project.description,
            "created_at": db_project.created_at.isoformat() if db_project.created_at else None,
        }
    }


# ---------------------------------------------------------
# Get All Projects
# ---------------------------------------------------------

@router.get("/")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()

    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "document_count": len(p.documents),
            }
            for p in projects
        ],
        "total": len(projects),
    }


# ---------------------------------------------------------
# Get Single Project
# ---------------------------------------------------------

@router.get("/{project_id}")
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "document_count": len(project.documents),
    }


# ---------------------------------------------------------
# Delete Project
# ---------------------------------------------------------

@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"message": "Project deleted successfully"}