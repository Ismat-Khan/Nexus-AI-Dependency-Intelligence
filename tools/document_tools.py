"""
NEXUS Document Intelligence Tools
Extracts text and structured sections from PDF, DOCX, TXT, MD, and CSV files.
Resilient against format variations, corrupted files, and missing dependencies.
"""

import os
import io
import re
import csv
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional


def extract_text_from_pdf(file_bytes_or_path) -> Dict[str, Any]:
    """Extract text from PDF using pypdf or fallback."""
    text_content = []
    metadata = {"page_count": 0, "status": "success"}
    
    try:
        import pypdf
        reader = None
        if isinstance(file_bytes_or_path, (str, bytes, io.BytesIO)):
            if isinstance(file_bytes_or_path, str):
                with open(file_bytes_or_path, "rb") as f:
                    stream = io.BytesIO(f.read())
            elif isinstance(file_bytes_or_path, bytes):
                stream = io.BytesIO(file_bytes_or_path)
            else:
                stream = file_bytes_or_path
            
            reader = pypdf.PdfReader(stream)
            metadata["page_count"] = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_content.append({"page": idx + 1, "text": page_text})
                
        return {
            "success": True,
            "pages": text_content,
            "full_text": "\n\n".join([p["text"] for p in text_content]),
            "metadata": metadata
        }
    except Exception as e:
        # Fallback pure-python basic stream extraction if pypdf is not installed
        try:
            raw_data = b""
            if isinstance(file_bytes_or_path, str) and os.path.exists(file_bytes_or_path):
                with open(file_bytes_or_path, "rb") as f:
                    raw_data = f.read()
            elif isinstance(file_bytes_or_path, bytes):
                raw_data = file_bytes_or_path
            elif hasattr(file_bytes_or_path, "read"):
                raw_data = file_bytes_or_path.read()
            
            # Simple text extraction from uncompressed PDF streams
            strings = re.findall(b"[(](.*?)[)]", raw_data)
            extracted = " ".join([s.decode("latin1", errors="ignore") for s in strings if len(s) > 2])
            if extracted.strip():
                return {
                    "success": True,
                    "pages": [{"page": 1, "text": extracted}],
                    "full_text": extracted,
                    "metadata": {"page_count": 1, "method": "fallback_stream"}
                }
        except Exception:
            pass
        return {
            "success": False,
            "error": f"Failed to extract PDF: {str(e)}",
            "full_text": "",
            "pages": []
        }


def extract_text_from_docx(file_bytes_or_path) -> Dict[str, Any]:
    """Extract text from DOCX using python-docx or native ZIP XML parser."""
    try:
        import docx
        doc_stream = None
        if isinstance(file_bytes_or_path, str):
            doc = docx.Document(file_bytes_or_path)
        else:
            if isinstance(file_bytes_or_path, bytes):
                stream = io.BytesIO(file_bytes_or_path)
            else:
                stream = file_bytes_or_path
            doc = docx.Document(stream)
            
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        tables_text = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_text:
                    tables_text.append(row_text)
                    
        full_text = "\n".join(paragraphs + tables_text)
        return {
            "success": True,
            "full_text": full_text,
            "paragraphs": paragraphs,
            "tables": tables_text
        }
    except Exception as e:
        # Fallback using zipfile and xml parsing directly (zero-dependency docx)
        try:
            if isinstance(file_bytes_or_path, str):
                z = zipfile.ZipFile(file_bytes_or_path)
            elif isinstance(file_bytes_or_path, bytes):
                z = zipfile.ZipFile(io.BytesIO(file_bytes_or_path))
            else:
                z = zipfile.ZipFile(file_bytes_or_path)
                
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            
            # Extract all text elements
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = []
            for p in tree.iterfind('.//w:p', ns):
                texts = [node.text for node in p.iterfind('.//w:t', ns) if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            full_text = "\n".join(paragraphs)
            return {
                "success": True,
                "full_text": full_text,
                "paragraphs": paragraphs,
                "tables": []
            }
        except Exception as inner_e:
            return {
                "success": False,
                "error": f"Failed to extract DOCX: {str(e)} / {str(inner_e)}",
                "full_text": "",
                "paragraphs": []
            }


def extract_text_from_txt(file_bytes_or_path) -> Dict[str, Any]:
    """Extract plain text from TXT or MD files."""
    try:
        content = ""
        if isinstance(file_bytes_or_path, str):
            with open(file_bytes_or_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        elif isinstance(file_bytes_or_path, bytes):
            content = file_bytes_or_path.decode("utf-8", errors="ignore")
        elif hasattr(file_bytes_or_path, "read"):
            data = file_bytes_or_path.read()
            if isinstance(data, bytes):
                content = data.decode("utf-8", errors="ignore")
            else:
                content = str(data)
                
        return {
            "success": True,
            "full_text": content,
            "lines": content.splitlines()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract text: {str(e)}",
            "full_text": ""
        }


def parse_document(file_name: str, file_bytes_or_path) -> Dict[str, Any]:
    """Dispatches document extraction based on extension."""
    ext = os.path.splitext(file_name)[1].lower()
    
    if ext == ".pdf":
        res = extract_text_from_pdf(file_bytes_or_path)
    elif ext in [".docx", ".doc"]:
        res = extract_text_from_docx(file_bytes_or_path)
    elif ext in [".txt", ".md", ".log"]:
        res = extract_text_from_txt(file_bytes_or_path)
    elif ext in [".csv"]:
        res = extract_text_from_txt(file_bytes_or_path)
    else:
        # Default try plain text
        res = extract_text_from_txt(file_bytes_or_path)
        
    res["file_name"] = file_name
    res["file_type"] = ext
    return res
