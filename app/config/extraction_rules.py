"""
Business rules for benefit extraction
"""
from typing import Dict, List, Any
from enum import Enum

from app.core.models.insurance_types import InsuranceProvider


# Rule types for extraction
class RuleType(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"
    CONDITIONAL = "conditional"


# Business rules for benefit extraction
EXTRACTION_RULES: Dict[InsuranceProvider, Dict[str, Dict[str, Any]]] = {
    InsuranceProvider.VSP: {
        "lens_categories": {
            "type": RuleType.REQUIRED.value,
            "subcategories": {
                "single_vision": {"type": RuleType.REQUIRED.value},
                "bifocal": {"type": RuleType.REQUIRED.value},
                "trifocal": {"type": RuleType.REQUIRED.value},
                "progressive": {"type": RuleType.REQUIRED.value},
            }
        },
        "lens_options": {
            "type": RuleType.REQUIRED.value,
            "options": {
                "polycarbonate": {"type": RuleType.REQUIRED.value},
                "anti_reflective": {"type": RuleType.REQUIRED.value},
                "photochromic": {"type": RuleType.REQUIRED.value},
                "scratch_resistant": {"type": RuleType.REQUIRED.value},
                "uv_protection": {"type": RuleType.OPTIONAL.value},
            }
        },
        "frequency": {
            "type": RuleType.REQUIRED.value,
            "fields": {
                "exam": {"type": RuleType.REQUIRED.value},
                "lenses": {"type": RuleType.REQUIRED.value},
                "frames": {"type": RuleType.REQUIRED.value},
                "contacts": {"type": RuleType.OPTIONAL.value},
            }
        },
        "copays": {
            "type": RuleType.REQUIRED.value,
            "fields": {
                "exam": {"type": RuleType.REQUIRED.value},
                "materials": {"type": RuleType.OPTIONAL.value},
            }
        },
    },
    
    InsuranceProvider.EYEMED: {
        "lens_categories": {
            "type": RuleType.REQUIRED.value,
            "subcategories": {
                "single_vision": {"type": RuleType.REQUIRED.value},
                "bifocal": {"type": RuleType.REQUIRED.value},
                "trifocal": {"type": RuleType.REQUIRED.value},
                "progressive": {"type": RuleType.REQUIRED.value},
            }
        },
        "lens_options": {
            "type": RuleType.REQUIRED.value,
            "options": {
                "polycarbonate": {"type": RuleType.REQUIRED.value},
                "anti_reflective": {"type": RuleType.REQUIRED.value},
                "photochromic": {"type": RuleType.REQUIRED.value},
                "scratch_resistant": {"type": RuleType.REQUIRED.value},
                "uv_protection": {"type": RuleType.OPTIONAL.value},
            }
        },
        "frequency": {
            "type": RuleType.REQUIRED.value,
            "fields": {
                "exam": {"type": RuleType.REQUIRED.value},
                "lenses": {"type": RuleType.REQUIRED.value},
                "frames": {"type": RuleType.REQUIRED.value},
                "contacts": {"type": RuleType.OPTIONAL.value},
            }
        },
        "copays": {
            "type": RuleType.REQUIRED.value,
            "fields": {
                "exam": {"type": RuleType.REQUIRED.value},
                "materials": {"type": RuleType.OPTIONAL.value},
            }
        },
    },
    
    # Placeholder rules for other providers
    InsuranceProvider.DAVIS: {
        "lens_categories": {
            "type": RuleType.REQUIRED.value,
            "subcategories": {
                "single_vision": {"type": RuleType.REQUIRED.value},
                "bifocal": {"type": RuleType.REQUIRED.value},
                "trifocal": {"type": RuleType.REQUIRED.value},
                "progressive": {"type": RuleType.REQUIRED.value},
            }
        },
    },
    
    InsuranceProvider.SPECTERA: {
        "lens_categories": {
            "type": RuleType.REQUIRED.value,
            "subcategories": {
                "single_vision": {"type": RuleType.REQUIRED.value},
                "bifocal": {"type": RuleType.REQUIRED.value},
                "trifocal": {"type": RuleType.REQUIRED.value},
                "progressive": {"type": RuleType.REQUIRED.value},
            }
        },
    },
    
    InsuranceProvider.SUPERIOR: {
        "lens_categories": {
            "type": RuleType.REQUIRED.value,
            "subcategories": {
                "single_vision": {"type": RuleType.REQUIRED.value},
                "bifocal": {"type": RuleType.REQUIRED.value},
                "trifocal": {"type": RuleType.REQUIRED.value},
                "progressive": {"type": RuleType.REQUIRED.value},
            }
        },
    },
}


# Helper functions for rule validation
def validate_required_field(data: Dict[str, Any], field_path: List[str]) -> bool:
    """
    Validate that a required field is present in the data
    
    Args:
        data: Data to validate
        field_path: List of fields to traverse to reach the target field
        
    Returns:
        True if the field is present and has a value, False otherwise
    """
    current = data
    for field in field_path:
        if field not in current:
            return False
        current = current[field]
    
    return current is not None and current != "" and current != []


def validate_extraction_rules(provider: InsuranceProvider, data: Dict[str, Any]) -> List[str]:
    """
    Validate extraction results against business rules
    
    Args:
        provider: Insurance provider
        data: Extracted data
        
    Returns:
        List of validation errors, empty if all rules pass
    """
    errors = []
    provider_rules = EXTRACTION_RULES.get(provider, {})
    
    # Validate required fields
    for category, rules in provider_rules.items():
        if rules["type"] == RuleType.REQUIRED.value and category not in data:
            errors.append(f"Missing required category: {category}")
            continue
        
        # Validate subcategories
        if "subcategories" in rules:
            for subcategory, subcategory_rules in rules["subcategories"].items():
                if subcategory_rules["type"] == RuleType.REQUIRED.value:
                    found = False
                    for item in data.get(category, []):
                        if subcategory in item:
                            found = True
                            break
                    
                    if not found:
                        errors.append(f"Missing required subcategory: {category}.{subcategory}")
    
    return errors 