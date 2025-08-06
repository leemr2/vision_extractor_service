"""
PDF validation utilities for checking uploaded files
"""

import io
import os
import logging
import fitz  # PyMuPDF
from typing import Optional, Union, BinaryIO

logger = logging.getLogger(__name__)


def validate_pdf(content: bytes) -> bool:
    """
    Validate that content is a valid PDF file.
    
    Args:
        content: PDF file content as bytes
        
    Returns:
        True if content is a valid PDF
        
    Raises:
        ValueError: If content is not a valid PDF
    """
    # Check file signature/magic bytes
    if not content.startswith(b'%PDF-'):
        raise ValueError("Invalid PDF: Missing PDF signature")
    
    # Try to open the PDF with PyMuPDF
    try:
        pdf_file = io.BytesIO(content)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Check if it has pages
        if len(doc) == 0:
            raise ValueError("Invalid PDF: Document contains no pages")
        
        # Check if we can access the first page
        page = doc.load_page(0)
        
        # Close the document
        doc.close()
        
        return True
    except Exception as e:
        logger.error(f"PDF validation error: {str(e)}")
        raise ValueError(f"Invalid PDF: {str(e)}")


def check_file_size(content: bytes, max_size_mb: float = 10.0) -> bool:
    """
    Check if the file size is within allowed limits.
    
    Args:
        content: File content as bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        True if file size is within limits
        
    Raises:
        ValueError: If file size exceeds the limit
    """
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"File too large: {size_mb:.2f} MB exceeds the {max_size_mb} MB limit")
    return True


def is_text_extractable(content: bytes) -> bool:
    """
    Check if text can be extracted from the PDF.
    
    Args:
        content: PDF file content as bytes
        
    Returns:
        True if text can be extracted, False otherwise
    """
    try:
        pdf_file = io.BytesIO(content)
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Try to extract text from the first page
        page = doc.load_page(0)
        text = page.get_text()
        
        # If we got some text, it's probably extractable
        return len(text.strip()) > 0
    except Exception as e:
        logger.warning(f"Text extraction check failed: {str(e)}")
        return False 