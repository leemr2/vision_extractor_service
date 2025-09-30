"""
Schema validator module for validating extracted vision insurance data.
"""

from typing import Dict, Any, Type, Union, Optional
from pydantic import BaseModel, ValidationError

from app.core.templates.vsp_template import VSPTemplate
from app.core.templates.eyemed_template import EyeMedTemplate
from app.core.templates.davis_template import DavisTemplate 
from app.core.templates.spectera_template import SpecteraTemplate
from app.core.models.standard_models import ProviderType

class SchemaValidator:
    """
    Validates extracted data against the appropriate template schema.
    Ensures that the data structure conforms to the expected format before returning to the API.
    """
    
    # Template mapping
    TEMPLATE_MAP = {
        ProviderType.VSP.value: VSPTemplate,
        ProviderType.EYEMED.value: EyeMedTemplate,
        ProviderType.DAVIS.value: DavisTemplate,
        ProviderType.SPECTERA.value: SpecteraTemplate,
        ProviderType.SUPERIOR.value: DavisTemplate,
        ProviderType.VERSANT.value: DavisTemplate,
    }
    
    @staticmethod
    def validate(provider_type: ProviderType, data: Dict[str, Any]) -> Union[VSPTemplate, EyeMedTemplate, DavisTemplate, SpecteraTemplate]:
        """
        Validates the extracted data against the appropriate provider template.
        
        Args:
            provider_type: The type of the provider
            data: The extracted data dictionary
            
        Returns:
            A validated template instance
            
        Raises:
            ValueError: If the provider is not supported or validation fails
        """
        provider_key = provider_type.value.lower().strip()
        
        if provider_key not in SchemaValidator.TEMPLATE_MAP:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        template_class = SchemaValidator.TEMPLATE_MAP[provider_key]
        
        try:
            validated_data = template_class(**data)
            return validated_data
        except ValidationError as e:
            raise ValueError(f"Validation failed for {provider_type}: {str(e)}")
    
    @staticmethod
    def get_template_for_provider(provider_type: ProviderType) -> Optional[Type[BaseModel]]:
        """
        Gets the template class for a given provider.
        
        Args:
            provider_type: The provider type
            
        Returns:
            The template class or None if not found
        """
        provider_key = provider_type.value.lower().strip()
        return SchemaValidator.TEMPLATE_MAP.get(provider_key) 