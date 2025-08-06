"""
Unified Versant Template - Standard output structure for all Versant Health products.
Handles Davis Vision, Superior Vision, and Versant Health documents.
"""

from pydantic import BaseModel, Field
from typing import Optional
from app.core.templates.davis_template import DavisTemplate

class VersantUnifiedTemplate(DavisTemplate):
    """
    Unified template for all Versant Health products (Davis Vision, Superior Vision, Versant Health).
    Inherits from DavisTemplate since all three providers use the same tabular document format.
    """
    
    def __init__(self, provider: str = "Versant Health", **data):
        """
        Initialize the template with the correct provider information.
        
        Args:
            provider: The specific provider name (Davis Vision, Superior Vision, or Versant Health)
            **data: Additional template data
        """
        # Set provider-specific defaults
        data.setdefault('provider', provider)
        data.setdefault('plan_name', provider)
        data.setdefault('document_type', 'Vision Benefits')
        
        super().__init__(**data)
    
    class Config:
        allow_population_by_field_name = True
        anystr_strip_whitespace = True