"""
Retriever service.

Loads the ChromaDB vector store and retrieves
the most relevant document chunks for a user query.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_TOP_K = 3

DEFAULT_SEARCH_TYPE = "similarity"

DEFAULT_PERSIST_DIRECTORY = "backend/chroma_db"

DEFAULT_COLLECTION_NAME = "openslate_documents"


# ---------------------------------------------------------
# Create retriever
# ---------------------------------------------------------

def create_retriever(
    vector_store,
    top_k: int = DEFAULT_TOP_K,
    search_type: str = DEFAULT_SEARCH_TYPE,
):
    """
    Create a LangChain retriever from ChromaDB.

    Args:
        vector_store:
            Chroma vector store created by vector_store.py.

        top_k:
            Number of relevant chunks to retrieve.

        search_type:
            Chroma search method.

    Returns:
        LangChain retriever.
    """

    if vector_store is None:
        raise ValueError(
            "Vector store cannot be None."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0."
        )

    print("🔎 Creating retriever...")
    print(
        f"📌 Search type: {search_type}"
    )
    print(
        f"📌 Top K: {top_k}"
    )

    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": top_k
        },
    )

    print("✅ Retriever created")

    return retriever


# ---------------------------------------------------------
# Retrieve documents
# ---------------------------------------------------------

def retrieve_documents(
    retriever,
    query: str,
) -> List[Document]:
    """
    Retrieve relevant documents for a query.

    Args:
        retriever:
            LangChain retriever.

        query:
            User question.

    Returns:
        List of relevant documents.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if retriever is None:
        raise ValueError(
            "Retriever cannot be None."
        )

    print("\n🔍 Searching vector database...")
    print(
        f"❓ Query: {query}"
    )

    documents = retriever.invoke(
        query
    )

    print(
        f"✅ Retrieved "
        f"{len(documents)} documents"
    )

    return documents


# ---------------------------------------------------------
# Display retrieved documents
# ---------------------------------------------------------

def display_retrieved_documents(
    documents: List[Document],
):
    """
    Display retrieved chunks for debugging.
    """

    if not documents:
        print(
            "⚠️ No relevant documents found."
        )
        return

    print("\n" + "=" * 60)
    print("📚 RETRIEVED DOCUMENTS")
    print("=" * 60)

    for index, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"\n--- Document {index} ---"
        )

        text = (
            document.page_content
            or ""
        )

        print(
            f"Characters: {len(text)}"
        )

        print(
            f"Content:\n{text[:1000]}"
        )

        if document.metadata:

            print(
                f"\nMetadata:"
            )

            for key, value in (
                document.metadata.items()
            ):

                # Don't print huge base64 image data
                if key == "original_content":
                    print(
                        "  original_content: "
                        "[stored]"
                    )
                else:
                    print(
                        f"  {key}: {value}"
                    )


# ---------------------------------------------------------
# Similarity search directly
# ---------------------------------------------------------

def similarity_search(
    vector_store,
    query: str,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Perform similarity search directly on ChromaDB.

    This is useful when you don't need a persistent
    retriever object.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    if vector_store is None:
        raise ValueError(
            "Vector store cannot be None."
        )

    print(
        f"🔍 Similarity search: {query}"
    )

    documents = (
        vector_store.similarity_search(
            query,
            k=top_k,
        )
    )

    print(
        f"✅ Found {len(documents)} documents"
    )

    return documents


# ---------------------------------------------------------
# Complete retrieval pipeline
# ---------------------------------------------------------

def search(
    vector_store,
    query: str,
    top_k: int = DEFAULT_TOP_K,
):
    """
    Complete retrieval pipeline.

    Vector Store
        ↓
    Retriever
        ↓
    Relevant chunks
    """

    retriever = create_retriever(
        vector_store=vector_store,
        top_k=top_k,
    )

    documents = retrieve_documents(
        retriever=retriever,
        query=query,
    )

    display_retrieved_documents(
        documents
    )

    return documents


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Retriever service loaded successfully."
    )

    print(
        "The retriever requires an existing "
        "ChromaDB vector store."
    )