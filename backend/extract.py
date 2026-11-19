"""Extraction de texte depuis n'importe quel fichier uploadé."""
import io
import json
import re

TEXT_EXT = {"txt", "md", "csv", "tsv", "log", "py", "js", "ts", "java", "c", "cpp", "rst", "tex", "xml", "yaml", "yml"}


def _decode(data: bytes) -> str:
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _pdf(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def _docx(data: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)


def _pptx(data: bytes) -> str:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(data))
    parts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                parts.append(shape.text_frame.text)
    return "\n".join(parts)


def _html(data: bytes) -> str:
    text = _decode(data)
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    return re.sub(r"<[^>]+>", " ", text)


def _json(data: bytes) -> str:
    def walk(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, dict):
            for v in o.values():
                yield from walk(v)
        elif isinstance(o, list):
            for v in o:
                yield from walk(v)
    return "\n".join(walk(json.loads(_decode(data))))


HANDLERS = {"pdf": _pdf, "docx": _docx, "pptx": _pptx, "html": _html, "htm": _html, "json": _json}


def extract_text(filename: str, data: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    handler = HANDLERS.get(ext)
    text = handler(data) if handler else _decode(data)  # txt, md, csv... ou inconnu
    return re.sub(r"\s+", " ", text).strip()
