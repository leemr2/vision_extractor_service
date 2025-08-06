"""
Provider mappings module for standardizing terminology across different vision insurance providers.
"""

from typing import Dict, Any, List


class ProviderMappings:
    """
    Maps provider-specific terminology to standard terminology.
    Ensures consistent output regardless of provider-specific language.
    """
    
    # Exam frequency mappings
    EXAM_FREQUENCY_MAPPINGS = {
        "once per year": "12 months",
        "once every year": "12 months",
        "once every 12 months": "12 months",
        "1 per year": "12 months",
        "1 per 12 months": "12 months",
        "once every 24 months": "24 months",
        "once every two years": "24 months",
        "1 per 24 months": "24 months",
        # Add more mappings as needed
    }
    
    # Lens frequency mappings
    LENS_FREQUENCY_MAPPINGS = {
        "once per year": "12 months",
        "once every year": "12 months",
        "once every 12 months": "12 months",
        "1 per year": "12 months",
        "1 per 12 months": "12 months",
        "once every 24 months": "24 months",
        "once every two years": "24 months",
        "1 per 24 months": "24 months",
        # Add more mappings as needed
    }
    
    # Frame frequency mappings
    FRAME_FREQUENCY_MAPPINGS = {
        "once every year": "12 months",
        "once per year": "12 months",
        "once every 12 months": "12 months",
        "1 per year": "12 months",
        "1 per 12 months": "12 months",
        "once every 24 months": "24 months",
        "once every two years": "24 months",
        "1 per 24 months": "24 months",
        # Add more mappings as needed
    }
    
    # Copay amount mappings
    COPAY_MAPPINGS = {
        "$0": "$0",
        "zero dollars": "$0",
        "no charge": "$0",
        "covered in full": "$0",
        "$10": "$10",
        "$15": "$15",
        "$20": "$20",
        "$25": "$25",
        # Add more mappings as needed
    }
    
    # VSP-specific mappings
    VSP_MAPPINGS = {
        "wellvision exam": "eye exam",
        "signature plan": "signature",
        "choice plan": "choice",
        # Add more mappings as needed
    }
    
    # EyeMed-specific mappings
    EYEMED_MAPPINGS = {
        "standard plastic lenses": "lenses",
        "frames": "frames",
        "contact lens fit and follow-up": "contact lens fitting",
        # Add more mappings as needed
    }
    
    # Davis-specific mappings
    DAVIS_MAPPINGS = {
        "fashion frames": "frames",
        "designer frames": "frames",
        "premier frames": "frames",
        # Add more mappings as needed
    }
    
    # Spectera-specific mappings
    SPECTERA_MAPPINGS = {
        "eye examination": "eye exam",
        # Add more mappings as needed
    }
    
    # Superior-specific mappings
    SUPERIOR_MAPPINGS = {
        "eye examination": "eye exam",
        # Add more mappings as needed
    }
    
    @staticmethod
    def standardize_frequency(value: str, frequency_type: str = "exam") -> str:
        """
        Standardizes frequency strings to a consistent format.
        
        Args:
            value: The frequency string to standardize
            frequency_type: The type of frequency (exam, lens, frame)
            
        Returns:
            A standardized frequency string
        """
        value_lower = value.lower().strip()
        
        if frequency_type == "exam":
            return ProviderMappings.EXAM_FREQUENCY_MAPPINGS.get(value_lower, value)
        elif frequency_type == "lens":
            return ProviderMappings.LENS_FREQUENCY_MAPPINGS.get(value_lower, value)
        elif frequency_type == "frame":
            return ProviderMappings.FRAME_FREQUENCY_MAPPINGS.get(value_lower, value)
        
        return value
    
    @staticmethod
    def standardize_copay(value: str) -> str:
        """
        Standardizes copay amounts to a consistent format.
        
        Args:
            value: The copay string to standardize
            
        Returns:
            A standardized copay string
        """
        value_lower = value.lower().strip()
        return ProviderMappings.COPAY_MAPPINGS.get(value_lower, value)
    
    @staticmethod
    def get_provider_mapping(provider: str) -> Dict[str, str]:
        """
        Gets the provider-specific term mappings.
        
        Args:
            provider: The provider name
            
        Returns:
            A dictionary of provider-specific mappings
        """
        provider_lower = provider.lower().strip()
        
        if "vsp" in provider_lower:
            return ProviderMappings.VSP_MAPPINGS
        elif "eyemed" in provider_lower:
            return ProviderMappings.EYEMED_MAPPINGS
        elif "davis" in provider_lower:
            return ProviderMappings.DAVIS_MAPPINGS
        elif "spectera" in provider_lower:
            return ProviderMappings.SPECTERA_MAPPINGS
        elif "superior" in provider_lower:
            return ProviderMappings.SUPERIOR_MAPPINGS
        
        return {} 