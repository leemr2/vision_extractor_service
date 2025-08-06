"""
Enums and constants for insurance providers and document types
"""
from enum import Enum, auto
from typing import Dict, List, Any


class InsuranceProvider(Enum):
    """
    Enum for supported insurance providers
    """
    VSP = "VSP"
    EYEMED = "EyeMed"
    DAVIS = "Davis Vision"
    SPECTERA = "Spectera"
    SUPERIOR = "Superior Vision"


class DocumentType(Enum):
    """
    Enum for document types
    """
    BENEFIT_SUMMARY = "benefit_summary"
    MEMBER_CARD = "member_card"
    CLAIM_FORM = "claim_form"
    LENS_OPTIONS = "lens_options"
    FRAME_COVERAGE = "frame_coverage"
    CONTACT_COVERAGE = "contact_coverage"


class CoverageType(Enum):
    """
    Enum for coverage types
    """
    COVERED = "covered"
    COVERED_IN_FULL = "covered_in_full"
    COPAY = "copay"
    ALLOWANCE = "allowance"
    DISCOUNT = "discount"
    NOT_COVERED = "not_covered"


class LensCategory(Enum):
    """
    Enum for lens categories
    """
    SINGLE_VISION = "single_vision"
    BIFOCAL = "bifocal"
    TRIFOCAL = "trifocal"
    PROGRESSIVE = "progressive"
    CONTACTS = "contacts"
    ENHANCEMENT = "enhancement"


# Mapping of provider-specific terms to standard terms
STANDARD_TERM_MAPPING: Dict[InsuranceProvider, Dict[str, str]] = {
    InsuranceProvider.VSP: {
        "copayment": "copay",
        "covered in full": "covered_in_full",
        "allowance": "allowance",
    },
    InsuranceProvider.EYEMED: {
        "member cost": "copay",
        "covered in full": "covered_in_full",
        "allowance": "allowance",
    },
    InsuranceProvider.DAVIS: {
        "covered": "covered_in_full",
        "copay": "copay",
        "allowance": "allowance",
    },
    InsuranceProvider.SPECTERA: {
        "covered": "covered_in_full",
        "copayment": "copay",
        "allowance": "allowance",
    },
    InsuranceProvider.SUPERIOR: {
        "covered": "covered_in_full",
        "copay": "copay",
        "allowed amount": "allowance",
    }
} 