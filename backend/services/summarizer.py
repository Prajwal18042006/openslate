"""
Document summarization service.

Creates AI-enhanced summaries for document chunks
containing text, tables, and images.
"""

import json
import base64
from typing import List
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


load_dotenv()

HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"


# ---------------------------------------------------------
# Create Hugging Face Vision LLM
# ---------------------------------------------------------
def create_summarizer():
    """
    Create Hugging Face summarization model.
    """

    print("🧠 Loading Hugging Face summarization model...")
    print(f"📌 Model: {HF_MODEL}")

    hf_token = os.getenv("HF_TOKEN")

    if not hf_token:
        raise ValueError(
            "HF_TOKEN is missing from .env"
        )

    llm = HuggingFaceEndpoint(
        repo_id=HF_MODEL,
        task="conversational",
        huggingfacehub_api_token=hf_token,
        temperature=0,
        max_new_tokens=800,
    )

    chat_model = ChatHuggingFace(
        llm=llm
    )

    print("✅ Summarization model ready")

    return chat_model
# ---------------------------------------------------------
# Separate content types
# ---------------------------------------------------------

def separate_content_types(chunk):
    """
    Extract text, tables and images from an Unstructured chunk.
    """

    content_data = {
        "text": str(
            getattr(chunk, "text", "") or ""
        ),
        "tables": [],
        "images": [],
        "types": [],
    }

    # ---------------------------------------------
    # Always consider text
    # ---------------------------------------------

    if content_data["text"].strip():
        content_data["types"].append("text")

    # ---------------------------------------------
    # Original elements
    # ---------------------------------------------

    metadata = getattr(
        chunk,
        "metadata",
        None
    )

    if metadata is None:
        return content_data

    original_elements = getattr(
        metadata,
        "orig_elements",
        []
    )

    # ---------------------------------------------
    # Inspect original elements
    # ---------------------------------------------

    for element in original_elements:

        element_type = type(
            element
        ).__name__

        # -----------------------------------------
        # Table
        # -----------------------------------------

        if element_type == "Table":

            table_html = getattr(
                getattr(
                    element,
                    "metadata",
                    None
                ),
                "text_as_html",
                None
            )

            if table_html:

                content_data[
                    "tables"
                ].append(
                    table_html
                )

            else:

                content_data[
                    "tables"
                ].append(
                    str(
                        getattr(
                            element,
                            "text",
                            ""
                        )
                    )
                )

            if "table" not in content_data["types"]:
                content_data[
                    "types"
                ].append("table")

        # -----------------------------------------
        # Image
        # -----------------------------------------

        elif element_type == "Image":

            image_metadata = getattr(
                element,
                "metadata",
                None
            )

            image_base64 = getattr(
                image_metadata,
                "image_base64",
                None
            )

            if image_base64:

                content_data[
                    "images"
                ].append(
                    image_base64
                )

                if "image" not in content_data["types"]:
                    content_data[
                        "types"
                    ].append("image")

    return content_data


# ---------------------------------------------------------
# Create AI summary
# ---------------------------------------------------------

def create_ai_summary(
    text: str,
    tables: List[str],
    images: List[str],
    llm,
):
    """
    Generate searchable AI summary for a chunk.
    """

    prompt = f"""
You are an AI document understanding system.

Create a detailed, searchable description of the
following document content.

TEXT:
{text}

"""

    # ---------------------------------------------
    # Add tables
    # ---------------------------------------------

    if tables:

        prompt += "\nTABLES:\n"

        for i, table in enumerate(
            tables,
            start=1
        ):

            prompt += (
                f"\nTable {i}:\n"
                f"{table}\n"
            )

    # ---------------------------------------------
    # Instructions
    # ---------------------------------------------

    prompt += """

Analyze the provided content and produce a
searchable description.

Include:

1. Main topic
2. Important concepts
3. Important facts
4. Numbers and data
5. Information from tables
6. Information visible in images
7. Relationships between concepts
8. Possible questions this content can answer
9. Useful alternative search terms

Do not invent information that is not present
in the provided content.

Return only the searchable description.
"""

    # ---------------------------------------------
    # Message
    # ---------------------------------------------

    message_content = [
        {
            "type": "text",
            "text": prompt,
        }
    ]

    # ---------------------------------------------
    # Add images
    # ---------------------------------------------

    for image_base64 in images:

        message_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        "data:image/jpeg;base64,"
                        f"{image_base64}"
                    )
                },
            }
        )

    message = HumanMessage(
        content=message_content
    )

    response = llm.invoke(
        [message]
    )

    return response.content


# ---------------------------------------------------------
# Convert chunk to LangChain Document
# ---------------------------------------------------------

def create_langchain_document(
    chunk,
    enhanced_content,
    content_data,
):
    """
    Convert processed chunk into LangChain Document.
    """

    metadata = {
        "content_types": json.dumps(
            content_data["types"]
        ),

        "original_content": json.dumps(
            {
                "raw_text": content_data[
                    "text"
                ],

                "tables_html": content_data[
                    "tables"
                ],

                "images_base64": content_data[
                    "images"
                ],
            }
        ),
    }

    # ---------------------------------------------
    # Preserve useful Unstructured metadata
    # ---------------------------------------------

    chunk_metadata = getattr(
        chunk,
        "metadata",
        None
    )

    if chunk_metadata:

        page_number = getattr(
            chunk_metadata,
            "page_number",
            None
        )

        if page_number is not None:
            metadata[
                "page_number"
            ] = page_number

        filename = getattr(
            chunk_metadata,
            "filename",
            None
        )

        if filename:
            metadata[
                "filename"
            ] = filename

    return Document(
        page_content=enhanced_content,
        metadata=metadata,
    )


# ---------------------------------------------------------
# Summarize all chunks
# ---------------------------------------------------------

def summarize_chunks(
    chunks: List,
    llm=None,
):
    """
    Process all chunks with AI summarization.

    Args:
        chunks:
            Chunks returned by chunker.py.

        llm:
            Optional Hugging Face model.

    Returns:
        List of LangChain Documents.
    """

    if not chunks:
        raise ValueError(
            "No chunks provided."
        )

    print(
        "🧠 Processing chunks with AI summaries..."
    )

    # Load model once
    if llm is None:
        llm = create_summarizer()

    processed_documents = []

    total_chunks = len(chunks)

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n📄 Processing "
            f"{index}/{total_chunks}"
        )

        # -----------------------------------------
        # Separate content
        # -----------------------------------------

        content_data = (
            separate_content_types(
                chunk
            )
        )

        print(
            f"   Types: "
            f"{content_data['types']}"
        )

        print(
            f"   Tables: "
            f"{len(content_data['tables'])}"
        )

        print(
            f"   Images: "
            f"{len(content_data['images'])}"
        )

        # -----------------------------------------
        # Create summary
        # -----------------------------------------

        has_visual_content = (
            content_data["tables"]
            or content_data["images"]
        )

        if has_visual_content:

            print(
                "   🧠 Creating AI summary..."
            )

            try:

                enhanced_content = (
                    create_ai_summary(
                        text=content_data[
                            "text"
                        ],
                        tables=content_data[
                            "tables"
                        ],
                        images=content_data[
                            "images"
                        ],
                        llm=llm,
                    )
                )

                print(
                    "   ✅ AI summary created"
                )

            except Exception as error:

                print(
                    f"   ⚠️ AI summary failed: "
                    f"{error}"
                )

                enhanced_content = (
                    content_data["text"]
                )

        else:

            print(
                "   → No table/image. "
                "Using original text."
            )

            enhanced_content = (
                content_data["text"]
            )

        # -----------------------------------------
        # Create LangChain document
        # -----------------------------------------

        document = (
            create_langchain_document(
                chunk=chunk,
                enhanced_content=(
                    enhanced_content
                ),
                content_data=content_data,
            )
        )

        processed_documents.append(
            document
        )

    print(
        f"\n✅ Processed "
        f"{len(processed_documents)} chunks"
    )

    return processed_documents


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "Summarizer service loaded successfully."
    )

    print(
        f"Model: {HF_MODEL}"
    )