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
    
    # Use context manager for automatic temp file cleanup
    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        prefix=f"{extraction_id}_",
        delete=True  # Auto-delete on close
    ) as temp_file:
        try:
            # Write content to temp file
            temp_file.write(file_content)
            temp_file.flush()  # Ensure data is written to disk
            temp_path = temp_file.name
            
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
            
        except (OSError, IOError) as e:
            logger.error(f"File operation failed: {e}")
            from fastapi import HTTPException, status as http_status
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document processing failed"
            )
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    # File automatically deleted when exiting context
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
    
    # Use context managers for automatic temp file cleanup
    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        prefix=f"{extraction_id}_file1_",
        delete=True
    ) as temp_file1, tempfile.NamedTemporaryFile(
        suffix=".pdf",
        prefix=f"{extraction_id}_file2_",
        delete=True
    ) as temp_file2:
        try:
            # Write both files to temp locations
            temp_file1.write(file1_content)
            temp_file1.flush()
            temp_path1 = temp_file1.name
            
            temp_file2.write(file2_content)
            temp_file2.flush()
            temp_path2 = temp_file2.name
            
            # Create VSP extractor instance
            vsp_extractor = VSPExtractor()
            
            # Process both documents through the VSP extractor
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
            
        except (OSError, IOError) as e:
            logger.error(f"File operation failed: {e}")
            from fastapi import HTTPException, status as http_status
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process documents"
            )
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    # Files automatically deleted when exiting context
    return response.dict()  # Use dict() for Pydantic v1.x


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