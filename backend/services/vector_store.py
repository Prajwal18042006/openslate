"""
Vector store service.

Converts chunks to LangChain Documents and stores them
directly in Chroma Cloud.
"""

import os
from typing import List

import chromadb
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_core.documents import Document


# =========================================================
# Load environment variables
# =========================================================

load_dotenv()


# =========================================================
# Configuration
# =========================================================

COLLECTION_NAME = "openslate_documents"


CHROMA_API_KEY = os.getenv(
    "CHROMA_API_KEY"
)

CHROMA_TENANT = os.getenv(
    "CHROMA_TENANT"
)

CHROMA_DATABASE = os.getenv(
    "CHROMA_DATABASE"
)


# =========================================================
# Chroma Cloud Client
# =========================================================

def get_chroma_client():

    if not CHROMA_API_KEY:
        raise ValueError(
            "CHROMA_API_KEY is missing from .env"
        )

    if not CHROMA_TENANT:
        raise ValueError(
            "CHROMA_TENANT is missing from .env"
        )

    if not CHROMA_DATABASE:
        raise ValueError(
            "CHROMA_DATABASE is missing from .env"
        )

    print(
        "☁️ Connecting to Chroma Cloud..."
    )

    print(
        f"🏢 Tenant: {CHROMA_TENANT}"
    )

    print(
        f"🗄️ Database: {CHROMA_DATABASE}"
    )

    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )

    print(
        "✅ Chroma Cloud connected"
    )

    return client


# =========================================================
# Convert chunks to LangChain Documents
# =========================================================

def convert_chunks_to_documents(
    chunks: List,
) -> List[Document]:
    """
    Convert chunks into LangChain Documents.

    IMPORTANT:
    Only very small metadata is stored in Chroma.

    We intentionally DO NOT store:
        - orig_elements
        - filename
        - category
        - content_type
        - large JSON objects
        - Unstructured metadata

    This prevents Chroma Cloud metadata quota errors.
    """

    if not chunks:
        raise ValueError(
            "No chunks provided."
        )

    documents = []

    for index, chunk in enumerate(chunks):

        # =================================================
        # Get text
        # =================================================

        if isinstance(
            chunk,
            Document,
        ):

            text = str(
                chunk.page_content or ""
            ).strip()

            source_metadata = (
                chunk.metadata or {}
            )

        else:

            text = str(
                getattr(
                    chunk,
                    "text",
                    "",
                )
                or ""
            ).strip()

            source_metadata = (
                getattr(
                    chunk,
                    "metadata",
                    None,
                )
                or {}
            )

        # =================================================
        # Skip empty chunks
        # =================================================

        if not text:
            continue

        # =================================================
        # VERY SMALL METADATA
        # =================================================

        metadata = {
            "chunk_id": int(index),
        }

        # -------------------------------------------------
        # Page number only
        # -------------------------------------------------

        page_number = source_metadata.get(
            "page_number"
        )

        if page_number is not None:

            try:

                metadata["page_number"] = int(
                    page_number
                )

            except (
                ValueError,
                TypeError,
            ):

                pass

        # =================================================
        # Create Document
        # =================================================

        document = Document(
            page_content=text,
            metadata=metadata,
        )

        documents.append(
            document
        )

    print(
        f"📄 Converted {len(documents)} "
        f"chunks to Chroma-safe Documents"
    )

    # -----------------------------------------------------
    # Debug metadata size
    # -----------------------------------------------------

    total_metadata_chars = sum(
        len(str(doc.metadata))
        for doc in documents
    )

    print(
        f"🧹 Total metadata characters: "
        f"{total_metadata_chars}"
    )

    return documents


# =========================================================
# Create / Add documents to Chroma Cloud
# =========================================================

def create_vector_store(
    chunks: List,
    embedding_model,
    collection_name: str = COLLECTION_NAME,
):
    """
    Create or load a Chroma Cloud collection
    and add documents to it.
    """

    if not chunks:

        raise ValueError(
            "Cannot create vector store "
            "without chunks."
        )

    if embedding_model is None:

        raise ValueError(
            "Embedding model is required."
        )

    print(
        "☁️ Creating Chroma Cloud vector store..."
    )

    print(
        f"📦 Collection: {collection_name}"
    )

    # =====================================================
    # Connect to Chroma Cloud
    # =====================================================

    client = get_chroma_client()

    # =====================================================
    # Convert chunks
    # =====================================================

    documents = (
        convert_chunks_to_documents(
            chunks
        )
    )

    if not documents:

        raise ValueError(
            "No valid documents available "
            "after conversion."
        )

    # =====================================================
    # Create LangChain Chroma instance
    # =====================================================

    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )

    # =====================================================
    # Add documents
    # =====================================================

    print(
        f"⬆️ Uploading {len(documents)} "
        f"documents to Chroma Cloud..."
    )

    vector_store.add_documents(
        documents=documents
    )

    print(
        "✅ Documents successfully stored "
        "in Chroma Cloud"
    )

    print(
        f"📦 Collection: {collection_name}"
    )

    print(
        f"📄 Documents stored: "
        f"{len(documents)}"
    )

    return vector_store


# =========================================================
# Load existing Chroma Cloud vector store
# =========================================================

def load_vector_store(
    embedding_model,
    collection_name: str = COLLECTION_NAME,
):
    """
    Load an existing Chroma Cloud collection.
    """

    if embedding_model is None:

        raise ValueError(
            "Embedding model is required."
        )

    print(
        "☁️ Loading Chroma Cloud vector store..."
    )

    client = get_chroma_client()

    vector_store = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )

    print(
        "✅ Chroma Cloud vector store loaded"
    )

    print(
        f"📦 Collection: {collection_name}"
    )

    return vector_store


# =========================================================
# Add new chunks
# =========================================================

def add_chunks(
    vector_store,
    chunks: List,
):
    """
    Add additional chunks to Chroma Cloud.
    """

    if not chunks:

        raise ValueError(
            "No chunks provided."
        )

    documents = (
        convert_chunks_to_documents(
            chunks
        )
    )

    if not documents:

        raise ValueError(
            "No valid documents to add."
        )

    vector_store.add_documents(
        documents=documents
    )

    print(
        f"✅ Added {len(documents)} "
        f"new chunks to Chroma Cloud"
    )

    return vector_store


# =========================================================
# Get collection count
# =========================================================

def get_collection_count(
    vector_store,
):
    """
    Return number of stored vectors.
    """

    collection = (
        vector_store._collection
    )

    count = collection.count()

    print(
        f"📊 Vectors stored: {count}"
    )

    return count


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    print(
        "Chroma Cloud vector store "
        "service loaded successfully."
    )