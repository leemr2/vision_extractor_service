"""
API endpoints for vision insurance document extraction
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks
from typing import Optional, Dict, Any

from app.core.processor import process_document
from app.core.utils.validator import validate_pdf
from app.core.models.standard_models import ExtractionRequest, ExtractionResponse, ErrorResponse, ProviderType

router = APIRouter()


@router.post("/extract", status_code=status.HTTP_200_OK, response_model=ExtractionResponse)
async def extract_document(
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
        
        # Validate PDF
        validate_pdf(contents)
        
        # Normalize provider hint if provided
        normalized_provider_hint = None
        if provider_hint:
            try:
                normalized_provider_hint = ProviderType(provider_hint.lower()).value
            except ValueError:
                # Invalid provider hint, but we'll still try to detect it
                pass
        
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
    except Exception as e:
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