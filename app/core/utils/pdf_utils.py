"""
PDF utility functions for extracting and processing text from PDF documents
"""

import io
import os
import logging
import tempfile
from typing import BinaryIO, List, Dict, Any, Optional, Union
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


async def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
    """
    Extract text content from a PDF document
    
    Args:
        pdf_file: PDF file as a file-like object
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If the PDF cannot be processed
    """
    try:
        # Use PyMuPDF to extract text
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            
            # If the page has very little text, it might be an image that needs OCR
            if len(page_text.strip()) < 50:
                logger.info(f"Page {page_num+1} has little text, attempting OCR")
                ocr_text = await extract_text_with_ocr(page)
                if ocr_text:
                    page_text = ocr_text
            
            text += page_text
        
        # Reset file pointer
        pdf_file.seek(0)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


async def extract_text_with_ocr(page: fitz.Page) -> str:
    """
    Extract text from a PDF page using OCR when necessary
    
    Args:
        page: PDF page object from PyMuPDF
        
    Returns:
        Extracted text content from OCR
    """
    try:
        # Create a temporary directory to store the image
        with tempfile.TemporaryDirectory() as temp_dir:
            # Render page to an image with higher resolution for better OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            image_path = os.path.join(temp_dir, "page.png")
            pix.save(image_path)
            
            # Use Tesseract OCR to extract text from the image
            img = Image.open(image_path)
            ocr_text = pytesseract.image_to_string(img, lang='eng')
            
            return ocr_text
    except Exception as e:
        logger.error(f"OCR extraction failed: {str(e)}")
        return ""


async def extract_tables_from_pdf(pdf_file: BinaryIO) -> List[Dict[str, Any]]:
    """
    Extract tables from a PDF document
    
    Args:
        pdf_file: PDF file as a file-like object
        
    Returns:
        List of extracted tables as dictionaries
        
    Raises:
        ValueError: If the tables cannot be extracted
    """
    # This is a placeholder implementation
    # In a real implementation, this would use a library like Camelot or Tabula
    return []


async def get_pdf_metadata(pdf_file: BinaryIO) -> Dict[str, Any]:
    """
    Extract metadata from a PDF document
    
    Args:
        pdf_file: PDF file as a file-like object
        
    Returns:
        Dictionary of PDF metadata
        
    Raises:
        ValueError: If the metadata cannot be extracted
    """
    try:
        # Use PyMuPDF to extract metadata
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "page_count": len(doc),
            "file_size": pdf_file.tell(),
        }
        
        # Reset file pointer
        pdf_file.seek(0)
        
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from PDF: {str(e)}")
        raise ValueError(f"Failed to extract metadata from PDF: {str(e)}")


def extract_images_from_pdf(pdf_file: Union[str, bytes, BinaryIO]) -> List[bytes]:
    """
    Extract images from a PDF file
    
    Args:
        pdf_file: PDF file path, bytes or file-like object
        
    Returns:
        List of extracted images as bytes
    """
    try:
        # If pdf_file is a file-like object, read its contents
        if hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)  # Reset the file pointer
        elif isinstance(pdf_file, bytes):
            pdf_data = pdf_file
        else:
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        images = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                images.append(image_bytes)
        
        return images
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}")
        return []


def pdf_to_text_with_layout(pdf_file: Union[str, bytes, BinaryIO]) -> str:
    """
    Extract text from PDF preserving layout information
    
    Args:
        pdf_file: PDF file path, bytes or file-like object
        
    Returns:
        Text with layout information preserved
    """
    try:
        # If pdf_file is a file-like object, read its contents
        if hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file.seek(0)  # Reset the file pointer
        elif isinstance(pdf_file, bytes):
            pdf_data = pdf_file
        else:
            with open(pdf_file, 'rb') as f:
                pdf_data = f.read()
        
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        text_with_layout = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Extract text with HTML formatting to preserve layout
            text_with_layout += page.get_text("html")
            text_with_layout += "\n\n"  # Add separation between pages
        
        return text_with_layout
    except Exception as e:
        logger.error(f"Error extracting text with layout from PDF: {str(e)}")
        return "Error extracting text with layout" 