"""
Text cleaning and normalization for document processing
"""
import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Clean and normalize extracted document text
    
    Args:
        text: Raw text extracted from document
        
    Returns:
        Normalized text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'[\r\n]+', '\n', text)
    
    # Fix common OCR errors in insurance documents
    text = _fix_ocr_errors(text)
    
    return text.strip()


def _fix_ocr_errors(text: str) -> str:
    """
    Fix common OCR errors in insurance documents
    
    Args:
        text: Text with potential OCR errors
        
    Returns:
        Text with common OCR errors fixed
    """
    # Common OCR error replacements
    replacements = [
        (r'l\/lonocular', 'Monocular'),
        (r'B\|focal', 'Bifocal'),
        (r'Tn(focal|focaI)', 'Trifocal'),
        (r'Pol[y\|]carb[o0]nate', 'Polycarbonate'),
        (r'Pr[o0]gress[i1]ve', 'Progressive'),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text 