"""
Embedding service.

Converts document chunks into vector embeddings
using a Hugging Face sentence-transformer model.
"""

from typing import List

from langchain_huggingface import HuggingFaceEmbeddings


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Create embedding model
# ---------------------------------------------------------

def create_embedding_model():
    """
    Initialize the Hugging Face embedding model.

    Returns:
        HuggingFaceEmbeddings
    """

    print("🧠 Loading embedding model...")
    print(f"📌 Model: {EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    print("✅ Embedding model loaded")

    return embeddings


# ---------------------------------------------------------
# Embed documents
# ---------------------------------------------------------

def embed_chunks(chunks: List, embeddings=None):
    """
    Convert document chunks into embeddings.

    Args:
        chunks:
            Chunks created by chunker.py.

        embeddings:
            Optional already-loaded embedding model.

    Returns:
        List of embedding vectors.
    """

    if not chunks:
        raise ValueError(
            "No chunks provided for embedding."
        )

    if embeddings is None:
        embeddings = create_embedding_model()

    print("🔢 Creating embeddings...")
    print(f"📄 Number of chunks: {len(chunks)}")

    texts = [
        str(chunk.text or "")
        for chunk in chunks
    ]

    # Remove empty chunks
    texts = [
        text
        for text in texts
        if text.strip()
    ]

    if not texts:
        raise ValueError(
            "All chunks are empty."
        )

    vectors = embeddings.embed_documents(
        texts
    )

    print(
        f"✅ Created {len(vectors)} embeddings"
    )

    if vectors:
        print(
            f"📐 Embedding dimension: "
            f"{len(vectors[0])}"
        )

    return vectors


# ---------------------------------------------------------
# Embed a single query
# ---------------------------------------------------------

def embed_query(
    query: str,
    embeddings=None
):
    """
    Convert a user query into an embedding vector.

    This is used later by the retriever.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if embeddings is None:
        embeddings = create_embedding_model()

    vector = embeddings.embed_query(
        query
    )

    print(
        f"✅ Query embedded "
        f"(dimension={len(vector)})"
    )

    return vector


# ---------------------------------------------------------
# Complete embedding pipeline
# ---------------------------------------------------------

def create_embeddings(chunks: List):
    """
    Complete embedding pipeline.

    chunks
        ↓
    embedding model
        ↓
    vectors
    """

    embeddings = create_embedding_model()

    vectors = embed_chunks(
        chunks,
        embeddings
    )

    return embeddings, vectors


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Embedding service loaded successfully."
    )

    print(
        f"Model: {EMBEDDING_MODEL}"
    )