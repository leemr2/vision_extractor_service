"""
Standard models for vision insurance data structures.
Provides common data models used across the application.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class ProviderType(str, Enum):
    """Supported vision insurance providers."""
    VSP = "vsp"
    EYEMED = "eyemed"
    DAVIS = "davis"
    SPECTERA = "spectera"
    SUPERIOR = "superior"
    VERSANT = "versant"
    UNKNOWN = "unknown"


class ExtractionRequest(BaseModel):
    """Model for incoming extraction requests."""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    provider_hint: Optional[ProviderType] = Field(None, description="Optional hint about the insurance provider")
    extract_all: bool = Field(False, description="Whether to extract all available information or just core benefits")


class ExtractionResponse(BaseModel):
    """Standard API response for extraction results."""
    provider: str = Field(..., description="Identified insurance provider")
    extraction_id: str = Field(..., description="Unique identifier for this extraction")
    data: Dict[str, Any] = Field(..., description="Extracted and structured vision insurance data")
    confidence: float = Field(..., description="Confidence score of the extraction (0.0-1.0)")
    warnings: Optional[List[str]] = Field(None, description="Any warnings during extraction")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: str = Field(..., description="Error code")


class DocumentMetadata(BaseModel):
    """Metadata about the processed document."""
    provider: ProviderType = Field(..., description="Identified provider")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    page_count: int = Field(..., description="Number of pages in the document")
    file_size: int = Field(..., description="Size of the document in bytes")
    mime_type: str = Field(..., description="MIME type of the document")
    filename: str = Field(..., description="Original filename") 