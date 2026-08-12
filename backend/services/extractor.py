"""
OpenSlate Mini - Document Extraction Utility

Supported local files:
- PDF
- DOC
- DOCX
- TXT
- HTML
- HTM
- CSV
- XLS
- XLSX
- PPT
- PPTX
- Markdown
- RTF

Supported remote sources:
- PDF URLs
- Webpage URLs

Important:
All Unstructured imports are lazy-loaded inside functions.
This prevents heavy document-processing libraries from
blocking FastAPI startup on Render.
"""

import sys
import tempfile
from pathlib import Path

import requests


# =========================================================
# Supported File Types
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".html",
    ".htm",
    ".csv",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".md",
    ".rtf",
}


# =========================================================
# PDF Extraction
# =========================================================

def _partition_pdf(file_path: str):
    """
    Extract PDF content.

    Includes:
    - Text
    - Tables
    - Images

    Unstructured PDF dependencies are imported only when
    a PDF is actually processed.
    """

    from unstructured.partition.pdf import partition_pdf

    return partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["image"],
        extract_image_block_to_payload=True,
    )


# =========================================================
# DOC Extraction
# =========================================================

def _partition_doc(file_path: str):
    """
    Extract legacy Microsoft Word .doc files.
    """

    from unstructured.partition.doc import partition_doc

    return partition_doc(
        filename=file_path
    )


# =========================================================
# DOCX Extraction
# =========================================================

def _partition_docx(file_path: str):
    """
    Extract Microsoft Word .docx files.
    """

    from unstructured.partition.docx import partition_docx

    return partition_docx(
        filename=file_path
    )


# =========================================================
# TXT Extraction
# =========================================================

def _partition_text(file_path: str):
    """
    Extract plain text files.
    """

    from unstructured.partition.text import partition_text

    return partition_text(
        filename=file_path
    )


# =========================================================
# HTML Extraction
# =========================================================

def _partition_html(file_path: str):
    """
    Extract HTML documents.
    """

    from unstructured.partition.html import partition_html

    return partition_html(
        filename=file_path
    )


# =========================================================
# CSV Extraction
# =========================================================

def _partition_csv(file_path: str):
    """
    Extract CSV files.
    """

    from unstructured.partition.csv import partition_csv

    return partition_csv(
        filename=file_path
    )


# =========================================================
# XLSX Extraction
# =========================================================

def _partition_xlsx(file_path: str):
    """
    Extract Excel .xlsx files.
    """

    from unstructured.partition.xlsx import partition_xlsx

    return partition_xlsx(
        filename=file_path
    )


# =========================================================
# PPTX Extraction
# =========================================================

def _partition_pptx(file_path: str):
    """
    Extract PowerPoint .pptx files.
    """

    from unstructured.partition.pptx import partition_pptx

    return partition_pptx(
        filename=file_path
    )


# =========================================================
# Markdown Extraction
# =========================================================

def _partition_markdown(file_path: str):
    """
    Extract Markdown files.
    """

    from unstructured.partition.md import partition_md

    return partition_md(
        filename=file_path
    )


# =========================================================
# RTF Extraction
# =========================================================

def _partition_rtf(file_path: str):
    """
    Extract Rich Text Format files.
    """

    from unstructured.partition.rtf import partition_rtf

    return partition_rtf(
        filename=file_path
    )


# =========================================================
# Webpage Extraction
# =========================================================

def _partition_webpage(html: str):
    """
    Extract content from an HTML webpage.
    """

    from unstructured.partition.html import partition_html

    return partition_html(
        text=html
    )


# =========================================================
# Download URL
# =========================================================

def _download_url(url: str) -> requests.Response:
    """
    Download content from a URL.
    """

    response = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()

    return response


# =========================================================
# Extract From URL
# =========================================================

def _extract_from_url(source: str):
    """
    Handle extraction from:

    - Remote PDF
    - Remote webpage
    """

    response = _download_url(source)

    content_type = (
        response.headers
        .get("content-type", "")
        .lower()
    )

    # Remove content-type parameters
    # Example:
    # application/pdf; charset=binary
    content_type = content_type.split(";")[0].strip()

    # =====================================================
    # Remote PDF
    # =====================================================

    if (
        content_type == "application/pdf"
        or source.lower().split("?")[0].endswith(".pdf")
    ):

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            ) as temp_file:

                temp_file.write(
                    response.content
                )

                temp_path = temp_file.name

            elements = _partition_pdf(
                temp_path
            )

        finally:

            if temp_path:

                Path(temp_path).unlink(
                    missing_ok=True
                )

        print(
            f"✅ Extracted {len(elements)} "
            f"elements from PDF URL"
        )

        return elements

    # =====================================================
    # Remote Webpage
    # =====================================================

    if (
        content_type == "text/html"
        or content_type == "application/xhtml+xml"
        or source.lower().split("?")[0].endswith(
            (".html", ".htm")
        )
    ):

        elements = _partition_webpage(
            response.text
        )

        print(
            f"✅ Extracted {len(elements)} "
            f"elements from webpage"
        )

        return elements

    # =====================================================
    # Unsupported URL
    # =====================================================

    raise ValueError(
        "Unsupported URL content type: "
        f"{content_type}. "
        "Only PDF URLs and webpage URLs are supported."
    )


# =========================================================
# Extract From Local File
# =========================================================

def _extract_from_file(source: str):
    """
    Extract content from a local file.
    """

    path = Path(source)

    # =====================================================
    # File Exists
    # =====================================================

    if not path.exists():

        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    # =====================================================
    # Is File
    # =====================================================

    if not path.is_file():

        raise ValueError(
            f"Source is not a file: {path}"
        )

    # =====================================================
    # Get Extension
    # =====================================================

    extension = path.suffix.lower()

    # =====================================================
    # Validate Extension
    # =====================================================

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    print(
        f"📄 Local file detected: {path}"
    )

    print(
        f"📌 File type: {extension}"
    )

    # =====================================================
    # PDF
    # =====================================================

    if extension == ".pdf":

        elements = _partition_pdf(
            str(path)
        )

    # =====================================================
    # DOC
    # =====================================================

    elif extension == ".doc":

        elements = _partition_doc(
            str(path)
        )

    # =====================================================
    # DOCX
    # =====================================================

    elif extension == ".docx":

        elements = _partition_docx(
            str(path)
        )

    # =====================================================
    # TXT
    # =====================================================

    elif extension == ".txt":

        elements = _partition_text(
            str(path)
        )

    # =====================================================
    # HTML
    # =====================================================

    elif extension in (
        ".html",
        ".htm",
    ):

        elements = _partition_html(
            str(path)
        )

    # =====================================================
    # CSV
    # =====================================================

    elif extension == ".csv":

        elements = _partition_csv(
            str(path)
        )

    # =====================================================
    # XLSX
    # =====================================================

    elif extension == ".xlsx":

        elements = _partition_xlsx(
            str(path)
        )

    # =====================================================
    # XLS
    # =====================================================

    elif extension == ".xls":

        raise ValueError(
            "Legacy .xls files are not directly supported "
            "by this deployment. "
            "Please convert .xls to .xlsx and upload again."
        )

    # =====================================================
    # PPTX
    # =====================================================

    elif extension == ".pptx":

        elements = _partition_pptx(
            str(path)
        )

    # =====================================================
    # PPT
    # =====================================================

    elif extension == ".ppt":

        raise ValueError(
            "Legacy .ppt files are not directly supported "
            "by this deployment. "
            "Please convert .ppt to .pptx and upload again."
        )

    # =====================================================
    # Markdown
    # =====================================================

    elif extension == ".md":

        elements = _partition_markdown(
            str(path)
        )

    # =====================================================
    # RTF
    # =====================================================

    elif extension == ".rtf":

        elements = _partition_rtf(
            str(path)
        )

    # =====================================================
    # Safety
    # =====================================================

    else:

        raise ValueError(
            f"Unsupported extension: {extension}"
        )

    # =====================================================
    # Result
    # =====================================================

    print(
        f"✅ Successfully extracted "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# Main Extraction Function
# =========================================================

def extract_document(source: str):
    """
    Main document extraction function.

    Supports local:

    - PDF
    - DOC
    - DOCX
    - TXT
    - HTML
    - HTM
    - CSV
    - XLSX
    - PPTX
    - MD
    - RTF

    Supports remote:

    - PDF URL
    - Website URL
    """

    # =====================================================
    # Validate Source
    # =====================================================

    if not source or not source.strip():

        raise ValueError(
            "Document source cannot be empty."
        )

    source = source.strip()

    print(
        f"🔍 Extracting source: {source}"
    )

    # =====================================================
    # URL
    # =====================================================

    if source.startswith(
        (
            "http://",
            "https://",
        )
    ):

        return _extract_from_url(
            source
        )

    # =====================================================
    # Local File
    # =====================================================

    return _extract_from_file(
        source
    )


# =========================================================
# Command Line Testing
# =========================================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python extractor.py "
            "<file_path_or_url>"
        )

        sys.exit(1)

    source = sys.argv[1]

    try:

        elements = extract_document(
            source
        )

        print(
            f"\n🎉 Total elements: "
            f"{len(elements)}"
        )

        print(
            "\nFirst 5 elements:"
        )

        print(
            "=" * 60
        )

        for i, element in enumerate(
            elements[:5],
            start=1,
        ):

            print(
                f"\nElement {i}"
            )

            print(
                f"Type: "
                f"{type(element).__name__}"
            )

            print(
                f"Text: "
                f"{str(element)[:500]}"
            )

    except Exception as e:

        print(
            f"\n❌ Extraction failed: {e}"
        )

        sys.exit(1)