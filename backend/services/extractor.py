"""
OpenSlate Mini - Fast Document Extraction Utility

Supports:
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

Also supports:
- PDF URLs
- Webpage URLs

PDF extraction:
- Primary: PyMuPDF
- Fallback: Unstructured
"""

import sys
import tempfile
import time
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

def _partition_pdf_with_pymupdf(file_path: str):
    """
    Fast text extraction from normal/text-based PDFs.

    Uses PyMuPDF instead of Unstructured for faster
    CPU-based extraction.

    Returns Unstructured Text elements so the existing
    chunker.py remains compatible.
    """

    print("\n" + "=" * 60)
    print("⚡ FAST PDF EXTRACTION - PyMuPDF")
    print("=" * 60)

    start_time = time.time()

    import pymupdf

    from unstructured.documents.elements import Text

    document = pymupdf.open(file_path)

    elements = []

    try:

        print(
            f"📄 PDF pages: {len(document)}"
        )

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            text = page.get_text("text")

            text = text.strip()

            if not text:
                continue

            element = Text(
                text=text,
            )

            # Add page metadata when possible
            try:
                element.metadata.page_number = (
                    page_number
                )
            except Exception:
                pass

            elements.append(element)

    finally:

        document.close()

    elapsed = time.time() - start_time

    print(
        f"📊 Extracted elements: "
        f"{len(elements)}"
    )

    print(
        f"⏱️ PyMuPDF extraction time: "
        f"{elapsed:.2f} seconds"
    )

    return elements

def _partition_pdf_with_unstructured(file_path: str):
    """
    Fallback PDF extraction using Unstructured.

    Used when PyMuPDF cannot extract useful text.
    """

    print("\n" + "=" * 60)
    print("🔄 FALLBACK PDF EXTRACTION - Unstructured")
    print("=" * 60)

    print(
        f"📁 File: {file_path}"
    )

    print(
        "⏳ Starting Unstructured PDF extraction..."
    )

    print(
        "🖥️ Device: CPU"
    )

    start_time = time.time()

    try:

        from unstructured.partition.pdf import (
            partition_pdf
        )

        print(
            "📦 Unstructured PDF parser imported"
        )

        print(
            "🚀 Calling partition_pdf()..."
        )

        elements = partition_pdf(
            filename=file_path,
            strategy="fast",
        )

        elapsed = (
            time.time() - start_time
        )

        print(
            f"✅ Unstructured extraction completed "
            f"in {elapsed:.2f} seconds"
        )

        print(
            f"📊 Extracted elements: "
            f"{len(elements)}"
        )

        return elements

    except Exception as e:

        elapsed = (
            time.time() - start_time
        )

        print("\n" + "=" * 60)
        print("❌ UNSTRUCTURED EXTRACTION FAILED")
        print("=" * 60)

        print(
            f"⏱️ Failed after: "
            f"{elapsed:.2f} seconds"
        )

        print(
            f"❌ Error type: "
            f"{type(e).__name__}"
        )

        print(
            f"❌ Error message: "
            f"{str(e)}"
        )

        print(
            f"❌ Full exception: "
            f"{repr(e)}"
        )

        import traceback

        print(
            "\n🔍 Full traceback:"
        )

        traceback.print_exc()

        print("=" * 60)

        raise


# =========================================================
# DOC Extraction
# =========================================================

def _partition_doc(file_path: str):

    print("📄 Extracting DOC file...")

    from unstructured.partition.doc import (
        partition_doc
    )

    elements = partition_doc(
        filename=file_path
    )

    print(
        f"✅ DOC extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# DOCX Extraction
# =========================================================

def _partition_docx(file_path: str):

    print("📄 Extracting DOCX file...")

    from unstructured.partition.docx import (
        partition_docx
    )

    elements = partition_docx(
        filename=file_path
    )

    print(
        f"✅ DOCX extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# TXT Extraction
# =========================================================

def _partition_text(file_path: str):

    print("📄 Extracting TXT file...")

    from unstructured.partition.text import (
        partition_text
    )

    elements = partition_text(
        filename=file_path
    )

    print(
        f"✅ TXT extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# HTML Extraction
# =========================================================

def _partition_html(file_path: str):

    print("🌐 Extracting HTML file...")

    from unstructured.partition.html import (
        partition_html
    )

    elements = partition_html(
        filename=file_path
    )

    print(
        f"✅ HTML extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# CSV Extraction
# =========================================================

def _partition_csv(file_path: str):

    print("📊 Extracting CSV file...")

    from unstructured.partition.csv import (
        partition_csv
    )

    elements = partition_csv(
        filename=file_path
    )

    print(
        f"✅ CSV extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# XLSX Extraction
# =========================================================

def _partition_xlsx(file_path: str):

    print("📊 Extracting XLSX file...")

    from unstructured.partition.xlsx import (
        partition_xlsx
    )

    elements = partition_xlsx(
        filename=file_path
    )

    print(
        f"✅ XLSX extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# PPTX Extraction
# =========================================================

def _partition_pptx(file_path: str):

    print("📊 Extracting PPTX file...")

    from unstructured.partition.pptx import (
        partition_pptx
    )

    elements = partition_pptx(
        filename=file_path
    )

    print(
        f"✅ PPTX extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# Markdown Extraction
# =========================================================

def _partition_markdown(file_path: str):

    print("📝 Extracting Markdown file...")

    from unstructured.partition.md import (
        partition_md
    )

    elements = partition_md(
        filename=file_path
    )

    print(
        f"✅ Markdown extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# RTF Extraction
# =========================================================

def _partition_rtf(file_path: str):

    print("📝 Extracting RTF file...")

    from unstructured.partition.rtf import (
        partition_rtf
    )

    elements = partition_rtf(
        filename=file_path
    )

    print(
        f"✅ RTF extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# Webpage Extraction
# =========================================================

def _partition_webpage(html: str):

    print("🌐 Extracting webpage...")

    from unstructured.partition.html import (
        partition_html
    )

    elements = partition_html(
        text=html
    )

    print(
        f"✅ Webpage extraction completed: "
        f"{len(elements)} elements"
    )

    return elements


# =========================================================
# Download URL
# =========================================================

def _download_url(url: str) -> requests.Response:

    print(
        f"🌐 Downloading URL: {url}"
    )

    start_time = time.time()

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

    elapsed = (
        time.time()
        - start_time
    )

    print(
        f"✅ Download completed in "
        f"{elapsed:.2f} seconds"
    )

    print(
        f"📦 Downloaded size: "
        f"{len(response.content)} bytes"
    )

    return response


# =========================================================
# Extract From URL
# =========================================================

def _extract_from_url(source: str):

    print("\n" + "=" * 60)
    print("🌐 REMOTE EXTRACTION")
    print("=" * 60)

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
        .split(";")[0]
        .strip()
    )

    print(
        f"📌 Content-Type: "
        f"{content_type}"
    )

    # =====================================================
    # Remote PDF
    # =====================================================

    if (
        content_type == "application/pdf"
        or source.lower()
        .split("?")[0]
        .endswith(".pdf")
    ):

        print(
            "📄 Remote PDF detected"
        )

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

            print(
                f"📁 Temporary PDF: "
                f"{temp_path}"
            )

            elements = _partition_pdf(
                temp_path
            )

        finally:

            if temp_path:

                Path(temp_path).unlink(
                    missing_ok=True
                )

                print(
                    "🗑️ Temporary PDF removed"
                )

        print(
            f"✅ Extracted "
            f"{len(elements)} elements "
            f"from PDF URL"
        )

        return elements

    # =====================================================
    # Remote Webpage
    # =====================================================

    if (
        content_type == "text/html"
        or content_type
        == "application/xhtml+xml"
        or source.lower()
        .split("?")[0]
        .endswith(
            (".html", ".htm")
        )
    ):

        print(
            "🌐 Webpage detected"
        )

        elements = _partition_webpage(
            response.text
        )

        print(
            f"✅ Extracted "
            f"{len(elements)} elements "
            f"from webpage"
        )

        return elements

    # =====================================================
    # Unsupported URL
    # =====================================================

    raise ValueError(
        "Unsupported URL content type: "
        f"{content_type}. "
        "Only PDF URLs and webpage URLs "
        "are supported."
    )


# =========================================================
# Extract From Local File
# =========================================================

def _extract_from_file(source: str):

    print("\n" + "=" * 60)
    print("📁 LOCAL FILE EXTRACTION")
    print("=" * 60)

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

    extension = (
        path.suffix.lower()
    )

    print(
        f"📄 File: {path.name}"
    )

    print(
        f"📌 File type: {extension}"
    )

    # =====================================================
    # Validate Extension
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

    start_time = time.time()

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
            "Legacy .xls files are not "
            "directly supported. "
            "Please convert .xls to .xlsx "
            "and upload again."
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
            "Legacy .ppt files are not "
            "directly supported. "
            "Please convert .ppt to .pptx "
            "and upload again."
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

    else:

        raise ValueError(
            f"Unsupported extension: "
            f"{extension}"
        )

    # =====================================================
    # Result
    # =====================================================

    elapsed = (
        time.time()
        - start_time
    )

    print(
        f"✅ Successfully extracted "
        f"{len(elements)} elements"
    )

    print(
        f"⏱️ Extraction time: "
        f"{elapsed:.2f} seconds"
    )

    print("=" * 60)
    print("🎉 EXTRACTION FINISHED")
    print("=" * 60)

    return elements


# =========================================================
# Main Extraction Function
# =========================================================

def extract_document(source: str):
    """
    Main document extraction function.

    Supports local files and URLs.
    """

    if (
        not source
        or not source.strip()
    ):

        raise ValueError(
            "Document source cannot be empty."
        )

    source = source.strip()

    print("\n" + "=" * 60)
    print("🚀 DOCUMENT EXTRACTION REQUEST")
    print("=" * 60)

    print(
        f"🔍 Source: {source}"
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

        print("=" * 60)

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
            f"\n❌ Extraction failed: "
            f"{e}"
        )

        sys.exit(1)