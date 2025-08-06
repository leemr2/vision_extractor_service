"""
Provider-specific regex patterns for document classification
"""
from typing import Dict, List

from app.core.models.standard_models import ProviderType


# Regex patterns to identify document provider
PROVIDER_PATTERNS: Dict[str, List[str]] = {
    ProviderType.VSP.value: [
        r"VSP|Vision Service Plan",
        r"VSP Choice Plan",
        r"VSP Signature Plan",
        r"VSP Advantage",
        r"www\.vsp\.com",
    ],
    
    ProviderType.EYEMED.value: [
        r"EyeMed",
        r"Eye Med",
        r"EyeMed Vision Care",
        r"EyeMed Insurance Company",
        r"www\.eyemed\.com",
        r"Insight Network",
        r"Select Network",
        r"Advantage Network",
    ],
    
    ProviderType.DAVIS.value: [
        r"Davis Vision",
        r"Davis Vision Insurance",
        r"DavisVision",
        r"www\.davisvision\.com",
    ],
    
    ProviderType.SPECTERA.value: [
        r"Spectera",
        r"Spectera Vision",
        r"UnitedHealthcare Vision",
        r"www\.spectera\.com",
        r"www\.myuhcvision\.com",
    ],
    
    ProviderType.SUPERIOR.value: [
        r"Superior Vision",
        r"Superior National",
        r"Superior Vision Services",
        r"www\.superiorvision\.com",
    ],
    
    ProviderType.VERSANT.value: [
        r"Versant Health",
        r"Versant\s+Health",
        r"www\.versanthealth\.com",
        r"Davis Vision.*Versant Health",
        r"Superior Vision.*Versant Health",
        r"Versant Health.*Davis Vision",
        r"Versant Health.*Superior Vision",
    ],
} 