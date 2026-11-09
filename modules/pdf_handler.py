"""PDF loading, preview rasterization, and atomic single-page exports."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import fitz


def open_document(path: str):
    document = fitz.open(path)
    if document.page_count == 0 or document.needs_pass:
        document.close()
        raise ValueError("The PDF is empty or password protected.")
    return document


def render_page(document, page_index: int, zoom: float):
    page = document.load_page(page_index)
    return page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)


def export_page(document, page_index: int, target: Path):
    """Write one page via a temporary file, then atomically move into place."""
    single = fitz.open()
    try:
        single.insert_pdf(document, from_page=page_index, to_page=page_index)
        fd, temp_path = tempfile.mkstemp(prefix=".pdf_organizer_", suffix=".pdf", dir=target.parent)
        os.close(fd)
        try:
            single.save(temp_path, garbage=3, deflate=True)
            os.replace(temp_path, target)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    finally:
        single.close()
