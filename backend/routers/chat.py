"""
Chat router - RAG-powered question answering with history.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend.models import Message
from backend.services.embedder import create_embedding_model
from backend.services.vector_store import load_vector_store
from backend.services.retriever import create_retriever
from backend.services.rag import run_rag


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    query: str
    project_id: Optional[str] = None


# ---------------------------------------------------------
# Ask a question
# ---------------------------------------------------------

@router.post("/ask")
def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Run RAG pipeline: embed query → retrieve → LLM answer.
    """

    try:

        # Embedding model
        embedding_model = create_embedding_model()

        # Load ChromaDB
        db_chroma = load_vector_store(
            embedding_model=embedding_model,
        )

        # Retriever
        retriever = create_retriever(
            vector_store=db_chroma,
            top_k=3,
        )

        # RAG
        result = run_rag(
            query=request.query,
            retriever=retriever,
        )

        # Store messages in DB
        if request.project_id:
            user_msg = Message(
                project_id=request.project_id,
                role="user",
                content=request.query,
            )
            db.add(user_msg)

            ai_msg = Message(
                project_id=request.project_id,
                role="assistant",
                content=result["answer"],
            )
            db.add(ai_msg)
            db.commit()

        return {
            "query": request.query,
            "answer": result["answer"],
            "sources": [
                {
                    "content": doc.page_content[:500],
                    "metadata": doc.metadata,
                }
                for doc in result["documents"]
            ],
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="No vector store found. Please process a document first.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ---------------------------------------------------------
# Get chat history for a project
# ---------------------------------------------------------

@router.get("/history/{project_id}")
def get_chat_history(
    project_id: str,
    db: Session = Depends(get_db),
):
    messages = (
        db.query(Message)
        .filter(Message.project_id == project_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return {
        "project_id": project_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
        "total": len(messages),
    }


# ---------------------------------------------------------
# Clear chat history
# ---------------------------------------------------------

@router.delete("/history/{project_id}")
def clear_chat_history(
    project_id: str,
    db: Session = Depends(get_db),
):
    db.query(Message).filter(Message.project_id == project_id).delete()
    db.commit()

    return {"message": "Chat history cleared"}