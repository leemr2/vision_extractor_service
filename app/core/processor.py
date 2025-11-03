"""
Document processing orchestration module
"""
import io
import os
import time
import uuid
import logging
import tempfile
from typing import Dict, Any, Optional, BinaryIO
from pathlib import Path

from app.core.preprocessing.document_classifier import detect_provider
from app.core.preprocessing.text_normalizer import normalize_text
from app.core.preprocessing.structure_analyzer import analyze_structure
from app.core.preprocessing.term_annotator import annotate_terms
from app.core.utils.security import redact_phi
from app.core.utils.pdf_utils import extract_text_from_pdf
from app.core.extractors.vsp_extractor import VSPExtractor
from app.core.extractors.eyemed_extractor import EyeMedExtractor
from app.core.extractors.spectera_extractor import SpecteraExtractor
from app.core.extractors.versant_tabular_extractor import VersantTabularExtractor
from app.core.models.standard_models import ProviderType, ExtractionResponse, DocumentMetadata
from app.core.validators.schema_validator import SchemaValidator

logger = logging.getLogger(__name__)


async def process_document(file_content: bytes, filename: str, provider_hint: str) -> Dict[str, Any]:
    """
    Process a document and extract structured vision insurance information.
    
    Args:
        file_content: Raw document bytes
        filename: Original filename
        provider_hint: Insurance provider (required)
        
    Returns:
        Dictionary containing structured benefit information
    """
    start_time = time.time()
    
    # Create a unique extraction ID
    extraction_id = str(uuid.uuid4())
    
    # Convert bytes to file-like object
    pdf_file = io.BytesIO(file_content)
    
    # Create a temporary file for the document (cross-platform)
    temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf", prefix=f"{extraction_id}_")
    try:
        with os.fdopen(temp_fd, "wb") as f:
            f.write(file_content)
    except (OSError, IOError) as e:
        # If writing fails, close the file descriptor to avoid leaks
        logger.error(f"Failed to write temp file: {e}")
        try:
            os.close(temp_fd)
        except OSError:
            pass  # Already closed or invalid
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document"
        )
    
    # Extract text from document
    text = await extract_text_from_pdf(pdf_file)
    
    # Use user-provided provider (trusted)
    detected_provider = await detect_provider(text, provider_hint)
    provider_type = ProviderType(detected_provider.lower())
    
    # Redact PHI if present
    redacted_text = await redact_phi(text)
    
    # Get appropriate extractor based on provider
    extractor = await get_extractor(provider_type)
    
    # Extract structured data
    extraction_result = await extractor.extract(redacted_text, temp_path)
    
    # Handle different extractor return formats
    if "data" in extraction_result:
        # New structured format with separate data and metadata
        extracted_data = extraction_result["data"]
        confidence = extraction_result.get("metadata", {}).get("confidence", 0.8)
    else:
        # Legacy flat format from get_result() or direct data return
        # Extract metadata fields and remove them from the data
        confidence = extraction_result.pop("confidence", 0.8)
        extraction_result.pop("confidence_scores", None)
        extraction_result.pop("provider", None)
        extracted_data = extraction_result
    
    # Validate the extracted data against the appropriate template
    try:
        validated_data = SchemaValidator.validate(provider_type, extracted_data)
    except ValueError as e:
        logger.warning(f"Validation failed: {str(e)}")
        # Continue with unvalidated data if validation fails
        validated_data = extracted_data
    
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Build the response
    response = ExtractionResponse(
        provider=provider_type.value,
        extraction_id=extraction_id,
        data=validated_data.dict() if hasattr(validated_data, 'dict') else (dict(validated_data) if hasattr(validated_data, "__dict__") else validated_data),
        confidence=confidence,
        warnings=[],  # Add any warnings that occurred during extraction
        processing_time=processing_time
    )
    
    # Cleanup temp file
    try:
        Path(temp_path).unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Error cleaning up temp file: {e}")
    
    return response.dict()  # Use dict() for Pydantic v1.x


async def process_vsp_documents(
    file1_content: bytes, 
    file1_name: str,
    file2_content: bytes, 
    file2_name: str,
    provider_hint: str = "vsp"
) -> Dict[str, Any]:
    """
    Process two VSP documents (Patient Record Report and Lens Enhancements) together.
    
    Args:
        file1_content: Raw bytes of first document
        file1_name: Filename of first document
        file2_content: Raw bytes of second document  
        file2_name: Filename of second document
        provider_hint: Insurance provider (defaults to "vsp" for dual-file processing)
        
    Returns:
        Dictionary containing structured benefit information from both documents
    """
    start_time = time.time()
    
    # Create a unique extraction ID
    extraction_id = str(uuid.uuid4())
    
    # Create temporary files for both documents
    temp_fd1, temp_path1 = tempfile.mkstemp(suffix=".pdf", prefix=f"{extraction_id}_file1_")
    temp_fd2, temp_path2 = tempfile.mkstemp(suffix=".pdf", prefix=f"{extraction_id}_file2_")
    
    try:
        # Write both files to temp locations
        with os.fdopen(temp_fd1, "wb") as f1:
            f1.write(file1_content)
        with os.fdopen(temp_fd2, "wb") as f2:
            f2.write(file2_content)
    except (OSError, IOError) as e:
        # If writing fails, close the file descriptors to avoid leaks
        logger.error(f"Failed to write temp files: {e}")
        try:
            os.close(temp_fd1)
        except OSError:
            pass
        try:
            os.close(temp_fd2)
        except OSError:
            pass
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process documents"
        )
    
    try:
        # Create VSP extractor instance
        vsp_extractor = VSPExtractor()
        
        # Process both documents through the VSP extractor
        # We'll modify the VSP extractor to handle multiple files
        extraction_result = await vsp_extractor.extract_from_multiple_files(
            [temp_path1, temp_path2],
            [file1_name, file2_name]
        )
        
        # Handle different extractor return formats
        if "data" in extraction_result:
            # New structured format with separate data and metadata
            extracted_data = extraction_result["data"]
            confidence = extraction_result.get("metadata", {}).get("confidence", 0.8)
        else:
            # Legacy flat format from get_result() or direct data return
            confidence = extraction_result.pop("confidence", 0.8)
            extraction_result.pop("confidence_scores", None)
            extraction_result.pop("provider", None)
            extracted_data = extraction_result
        
        # Validate the extracted data against the VSP template
        try:
            validated_data = SchemaValidator.validate(ProviderType.VSP, extracted_data)
        except ValueError as e:
            logger.warning(f"Validation failed: {str(e)}")
            # Continue with unvalidated data if validation fails
            validated_data = extracted_data
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Build the response
        response = ExtractionResponse(
            provider="vsp",
            extraction_id=extraction_id,
            data=validated_data.dict() if hasattr(validated_data, 'dict') else (dict(validated_data) if hasattr(validated_data, "__dict__") else validated_data),
            confidence=confidence,
            warnings=[],  # Add any warnings that occurred during extraction
            processing_time=processing_time
        )
        
        return response.dict()  # Use dict() for Pydantic v1.x
        
    finally:
        # Cleanup temp files
        try:
            Path(temp_path1).unlink(missing_ok=True)
            Path(temp_path2).unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")


async def get_extractor(provider: ProviderType):
    """
    Get the appropriate extractor for a given insurance provider.
    
    Args:
        provider: The detected insurance provider
        
    Returns:
        An extractor instance for the provider
    
    Raises:
        ValueError: If no extractor is available for the provider
    """
    extractors = {
        ProviderType.VSP: VSPExtractor(),
        ProviderType.EYEMED: EyeMedExtractor(),
        ProviderType.DAVIS: VersantTabularExtractor("Davis Vision"),
        ProviderType.SPECTERA: SpecteraExtractor(),
        ProviderType.SUPERIOR: VersantTabularExtractor("Superior Vision"),
        ProviderType.VERSANT: VersantTabularExtractor("Versant Health"),
    }
    
    if provider not in extractors:
        raise ValueError(f"No extractor available for provider: {provider.value}")
    
    return extractors[provider] 