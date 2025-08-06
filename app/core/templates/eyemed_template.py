"""
Template for EyeMed vision insurance benefits document extraction.
Defines simplified output structure (no PHI included).
"""
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field


class EligibilityInfo(BaseModel):
    """Eligibility information (boolean flags only, no dates or frequency)"""
    exam_eligible: bool = Field(default=False, description="Whether the member is eligible for an eye exam")
    lenses_eligible: bool = Field(default=False, description="Whether the member is eligible for lenses")
    frame_eligible: bool = Field(default=False, description="Whether the member is eligible for frames")
    contact_lenses_eligible: bool = Field(default=False, description="Whether the member is eligible for contact lenses")


class ExamServices(BaseModel):
    """Exam services benefits"""
    exam: Optional[str] = Field(None, description="Routine eye exam cost")
    retinal_imaging: Optional[str] = Field(None, description="Retinal imaging cost")


class Lenses(BaseModel):
    """Lens benefits"""
    single_vision: Optional[str] = Field(None, description="Single vision lenses cost")
    bifocal: Optional[str] = Field(None, description="Bifocal lenses cost")
    trifocal: Optional[str] = Field(None, description="Trifocal lenses cost")
    lenticular: Optional[str] = Field(None, description="Lenticular lenses cost")


class ProgressiveLenses(BaseModel):
    """Progressive lens benefits"""
    standard: Optional[str] = Field(None, description="Standard progressive lenses cost")
    premium_tier_1: Optional[str] = Field(None, description="Premium Tier 1 progressive lenses cost")
    premium_tier_2: Optional[str] = Field(None, description="Premium Tier 2 progressive lenses cost")
    premium_tier_3: Optional[str] = Field(None, description="Premium Tier 3 progressive lenses cost")
    premium_tier_4: Optional[str] = Field(None, description="Premium Tier 4 progressive lenses cost")
    premium_tier_5: Optional[str] = Field(None, description="Premium Tier 5 Innovations progressive lenses cost")


class AntiReflectiveCoating(BaseModel):
    """Anti-reflective coating benefits"""
    standard: Optional[str] = Field(None, description="Standard anti-reflective coating cost")
    premium_tier_1: Optional[str] = Field(None, description="Premium Tier 1 anti-reflective coating cost")
    premium_tier_2: Optional[str] = Field(None, description="Premium Tier 2 anti-reflective coating cost")
    premium_tier_3: Optional[str] = Field(None, description="Premium Tier 3 anti-reflective coating cost")


class LensOptions(BaseModel):
    """Lens options benefits"""
    anti_reflective_coating: Optional[Dict[str, Any]] = Field(None, description="Anti-reflective coating benefits")
    photochromic: Optional[str] = Field(None, description="Photochromic/Transitions lenses cost")
    polycarbonate: Optional[str] = Field(None, description="Polycarbonate lenses cost")
    scratch_coating: Optional[str] = Field(None, description="Scratch-resistant coating cost")
    tint: Optional[str] = Field(None, description="Tint (solid and gradient) cost")
    uv_treatment: Optional[str] = Field(None, description="UV treatment cost")
    other_options: Optional[str] = Field(None, description="All other lens options cost")


class ContactLensFit(BaseModel):
    """Contact lens fit and follow-up benefits"""
    standard: Optional[str] = Field(None, description="Standard fit cost")
    premium: Optional[str] = Field(None, description="Premium fit cost")


class VisionBenefits(BaseModel):
    """Vision benefits information"""
    exam_services: Optional[Dict[str, Any]] = Field(None, description="Exam service benefits")
    frame: Optional[str] = Field(None, description="Frame benefit")
    lenses: Optional[Dict[str, Any]] = Field(None, description="Lens benefits")
    progressive_lenses: Optional[Dict[str, Any]] = Field(None, description="Progressive lens benefits")
    lens_options: Optional[Dict[str, Any]] = Field(None, description="Lens options benefits")
    contact_lens_fit: Optional[Dict[str, Any]] = Field(None, description="Contact lens fit benefits")


class EyeMedTemplate(BaseModel):
    """
    Template for EyeMed vision insurance document extraction.
    Defines a simplified output structure without PHI.
    """
    provider: str = Field(..., description="Provider name (EyeMed)")
    eligibility_info: EligibilityInfo = Field(..., description="Eligibility information (boolean flags only)")
    vision_benefits: VisionBenefits = Field(..., description="Vision benefits information")
    confidence_score: Optional[float] = Field(None, description="Overall confidence score for the extraction")
    
    # Raw extraction data for debugging/verification
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw extracted data for verification") 