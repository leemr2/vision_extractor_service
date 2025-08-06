"""
Base extractor module providing common functionality for all provider-specific extractors.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for all vision insurance extractors.
    Defines the common interface and provides shared utility methods.
    """
    
    def __init__(self, provider_name: str):
        """
        Initialize the base extractor.
        
        Args:
            provider_name: The name of the insurance provider
        """
        self.provider_name = provider_name
        self.extracted_data = {}
        self.confidence_scores = {}
    
    def reset(self):
        """
        Reset the extractor's internal state by clearing extracted data and confidence scores.
        This is useful when reusing the same extractor instance for multiple documents.
        """
        self.extracted_data = {}
        self.confidence_scores = {}
    
    @abstractmethod
    async def extract(self, document_text: str, document_path: str) -> Dict[str, Any]:
        """
        Extract structured data from the document.
        This method must be implemented by all concrete extractors.
        
        Args:
            document_text: The extracted text from the document
            document_path: Path to the original document file
            
        Returns:
            A dictionary of extracted information
        """
        pass
    
    @abstractmethod
    async def extract_exam_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract examination benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of examination benefits
        """
        pass
    
    @abstractmethod
    async def extract_frame_benefits(self, document_text: str) -> str:
        """
        Extract frame benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            Frame benefit cost value as a string
        """
        pass
    
    @abstractmethod
    async def extract_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract lens benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of lens benefits
        """
        pass
    
    @abstractmethod
    async def extract_progressive_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract progressive lens benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of progressive lens benefits
        """
        pass
    
    @abstractmethod
    async def extract_lens_options(self, document_text: str) -> Dict[str, Any]:
        """
        Extract lens options information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of lens options
        """
        pass
    
    @abstractmethod
    async def extract_contact_lens_fit(self, document_text: str) -> Dict[str, Any]:
        """
        Extract contact lens fit benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of contact lens fit benefits
        """
        pass
    
    @abstractmethod
    async def extract_contact_lenses(self, document_text: str) -> Dict[str, Any]:
        """
        Extract contact lenses benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of contact lenses benefits
        """
        pass
    
    async def preprocess_text(self, text: str) -> str:
        """
        Preprocess document text for extraction.
        
        Args:
            text: The raw document text
            
        Returns:
            Preprocessed text
        """
        # Basic preprocessing - can be overridden by specific extractors
        if not text:
            return ""
        
        # Remove excessive whitespace
        processed = " ".join(text.split())
        return processed
    
    def set_confidence(self, field: str, score: float) -> None:
        """
        Set confidence score for an extracted field.
        
        Args:
            field: The field name
            score: Confidence score (0.0-1.0)
        """
        self.confidence_scores[field] = max(0.0, min(1.0, score))
    
    def get_overall_confidence(self) -> float:
        """
        Calculate the overall confidence score.
        
        Returns:
            Average confidence score across all fields
        """
        if not self.confidence_scores:
            return 0.0
        
        return sum(self.confidence_scores.values()) / len(self.confidence_scores)
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata about the extraction process.
        
        Returns:
            A dictionary of metadata
        """
        return {
            "provider": self.provider_name,
            "confidence": self.get_overall_confidence(),
            "confidence_scores": self.confidence_scores
        }
    
    def get_result(self) -> Dict[str, Any]:
        """
        Get the final extraction result with metadata.
        
        Returns:
            A dictionary with extracted data and metadata
        """
        # Combine extracted data with metadata
        result = self.extracted_data.copy()
        
        # Add metadata
        metadata = self.extract_metadata()
        result["provider"] = metadata["provider"]
        result["confidence"] = metadata["confidence"]
        result["confidence_scores"] = metadata["confidence_scores"]
        
        return result

    def _extract_lens_categories(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Helper method to extract lens categories from document sections
        
        Args:
            sections: List of document sections
            
        Returns:
            List of lens categories with options
        """
        # This is a placeholder implementation
        # To be overridden by provider-specific extractors
        return [] 