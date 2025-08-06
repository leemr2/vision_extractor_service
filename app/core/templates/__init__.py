"""
Templates package for standardized vision insurance output data structures.
"""

from app.core.templates.vsp_template import VSPTemplate
from app.core.templates.eyemed_template import EyeMedTemplate
from app.core.templates.davis_template import DavisTemplate
from app.core.templates.spectera_template import SpecteraTemplate
from app.core.templates.versant_unified_template import VersantUnifiedTemplate

__all__ = [
    'VSPTemplate',
    'EyeMedTemplate',
    'DavisTemplate',
    'SpecteraTemplate',
    'VersantUnifiedTemplate',
] 