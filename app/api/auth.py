"""
Authentication logic for API access
"""
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config.settings import settings

# API key header definition
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    """
    Validate the API key provided in the Authorization header
    
    Args:
        api_key_header: The Authorization header value
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid or missing
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    # Check if header has the expected format "Bearer API_KEY"
    if not api_key_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    # Extract the API key
    api_key = api_key_header.replace("Bearer ", "")
    
    # Validate the API key
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key 