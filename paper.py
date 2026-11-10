"""Extract page-labelled text locally, making omissions explicit."""
import io
from dataclasses import dataclass

from pypdf import PdfReader

MAX_SOURCE_BYTES = 18000


@dataclass
class Paper:
    pages: int
    text: str
    notes: list[str]


def extract_paper(data: bytes) -> Paper:
    if not data.startswith(b"%PDF-"):
        raise ValueError("This file is not a valid PDF.")
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise ValueError("Please upload an unencrypted PDF.")
        if not 1 <= len(reader.pages) <= 100:
            raise ValueError("Please choose a paper with 1–100 pages.")
        pages = [(i, (page.extract_text() or "").strip()) for i, page in enumerate(reader.pages, 1)]
    except ValueError:
        raise
    except Exception:
        raise ValueError("The PDF could not be read. Try exporting it again.") from None
    readable = [(i, text) for i, text in pages if text]
    if not readable:
        raise ValueError("This PDF has no readable text. Scanned PDFs need OCR first; upload a PDF with selectable text.")
    notes = ["Local generation uses extracted PDF text only. Images, figures and layout-dependent equations may be missing or incomplete."]
    if len(readable) != len(pages):
        notes.append("Pages without readable text were skipped: " + ", ".join(str(i) for i, text in pages if not text) + ".")
    full_text = "\n\n".join(f"[PDF page {i}]\n{text}" for i, text in readable)
    if len(full_text.encode("utf-8")) > MAX_SOURCE_BYTES:
        # Sample each readable page instead of silently dropping the end of the paper.
        per_page = MAX_SOURCE_BYTES // len(readable)
        excerpts = []
        for i, text in readable:
            header = f"[PDF page {i}]\n"
            marker = "\n[remaining page text omitted]"
            budget = per_page - len((header + marker + "\n\n").encode("utf-8"))
            encoded = text.encode("utf-8")
            excerpt = encoded[:budget].decode("utf-8", errors="ignore")
            excerpts.append(header + excerpt + (marker if len(encoded) > budget else ""))
        full_text = "\n\n".join(excerpts)
        notes.append("This paper exceeded the local context budget. The tutorial uses excerpts from each readable page; some methods and details are omitted. Upload a shorter PDF excerpt for a more focused tutorial.")
    return Paper(len(pages), full_text, notes)
