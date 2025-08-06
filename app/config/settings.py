"""
Application settings and configuration
"""
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API settings
    API_KEY: str = os.getenv("API_KEY", "test_api_key")
    
    # Service settings
    SERVICE_NAME: str = "vision-insurance-extractor"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Document limits
    MAX_DOCUMENT_SIZE_MB: int = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "10"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        """
        Pydantic configuration
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings() 