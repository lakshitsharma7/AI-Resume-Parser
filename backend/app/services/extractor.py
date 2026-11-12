import os
import shutil
import logging
from typing import Tuple, List, Optional
from pathlib import Path
from PIL import Image

import pdfplumber
import pypdf
import docx
import pytesseract

from app.config import settings

logger = logging.getLogger(__name__)

# Configure Tesseract path if available
if settings.TESSERACT_CMD and os.path.exists(settings.TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
else:
    # Check default Windows installation paths
    default_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Dell\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    ]
    for p in default_paths:
        if os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            break

def is_tesseract_available() -> bool:
    """Checks if Tesseract binary is executable on the system."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False

class DocumentExtractor:
    """
    Extracts text from PDF, DOCX, and image formats.
    Features:
    - 2-column layout awareness to prevent interleaved lines.
    - Table structure preservation.
    - Automatic OCR fallback for scanned resumes.
    """

    @classmethod
    def extract_text(cls, file_path: str) -> Tuple[str, str]:
        """
        Extracts raw normalized text from the given file.
        Returns: (extracted_text, method_used)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if os.path.getsize(file_path) == 0:
            raise ValueError("The uploaded file is empty (0 bytes).")

        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return cls._extract_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return cls._extract_docx(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return cls._extract_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @classmethod
    def _extract_pdf(cls, file_path: str) -> Tuple[str, str]:
        """
        Extracts text from PDF with column-detection and OCR fallback for scanned pages.
        """
        # 1. Check for encryption or password protection
        try:
            reader = pypdf.PdfReader(file_path)
            if reader.is_encrypted:
                raise ValueError("The PDF file is encrypted or password-protected and cannot be parsed.")
        except ValueError:
            raise
        except Exception as e:
            # Corrupted PDF stream check
            if "empty" in str(e).lower() or "eof" in str(e).lower():
                raise ValueError(f"The PDF file is corrupted or incomplete: {e}")

        extracted_pages: List[str] = []
        is_scanned = False
        method = "pdfplumber"

        try:
            with pdfplumber.open(file_path) as pdf:
                total_text_length = 0
                for page_idx, page in enumerate(pdf.pages):
                    page_text = cls._extract_page_with_columns(page)
                    if not page_text or len(page_text.strip()) < 40:
                        # Attempt table extraction on this page
                        tables = page.extract_tables()
                        table_text = ""
                        for table in tables:
                            for row in table:
                                filtered_cells = [str(c).strip() for c in row if c]
                                if filtered_cells:
                                    table_text += " | ".join(filtered_cells) + "\n"
                        if table_text:
                            page_text = (page_text or "") + "\n" + table_text

                    total_text_length += len(page_text.strip()) if page_text else 0
                    extracted_pages.append(page_text or "")

                # If the entire PDF has less than 80 characters, it is likely scanned
                if total_text_length < 80 and len(pdf.pages) > 0:
                    is_scanned = True

        except Exception as e:
            logger.warning(f"pdfplumber extraction failed for {file_path}: {e}. Falling back to pypdf.")
            try:
                reader = pypdf.PdfReader(file_path)
                pypdf_text = []
                for p in reader.pages:
                    pypdf_text.append(p.extract_text() or "")
                combined = "\n\n".join(pypdf_text)
                if len(combined.strip()) < 80:
                    is_scanned = True
                else:
                    return combined, "pypdf"
            except Exception as e2:
                logger.error(f"pypdf extraction failed: {e2}")
                is_scanned = True

        if is_scanned:
            if is_tesseract_available():
                logger.info(f"Triggering Tesseract OCR for scanned PDF: {file_path}")
                ocr_text = cls._extract_pdf_ocr(file_path)
                if ocr_text.strip():
                    return ocr_text, "tesseract_ocr"
            else:
                logger.warning("PDF appears to be scanned, but Tesseract OCR is not installed.")
                fallback = "\n\n".join(extracted_pages).strip()
                return fallback, "pdfplumber_scanned_unparsed"

        return "\n\n".join(extracted_pages).strip(), method

    @classmethod
    def _extract_page_with_columns(cls, page: pdfplumber.page.Page) -> str:
        """
        Analyzes word positions to detect if the page has a 2-column layout.
        If a two-column gutter exists, extracts left column then right column.
        """
        try:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                return page.extract_text() or ""

            page_width = page.width
            # Divide into horizontal buckets to test for a central vertical gutter
            mid_start = page_width * 0.28
            mid_end = page_width * 0.45
            
            # Count words crossing or centered around the gutter
            left_words = [w for w in words if w['x1'] <= mid_start]
            right_words = [w for w in words if w['x0'] >= mid_start]
            cross_words = [w for w in words if w['x0'] < mid_start and w['x1'] > mid_start]

            # If clear separation and low cross-over, treat as two columns
            if len(left_words) > 15 and len(right_words) > 15 and len(cross_words) < 5:
                # Sort left column top-to-bottom
                left_words.sort(key=lambda w: (round(w['top'] / 5) * 5, w['x0']))
                right_words.sort(key=lambda w: (round(w['top'] / 5) * 5, w['x0']))
                
                left_text = cls._words_to_text(left_words)
                right_text = cls._words_to_text(right_words)
                return f"{left_text}\n\n{right_text}"
            else:
                return page.extract_text(layout=False) or ""
        except Exception:
            return page.extract_text() or ""

    @staticmethod
    def _words_to_text(words: List[dict]) -> str:
        """Reconstructs text lines from word bounding boxes."""
        lines: List[str] = []
        current_line: List[str] = []
        current_top: Optional[float] = None

        for w in words:
            if current_top is None:
                current_top = w['top']
                current_line.append(w['text'])
            elif abs(w['top'] - current_top) < 6:
                current_line.append(w['text'])
            else:
                lines.append(" ".join(current_line))
                current_line = [w['text']]
                current_top = w['top']

        if current_line:
            lines.append(" ".join(current_line))
            
        return "\n".join(lines)

    @classmethod
    def _extract_docx(cls, file_path: str) -> Tuple[str, str]:
        """Extracts text from DOCX documents including tables and headers."""
        try:
            doc = docx.Document(file_path)
            content_blocks: List[str] = []

            # Paragraphs
            for p in doc.paragraphs:
                text = p.text.strip()
                if text:
                    content_blocks.append(text)

            # Tables
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        content_blocks.append(" | ".join(row_cells))

            return "\n\n".join(content_blocks).strip(), "python-docx"
        except Exception as e:
            logger.error(f"Error reading docx {file_path}: {e}")
            raise ValueError(f"The DOCX file is corrupted, invalid or unreadable: {e}")

    @classmethod
    def _extract_image(cls, file_path: str) -> Tuple[str, str]:
        """Extracts text from an image file using Tesseract OCR."""
        if not is_tesseract_available():
            raise RuntimeError("Tesseract OCR is not installed or not in PATH to process image resumes.")
        
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text.strip(), "tesseract_ocr"
        except Exception as e:
            logger.error(f"Error extracting image {file_path}: {e}")
            raise

    @classmethod
    def _extract_pdf_ocr(cls, file_path: str) -> str:
        """Extracts OCR text from scanned PDF pages using pypdfium2 / pdfplumber image conversion."""
        text_pages: List[str] = []
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(file_path)
            for page in pdf:
                pil_image = page.render(scale=2.0).to_pil()
                page_text = pytesseract.image_to_string(pil_image)
                text_pages.append(page_text.strip())
            return "\n\n".join(text_pages)
        except Exception as e:
            logger.warning(f"PDF OCR failed: {e}")
            return ""

