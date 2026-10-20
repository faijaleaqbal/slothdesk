"""
Universal text & content extractor for SlothDesk.
Extracts clean plain text from files of any common format.
"""

import os
import re
import csv
import json
from pathlib import Path
from typing import Dict, Any, Tuple

def extract_content(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text content and metadata from a file.
    Returns (cleaned_text, metadata_dict).
    """
    if not file_path.exists():
        return "", {"error": "File does not exist"}

    ext = file_path.suffix.lower()
    stat = file_path.stat()
    meta: Dict[str, Any] = {
        "filename": file_path.name,
        "extension": ext,
        "size_bytes": stat.st_size,
        "modified_time": stat.st_mtime
    }

    # Text / Code / Markdown
    text_extensions = {
        ".txt", ".md", ".markdown", ".rst", ".log",
        ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css",
        ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
        ".sh", ".bash", ".ps1", ".cmd", ".bat", ".sql", ".env"
    }

    if ext in text_extensions:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(50000)  # Read up to 50KB for fast analysis
            return content.strip(), meta
        except Exception as e:
            return f"[Error reading text file: {e}]", meta

    # CSV / TSV
    if ext in {".csv", ".tsv"}:
        try:
            delimiter = "\t" if ext == ".tsv" else ","
            lines = []
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f, delimiter=delimiter)
                for i, row in enumerate(reader):
                    if i > 50:  # first 50 rows
                        lines.append(f"... and {stat.st_size} total bytes")
                        break
                    lines.append(", ".join(row))
            return "\n".join(lines), meta
        except Exception as e:
            return f"[Error parsing table: {e}]", meta

    # PDF basic text extractor (reads standard streams if pypdf is not installed)
    if ext == ".pdf":
        try:
            # Try importing pypdf / PyPDF2 if available
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                text_parts = []
                for page in reader.pages[:10]:
                    text_parts.append(page.extract_text() or "")
                extracted = "\n".join(text_parts).strip()
                if extracted:
                    return extracted, meta
            except ImportError:
                pass

            # Fallback lightweight PDF text stream regex extractor
            with open(file_path, "rb") as f:
                raw_bytes = f.read(100000)
            text_chunks = re.findall(rb"\((.*?)\)Tj", raw_bytes)
            if not text_chunks:
                text_chunks = re.findall(rb"\[(.*?)\]TJ", raw_bytes)
            decoded = " ".join([c.decode("latin1", errors="ignore") for c in text_chunks[:300]])
            if len(decoded.strip()) > 30:
                return decoded.strip(), meta
            return f"[PDF Document: {file_path.name}, Size: {stat.st_size} bytes]", meta
        except Exception as e:
            return f"[PDF File: {file_path.name}, parsing note: {e}]", meta

    # Images
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}:
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                meta["dimensions"] = f"{img.width}x{img.height}"
                meta["format"] = img.format
                return f"[Image File: {file_path.name}, Format: {img.format}, Resolution: {img.width}x{img.height}]", meta
        except Exception:
            return f"[Image Media File: {file_path.name}, Size: {stat.st_size} bytes]", meta

    # Audio
    if ext in {".mp3", ".wav", ".m4a", ".ogg", ".flac"}:
        return f"[Audio Recording: {file_path.name}, Size: {stat.st_size} bytes]", meta

    # Default fallback
    return f"[Binary / Data File: {file_path.name}, Extension: {ext}, Size: {stat.st_size} bytes]", meta
