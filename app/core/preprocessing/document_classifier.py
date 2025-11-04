"""
Document classifier for vision insurance provider validation.
Provider types are user-defined and validated, not auto-detected.
"""
import re
import logging
from typing import Dict

from app.core.models.standard_models import ProviderType
from app.config.provider_patterns import PROVIDER_PATTERNS

logger = logging.getLogger(__name__)


async def detect_provider(provider_hint: str) -> str:
    """
    Validate and return the user-provided insurance provider type.
    
    The provider type is always user-defined and required. This function
    validates the provider hint and returns the normalized provider value.
    
    Args:
        provider_hint: User-provided provider selection (required)
        
    Returns:
        The normalized insurance provider name
        
    Raises:
        ValueError: If the provider hint is invalid or not supported
    """
    try:
        provider_enum = ProviderType(provider_hint.lower())
        logger.info(f"Using user-provided provider: {provider_hint}")
        return provider_enum.value
    except ValueError:
        logger.error(f"Invalid provider hint: {provider_hint}")
        raise ValueError(
            f"Unsupported provider: {provider_hint}. "
            f"Supported providers: {[p.value for p in ProviderType if p != ProviderType.UNKNOWN]}"
        )


async def get_confidence_scores(document_text: str) -> Dict[str, float]:
    """
    Get confidence scores for each provider based on pattern matches.
    
    Note: This function is currently unused and maintained for potential future
    debugging or audit purposes. Provider detection is now user-defined.
    
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