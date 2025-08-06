"""
Document classifier for vision insurance provider detection
"""
import re
import logging
from typing import Dict, Pattern, Optional

from app.core.models.standard_models import ProviderType
from app.config.provider_patterns import PROVIDER_PATTERNS

logger = logging.getLogger(__name__)


async def detect_provider(document_text: str, provider_hint: Optional[str] = None) -> str:
    """
    Detect the vision insurance provider based on user selection or document text patterns.
    
    Args:
        document_text: The extracted text from the document
        provider_hint: User-provided provider selection (trusted when provided)
        
    Returns:
        The detected insurance provider name
        
    Raises:
        ValueError: If the provider cannot be determined
    """
    # If a provider hint is given, trust it (user knows their insurance better than pattern matching)
    if provider_hint:
        try:
            provider_enum = ProviderType(provider_hint.lower())
            logger.info(f"Using user-provided provider: {provider_hint}")
            return provider_enum.value
        except ValueError:
            logger.warning(f"Invalid provider hint: {provider_hint}")
    
    # Fallback to pattern detection (only when no user input provided)
    confidence_scores = {}
    
    for provider, patterns in PROVIDER_PATTERNS.items():
        # Count how many patterns match for this provider
        matches = 0
        for pattern in patterns:
            if re.search(pattern, document_text, re.IGNORECASE):
                matches += 1
        
        # Calculate confidence score based on matches
        if matches > 0:
            confidence = matches / len(patterns)
            confidence_scores[provider] = confidence
    
    # If we have confidence scores, return the provider with the highest confidence
    if confidence_scores:
        best_provider = max(confidence_scores, key=confidence_scores.get)
        logger.info(f"Auto-detected provider {best_provider} with confidence {confidence_scores[best_provider]:.2f}")
        return best_provider
    
    # Default to unknown if no patterns match
    logger.warning("Unable to determine insurance provider from document")
    return ProviderType.UNKNOWN.value


async def get_confidence_scores(document_text: str) -> Dict[str, float]:
    """
    Get confidence scores for each provider based on pattern matches.
    
    Args:
        document_text: The extracted text from the document
        
    Returns:
        Dictionary with provider names as keys and confidence scores as values
    """
    confidence_scores = {}
    
    for provider, patterns in PROVIDER_PATTERNS.items():
        # Count how many patterns match for this provider
        matches = 0
        for pattern in patterns:
            if re.search(pattern, document_text, re.IGNORECASE):
                matches += 1
        
        # Calculate confidence score based on matches
        if matches > 0:
            confidence = matches / len(patterns)
            confidence_scores[provider] = confidence
        else:
            confidence_scores[provider] = 0.0
    
    return confidence_scores 