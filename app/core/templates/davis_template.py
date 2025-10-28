"""
Pydantic models for Davis Vision benefit extraction results.
"""
from typing import Dict, Optional, Union, List, Any
from pydantic import BaseModel, Field
import json

# Simplified benefit value type - only int/float/None
BenefitValue = Union[int, float, None]

class SimplifiedBenefitItem(BaseModel):
    """Simplified model for individual benefit items - pricing focused

    Fields:
    - description: Benefit item name/description
    - copay: Out-of-pocket cost (0 if "No Copay", null if not available in plan)
    - allowance: Plan contribution amount (only for Frame/ContactLens "Non Plan" items)
    """
    description: str
    copay: Optional[BenefitValue] = None
    allowance: Optional[BenefitValue] = None

# Keep legacy BenefitItem for backwards compatibility (deprecated)
class BenefitItem(BaseModel):
    """Base model for individual benefit items (DEPRECATED - use SimplifiedBenefitItem)"""
    description: Optional[str] = None
    frequency: Optional[str] = None
    copay: Optional[BenefitValue] = None
    amount_allowed_per_period: Optional[BenefitValue] = None
    available: Optional[str] = None
    next_available_date: Optional[str] = None
    allowance_remaining: Optional[BenefitValue] = None
    auth_required: Optional[str] = None

class ExamBenefits(BaseModel):
    """Models exam-related benefits"""
    routine_exam: Optional[SimplifiedBenefitItem] = Field(None, alias="Routine Exam")

class SpectacleLensBenefits(BaseModel):
    """Models spectacle lens benefits"""
    bifocal_spectacle_lens: Optional[SimplifiedBenefitItem] = Field(None, alias="Bifocal - Spectacle Lens (Plan)")
    single_vision_spectacle_lens: Optional[SimplifiedBenefitItem] = Field(None, alias="Single Vision - Spectacle Lens (Plan)")
    trifocal_spectacle_lens: Optional[SimplifiedBenefitItem] = Field(None, alias="Trifocal - Spectacle Lens (Plan)")
    single_vision_lenticular_myodisc: Optional[SimplifiedBenefitItem] = Field(None, alias="Single Vision - Lenticular Myodisc")

class SpectacleLensOptionsBenefits(BaseModel):
    """Models spectacle lens option benefits"""
    # Anti-reflective coatings
    ar_coating_standard: Optional[SimplifiedBenefitItem] = Field(None, alias="AR Coating Standard")
    ar_coating_premium: Optional[SimplifiedBenefitItem] = Field(None, alias="AR Coating Premium")
    ar_coating_ultra: Optional[SimplifiedBenefitItem] = Field(None, alias="AR Coating Ultra")
    ar_coating_ultimate: Optional[SimplifiedBenefitItem] = Field(None, alias="AR Coating Ultimate")

    # Progressive lenses
    progressive_standard: Optional[SimplifiedBenefitItem] = Field(None, alias="Progressive Standard")
    progressive_premium: Optional[SimplifiedBenefitItem] = Field(None, alias="Progressive Premium")
    progressive_ultra: Optional[SimplifiedBenefitItem] = Field(None, alias="Progressive Ultra")
    progressive_ultimate: Optional[SimplifiedBenefitItem] = Field(None, alias="Progressive Ultimate")

    # Polycarbonate options
    polycarbonate_single_vision: Optional[SimplifiedBenefitItem] = Field(None, alias="Polycarbonate - Single Vision")
    polycarbonate_provided: Optional[SimplifiedBenefitItem] = Field(None, alias="Polycarbonate Provided")
    hd_polycarbonate_single_vision: Optional[SimplifiedBenefitItem] = Field(None, alias="HD Polycarbonate - Single Vision")
    hd_polycarbonate_multifocal: Optional[SimplifiedBenefitItem] = Field(None, alias="HD Polycarbonate - Multifocal")

    # High index lenses
    high_index_167_single_vision: Optional[SimplifiedBenefitItem] = Field(None, alias="HighIndex 1.67 - Single Vision")
    high_index_174_single_vision: Optional[SimplifiedBenefitItem] = Field(None, alias="HighIndex 1.74 - Single Vision")
    high_index_174_multifocal: Optional[SimplifiedBenefitItem] = Field(None, alias="HighIndex 1.74 - Multifocal")

    # Tints and photochromic options
    tint: Optional[SimplifiedBenefitItem] = Field(None, alias="Tint")
    tint_solid: Optional[SimplifiedBenefitItem] = Field(None, alias="Tint Solid")
    tint_gradient: Optional[SimplifiedBenefitItem] = Field(None, alias="Tint Gradient")
    tint_gg: Optional[SimplifiedBenefitItem] = Field(None, alias="Tint GG")
    single_vision_tint_photogrey: Optional[SimplifiedBenefitItem] = Field(None, alias="Single Vision - Tint Photogrey")
    multivision_tint_photogrey: Optional[SimplifiedBenefitItem] = Field(None, alias="Multivision - Tint Photogrey")
    single_vision_tint_plastic_photosensitive: Optional[SimplifiedBenefitItem] = Field(None, alias="Single Vision - Tint Plastic - Photosensitive")
    multivision_tint_plastic_photosensitive: Optional[SimplifiedBenefitItem] = Field(None, alias="Multivision - Tint Plastic - Photosensitive")

    # Other lens options
    blue_light_filtering_ebs: Optional[SimplifiedBenefitItem] = Field(None, alias="Blue Light Filtering - EBS")
    polarized: Optional[SimplifiedBenefitItem] = Field(None, alias="Polarized")
    intermediate_vision: Optional[SimplifiedBenefitItem] = Field(None, alias="Intermediate Vision")
    ultraviolet_coating: Optional[SimplifiedBenefitItem] = Field(None, alias="Ultraviolet Coating")
    scratch_resistant_coating: Optional[SimplifiedBenefitItem] = Field(None, alias="Scratch Resistant Coating")
    scratch_resistant_coating_premium: Optional[SimplifiedBenefitItem] = Field(None, alias="Scratch Resistant Coating Premium")
    single_vision_scratch_resistant_coating_protection: Optional[SimplifiedBenefitItem] = Field(None, alias="Single Vision - Scratch Resistant Coating Protection")
    multivision_scratch_resistant_coating_protection: Optional[SimplifiedBenefitItem] = Field(None, alias="Multivision - Scratch Resistant Coating Protection")
    mirror_solid_single_double_gradient: Optional[SimplifiedBenefitItem] = Field(None, alias="Mirror - Solid, Single & Double Gradient")

    # Edge and special processing options
    edge_polish: Optional[SimplifiedBenefitItem] = Field(None, alias="Edge Polish")
    high_luster_edge_polish: Optional[SimplifiedBenefitItem] = Field(None, alias="High Luster Edge Polish")
    roll_polish: Optional[SimplifiedBenefitItem] = Field(None, alias="Roll Polish")
    roll_edge: Optional[SimplifiedBenefitItem] = Field(None, alias="Roll Edge")
    rimless_drill: Optional[SimplifiedBenefitItem] = Field(None, alias="Rimless Drill")
    slab_off: Optional[SimplifiedBenefitItem] = Field(None, alias="Slab Off")
    blended_segment: Optional[SimplifiedBenefitItem] = Field(None, alias="Blended Segment")
    oversized_lenses: Optional[SimplifiedBenefitItem] = Field(None, alias="Oversized Lenses")

class FrameBenefits(BaseModel):
    """Models frame benefits"""
    premier_frame: Optional[SimplifiedBenefitItem] = Field(None, alias="Premier Frame")
    designer_frame: Optional[SimplifiedBenefitItem] = Field(None, alias="Designer Frame")
    fashion_frame: Optional[SimplifiedBenefitItem] = Field(None, alias="Fashion Frame")
    frame_non_plan: Optional[SimplifiedBenefitItem] = Field(None, alias="Frame (Non Plan)")

class ContactLensBenefits(BaseModel):
    """Models contact lens benefits"""
    contact_lens_plan: Optional[SimplifiedBenefitItem] = Field(None, alias="Contact Lens (Plan)")
    contact_lens_non_plan: Optional[SimplifiedBenefitItem] = Field(None, alias="Contact Lens (Non Plan)")
    contact_lens_specialty_non_plan: Optional[SimplifiedBenefitItem] = Field(None, alias="Contact Lens - Specialty (Non Plan)")
    medically_necessary_non_plan: Optional[SimplifiedBenefitItem] = Field(None, alias="Medically Necessary - (Non Plan)")

class DavisTemplate(BaseModel):
    """Root model for the Davis Vision extraction result."""
    plan_name: Optional[str] = "Davis Vision" # Default based on template
    document_type: Optional[str] = "Vision Benefits" # Default based on template
    provider: Optional[str] = "Davis Vision" # Default based on template

    # Core benefit categories matching the raw data structure
    exam_benefits: Optional[ExamBenefits] = Field(None, alias="Exam")
    spectacle_lens_benefits: Optional[SpectacleLensBenefits] = Field(None, alias="SpectacleLens")
    spectacle_lens_options_benefits: Optional[SpectacleLensOptionsBenefits] = Field(None, alias="SpectacleLensOptions")
    frame_benefits: Optional[FrameBenefits] = Field(None, alias="Frame")
    contact_lens_benefits: Optional[ContactLensBenefits] = Field(None, alias="ContactLens")

    custom_id: Optional[str] = None # From template example
    error: Optional[str] = None # For reporting extraction errors

    class Config:
        allow_population_by_field_name = True # Allows using either field name or alias
        anystr_strip_whitespace = True
        
    def to_template_json(self) -> Dict[str, Any]:
        """
        Convert the model to a JSON dictionary with simplified benefit structure.

        Rules:
        - copay: null if not found in document (benefit not available)
        - copay: 0 if "No Copay" in document
        - allowance: only present for Frame/ContactLens "Non Plan" items
        - All other None values remain as null in JSON
        """
        # Get the model as a dictionary with aliases for field names, excluding None values
        raw_dict = self.dict(by_alias=True, exclude_none=True)

        import logging
        logger = logging.getLogger(__name__)

        # Debug logging of the raw dictionary structure
        logger.debug(f"Simplified template JSON: {json.dumps(raw_dict, indent=2, default=str)}")

        return raw_dict