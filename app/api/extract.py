"""
API endpoints for vision insurance document extraction
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks, Request
from typing import Optional, Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.processor import process_document
from app.core.utils.validator import validate_pdf
from app.core.models.standard_models import ExtractionRequest, ExtractionResponse, ErrorResponse, ProviderType
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize limiter for this router
limiter = Limiter(key_func=get_remote_address)


@router.post("/extract", status_code=status.HTTP_200_OK, response_model=ExtractionResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def extract_document(
    request: Request,
    file: UploadFile = File(...),
    provider_hint: str = Form(...),
    extract_all: bool = Form(False),
    background_tasks: BackgroundTasks = None
):
    """
    Extract structured vision benefits information from a vision insurance document
    
    Args:
        file: PDF document to process
        provider_hint: Insurance provider (required)
        extract_all: Whether to extract all available information or just core benefits
        background_tasks: FastAPI background tasks handler
        
    Returns:
        JSON response with extracted benefit information
    """
    # Validate provider hint
    try:
        ProviderType(provider_hint.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider_hint}. Supported providers: {[p.value for p in ProviderType if p != ProviderType.UNKNOWN]}",
            headers={"X-Error-Code": "invalid_provider"}
        )
    
    # Validate input file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
            headers={"X-Error-Code": "unsupported_file_type"}
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Enforce file size limit
        max_size = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024  # Convert to bytes
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_DOCUMENT_SIZE_MB}MB",
                headers={"X-Error-Code": "file_too_large"}
            )
        
        # Validate PDF
        validate_pdf(contents)
        
        # Normalize provider hint (already validated above, but normalize for consistency)
        normalized_provider_hint = ProviderType(provider_hint.lower()).value
        
        # Process document and extract benefits
        result = await process_document(
            file_content=contents,
            filename=file.filename,
            provider_hint=normalized_provider_hint
        )
        
        # Add cleanup task if needed
        if background_tasks:
            # Could add tasks like removing temp files, logging, etc.
            pass
        
        return result
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle validation errors
        logger.error(f"Validation error: {e}")
        error_response = ErrorResponse(
            error="validation_error",
            detail=str(e),
            code="ERR_VALIDATION"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=dict(error_response)
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Processing error: {e}", exc_info=True)
        error_response = ErrorResponse(
            error="processing_error",
            detail=str(e),
            code="ERR_PROCESSING"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=dict(error_response)
        )
    finally:
        await file.close()


@router.get("/providers", status_code=status.HTTP_200_OK)
async def list_supported_providers():
    """
    Get a list of supported vision insurance providers
    
    Returns:
        List of supported provider names and IDs
    """
    return {
        "providers": [
            {"id": ProviderType.VSP.value, "name": "VSP Vision Care"},
            {"id": ProviderType.EYEMED.value, "name": "EyeMed Vision Care"},
            {"id": ProviderType.DAVIS.value, "name": "Davis Vision"},
            {"id": ProviderType.SPECTERA.value, "name": "Spectera"},
            {"id": ProviderType.SUPERIOR.value, "name": "Superior Vision"},
        ]
    } 