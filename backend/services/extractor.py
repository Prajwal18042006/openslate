"""
Document extraction utility.

Supports extracting content from:

Local files:
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
- MD
- RTF

Remote:
- PDF URLs
- Webpage URLs
"""

import sys
import tempfile
from pathlib import Path

import requests

from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from unstructured.partition.html import partition_html
from unstructured.partition.csv import partition_csv
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.pptx import partition_pptx
from unstructured.partition.md import partition_md
from unstructured.partition.rtf import partition_rtf


# =========================================================
# Supported file types
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
# PDF extraction
# =========================================================

def _partition_pdf(file_path: str):
    """
    Extract PDF content including:

    - Text
    - Tables
    - Images
    """

    return partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["image"],
        extract_image_block_to_payload=True,
    )


# =========================================================
# DOC extraction
# =========================================================

def _partition_doc(file_path: str):
    """
    Extract legacy Microsoft Word .doc files.
    """

    return partition_doc(
        filename=file_path
    )


# =========================================================
# DOCX extraction
# =========================================================

def _partition_docx(file_path: str):
    """
    Extract Microsoft Word .docx files.
    """

    return partition_docx(
        filename=file_path
    )


# =========================================================
# TXT extraction
# =========================================================

def _partition_text(file_path: str):
    """
    Extract plain text files.
    """

    return partition_text(
        filename=file_path
    )


# =========================================================
# HTML extraction
# =========================================================

def _partition_html(file_path: str):
    """
    Extract HTML documents.
    """

    return partition_html(
        filename=file_path
    )


# =========================================================
# CSV extraction
# =========================================================

def _partition_csv(file_path: str):
    """
    Extract CSV files.
    """

    return partition_csv(
        filename=file_path
    )


# =========================================================
# XLSX extraction
# =========================================================

def _partition_xlsx(file_path: str):
    """
    Extract Excel .xlsx files.
    """

    return partition_xlsx(
        filename=file_path
    )


# =========================================================
# PPTX extraction
# =========================================================

def _partition_pptx(file_path: str):
    """
    Extract PowerPoint .pptx files.
    """

    return partition_pptx(
        filename=file_path
    )


# =========================================================
# Markdown extraction
# =========================================================

def _partition_markdown(file_path: str):
    """
    Extract Markdown files.
    """

    return partition_md(
        filename=file_path
    )


# =========================================================
# RTF extraction
# =========================================================

def _partition_rtf(file_path: str):
    """
    Extract Rich Text Format files.
    """

    return partition_rtf(
        filename=file_path
    )


# =========================================================
# Webpage extraction
# =========================================================

def _partition_webpage(
    html: str
):
    """
    Extract content from HTML/webpages.
    """

    return partition_html(
        text=html
    )


# =========================================================
# Download URL
# =========================================================

def _download_url(
    url: str
) -> requests.Response:
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
                "Chrome/151.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()

    return response


# =========================================================
# Extract from URL
# =========================================================

def _extract_from_url(
    source: str
):
    """
    Handle extraction from:

    - Remote PDF
    - Remote webpage
    """

    response = _download_url(
        source
    )

    content_type = (
        response.headers
        .get(
            "content-type",
            ""
        )
        .lower()
    )

    # =====================================================
    # Remote PDF
    # =====================================================

    if "application/pdf" in content_type:

        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            ) as temp_file:

                temp_file.write(
                    response.content
                )

                temp_path = (
                    temp_file.name
                )

            elements = _partition_pdf(
                temp_path
            )

        finally:

            if temp_path:

                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )

        print(
            f"✅ Extracted {len(elements)} "
            f"elements from PDF URL"
        )

        return elements

    # =====================================================
    # Remote webpage
    # =====================================================

    if (
        "text/html" in content_type
        or
        "application/xhtml+xml"
        in content_type
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
        f"{content_type}"
    )


# =========================================================
# Extract from local file
# =========================================================

def _extract_from_file(
    source: str
):
    """
    Extract content from a local file.
    """

    path = Path(
        source
    )

    # =====================================================
    # File exists?
    # =====================================================

    if not path.exists():

        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    # =====================================================
    # Is it a file?
    # =====================================================

    if not path.is_file():

        raise ValueError(
            f"Source is not a file: {path}"
        )

    # =====================================================
    # Get extension
    # =====================================================

    extension = (
        path.suffix.lower()
    )

    # =====================================================
    # Validate extension
    # =====================================================

    if (
        extension
        not in SUPPORTED_EXTENSIONS
    ):

        raise ValueError(
            f"Unsupported file type: "
            f"{extension}. "
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

        # Unstructured does not always provide
        # direct XLS partitioning.
        #
        # Try converting through LibreOffice
        # if available.

        raise ValueError(
            "Legacy .xls files are not directly "
            "supported. Please convert .xls to "
            ".xlsx and upload again."
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
            "Legacy .ppt files are not directly "
            "supported. Please convert .ppt to "
            ".pptx and upload again."
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
            f"Unsupported extension: "
            f"{extension}"
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
# Main extraction function
# =========================================================

def extract_document(
    source: str
):
    """
    Main document extraction function.

    Supports:

    Local:
        PDF
        DOC
        DOCX
        TXT
        HTML
        CSV
        XLSX
        PPTX
        MD
        RTF

    Remote:
        PDF URL
        Website URL
    """

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
    # Local file
    # =====================================================

    return _extract_from_file(
        source
    )


# =========================================================
# Command-line testing
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