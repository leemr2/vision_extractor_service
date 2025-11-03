"""
Application settings and configuration
"""
import logging
from typing import List, Union
from pydantic import BaseSettings, validator

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # API settings
    API_KEY: str = ""
    
    # Service settings
    SERVICE_NAME: str = "vision-insurance-extractor"
    DEBUG: bool = False
    
    # CORS settings (accepts string or list, will be parsed to list)
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    # Document limits
    MAX_DOCUMENT_SIZE_MB: int = 10
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """
        Pydantic configuration
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Don't try to parse strings as JSON
        json_loads = lambda x: x
    
    @validator('CORS_ORIGINS', pre=True, always=True)
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://localhost:8000"]
    
    @validator('DEBUG', pre=True)
    def parse_debug(cls, v):
        """Parse DEBUG from string to boolean"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    @validator('API_KEY')
    def validate_api_key(cls, v):
        """Validate API_KEY is set and not the test default"""
        if not v or v == "test_api_key":
            raise ValueError(
                "API_KEY must be set in environment variables. "
                "Never use 'test_api_key' in production."
            )
        return v
    
    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v, values):
        """Warn if CORS wildcard is used in production"""
        debug = values.get('DEBUG', False)
        if "*" in v and not debug:
            logger.warning(
                "CORS wildcard (*) detected in production mode. "
                "This is insecure. Set CORS_ORIGINS explicitly."
            )
        return v


# Create settings instance
settings = Settings() 