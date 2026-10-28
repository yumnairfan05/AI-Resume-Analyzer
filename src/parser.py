"""Turn an uploaded CV (PDF / DOCX / TXT) into clean plain text."""
import io
import re

import docx
from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(uploaded_file) -> str:
    """Accepts a Streamlit UploadedFile (anything with .name and .read())."""
    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    elif name.endswith(".docx"):
        document = docx.Document(io.BytesIO(data))
        text = "\n".join(p.text for p in document.paragraphs)
    elif name.endswith(".txt"):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF, DOCX or TXT file.")

    text = clean_text(text)
    if len(text) < 80:
        raise ValueError(
            "Could not read enough text from this file. "
            "If it is a scanned image PDF, export a text-based PDF and try again."
        )
    return text
