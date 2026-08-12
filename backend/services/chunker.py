"""
Document chunking service.

Takes elements extracted by Unstructured and creates
semantic chunks based on document titles/headings.
"""

from typing import List

from unstructured.chunking.title import chunk_by_title


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MAX_CHARACTERS = 3000
NEW_AFTER_N_CHARS = 2400
COMBINE_TEXT_UNDER_N_CHARS = 500


# ---------------------------------------------------------
# Main chunking function
# ---------------------------------------------------------

def create_chunks(elements: List):
    """
    Create semantic chunks from Unstructured elements.

    Args:
        elements:
            Elements returned by extractor.py.

    Returns:
        List of chunked Unstructured elements.
    """

    if not elements:
        raise ValueError(
            "No elements were provided for chunking."
        )

    print("✂️ Creating document chunks...")
    print(f"📄 Input elements: {len(elements)}")

    chunks = chunk_by_title(
        elements,

        max_characters=MAX_CHARACTERS,

        new_after_n_chars=NEW_AFTER_N_CHARS,

        combine_text_under_n_chars=COMBINE_TEXT_UNDER_N_CHARS,
    )

    print(
        f"✅ Created {len(chunks)} chunks"
    )

    return chunks


# ---------------------------------------------------------
# Chunk statistics
# ---------------------------------------------------------

def get_chunk_statistics(chunks: List):
    """
    Display basic statistics about generated chunks.
    """

    if not chunks:
        print("⚠️ No chunks available.")
        return

    total_characters = sum(
        len(str(chunk.text or ""))
        for chunk in chunks
    )

    average_characters = (
        total_characters / len(chunks)
    )

    largest_chunk = max(
        len(str(chunk.text or ""))
        for chunk in chunks
    )

    smallest_chunk = min(
        len(str(chunk.text or ""))
        for chunk in chunks
    )

    print("\n📊 Chunk Statistics")
    print("=" * 50)

    print(
        f"Total chunks       : {len(chunks)}"
    )

    print(
        f"Total characters   : {total_characters}"
    )

    print(
        f"Average characters : {average_characters:.2f}"
    )

    print(
        f"Largest chunk      : {largest_chunk}"
    )

    print(
        f"Smallest chunk     : {smallest_chunk}"
    )


# ---------------------------------------------------------
# Preview chunks
# ---------------------------------------------------------

def preview_chunks(
    chunks: List,
    number_of_chunks: int = 5
):
    """
    Display a preview of generated chunks.
    """

    if not chunks:
        print("⚠️ No chunks to preview.")
        return

    print("\n🔎 Chunk Preview")
    print("=" * 60)

    for index, chunk in enumerate(
        chunks[:number_of_chunks],
        start=1
    ):

        text = str(chunk.text or "")

        print(
            f"\n--- Chunk {index} ---"
        )

        print(
            f"Characters: {len(text)}"
        )

        print(
            text[:500]
        )

        if len(text) > 500:
            print("...")


# ---------------------------------------------------------
# Complete chunking pipeline
# ---------------------------------------------------------

def chunk_document(elements: List):
    """
    Complete chunking pipeline.

    Elements
        ↓
    Semantic chunking
        ↓
    Statistics
        ↓
    Preview

    Returns:
        List of chunks.
    """

    chunks = create_chunks(
        elements
    )

    get_chunk_statistics(
        chunks
    )

    preview_chunks(
        chunks
    )

    return chunks


# ---------------------------------------------------------
# Example usage
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "This module expects extracted "
        "elements from extractor.py."
    )

    print(
        "Use:"
    )

    print(
        "from backend.services.extractor import extract_document"
    )

    print(
        "from backend.services.chunker import chunk_document"
    )

    print(
        "elements = extract_document('document.pdf')"
    )

    print(
        "chunks = chunk_document(elements)"
    )