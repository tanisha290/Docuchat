"""
Extracts text from a PDF, keeping a page-number mapping so every
downstream chunk can cite the page it came from.
"""
from pypdf import PdfReader


def extract_pages(file_path):
    """
    Returns a list of dicts: [{"page": 1, "text": "..."}, ...]
    Pages with no extractable text are skipped (e.g. scanned images).
    """
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({"page": i, "text": text})
    return pages, len(reader.pages)


class NoExtractableTextError(Exception):
    """Raised when a PDF has no extractable text at all (e.g. scanned/image-only)."""
    pass


def extract_or_raise(file_path):
    pages, total_pages = extract_pages(file_path)
    if not pages:
        raise NoExtractableTextError(
            "No extractable text found in this PDF. It may be a scanned "
            "image without an OCR text layer."
        )
    return pages, total_pages
