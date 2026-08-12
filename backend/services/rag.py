"""
RAG (Retrieval-Augmented Generation) service.

Flow:

User Query
    ↓
Retriever
    ↓
Relevant Documents
    ↓
LLM
    ↓
Final Answer
"""
import os
import json
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

HF_MODEL = os.getenv(
    "HF_MODEL",
    "Qwen/Qwen2.5-7B-Instruct"
)

# ---------------------------------------------------------
# Create RAG LLM
# ---------------------------------------------------------

def create_rag_llm():
    """
    Create the Hugging Face LLM used for final answers.
    """

    print("🧠 Loading RAG LLM...")
    print(f"📌 Model: {HF_MODEL}")

    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        raise ValueError(
            "HF_TOKEN is missing from .env"
        )

    llm_endpoint = HuggingFaceEndpoint(
        repo_id=HF_MODEL,
        task="conversational",
        huggingfacehub_api_token=hf_token,
        temperature=0,
        max_new_tokens=1000,
    )

    llm = ChatHuggingFace(
        llm=llm_endpoint
    )

    print("✅ RAG LLM ready")

    return llm

# ---------------------------------------------------------
# Format retrieved documents
# ---------------------------------------------------------

def format_context(
    documents: List[Document],
) -> str:
    """
    Convert retrieved documents into LLM context.
    """

    if not documents:
        return ""

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        text = (
            document.page_content
            or ""
        )

        metadata = (
            document.metadata
            or {}
        )

        context_parts.append(
            f"""
--- SOURCE {index} ---

CONTENT:
{text}

METADATA:
{json.dumps(
    metadata,
    ensure_ascii=False,
    default=str
)}
"""
        )

    return "\n".join(
        context_parts
    )


# ---------------------------------------------------------
# Build RAG prompt
# ---------------------------------------------------------

def build_rag_prompt(
    query: str,
    documents: List[Document],
) -> str:
    """
    Build the prompt for final answer generation.
    """

    context = format_context(
        documents
    )

    prompt = f"""
You are an AI assistant for a document
question-answering system.

Answer the user's question using ONLY the
information provided in the retrieved documents.

USER QUESTION:
{query}

RETRIEVED DOCUMENTS:
{context}

INSTRUCTIONS:

1. Answer the question clearly and directly.
2. Use information from the retrieved documents.
3. Do not invent facts.
4. If the retrieved documents do not contain
   enough information, say:

   "I don't have enough information to answer
   that question based on the provided documents."

5. If possible, mention the relevant source/page
   information from the metadata.
6. For numerical questions, preserve the exact
   numbers from the documents.
7. If tables are present, use their data carefully.
8. If visual information is present in the context,
   use it when relevant.

FINAL ANSWER:
"""

    return prompt


# ---------------------------------------------------------
# Generate final answer
# ---------------------------------------------------------

def generate_answer(
    query: str,
    documents: List[Document],
    llm=None,
) -> str:
    """
    Generate the final RAG answer.

    Args:
        query:
            User question.

        documents:
            Retrieved relevant documents.

        llm:
            Optional already-created LLM.

    Returns:
        Final answer string.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if not documents:
        return (
            "I don't have enough information "
            "to answer that question based on "
            "the provided documents."
        )

    # Load model once
    if llm is None:
        llm = create_rag_llm()

    print("🤖 Generating final answer...")

    prompt = build_rag_prompt(
        query=query,
        documents=documents,
    )

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": prompt,
            }
        ]
    )

    response = llm.invoke(
        [message]
    )

    answer = response.content

    print("✅ Final answer generated")

    return answer


# ---------------------------------------------------------
# Complete RAG pipeline
# ---------------------------------------------------------

def run_rag(
    query: str,
    retriever,
    llm=None,
    top_k: int = 3,
):
    """
    Complete RAG pipeline.

    Query
      ↓
    Retriever
      ↓
    Top-K documents
      ↓
    LLM
      ↓
    Answer

    Returns:
        answer, retrieved_documents
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    print("\n" + "=" * 60)
    print("🚀 RUNNING RAG PIPELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # Step 1: Retrieval
    # -----------------------------------------------------

    print("\n🔎 Step 1: Retrieving documents...")

    documents = retriever.invoke(
        query
    )

    # Limit results
    documents = documents[:top_k]

    print(
        f"✅ Retrieved "
        f"{len(documents)} documents"
    )

    # -----------------------------------------------------
    # Step 2: Generate answer
    # -----------------------------------------------------

    print("\n🤖 Step 2: Generating answer...")

    answer = generate_answer(
        query=query,
        documents=documents,
        llm=llm,
    )

    # -----------------------------------------------------
    # Step 3: Return
    # -----------------------------------------------------

    print("\n🎉 RAG completed")

    return {
        "query": query,
        "answer": answer,
        "documents": documents,
    }


# ---------------------------------------------------------
# Simple answer helper
# ---------------------------------------------------------

def ask(
    query: str,
    retriever,
    llm=None,
):
    """
    Simple helper that returns only the answer.
    """

    result = run_rag(
        query=query,
        retriever=retriever,
        llm=llm,
    )

    return result["answer"]


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "RAG service loaded successfully."
    )