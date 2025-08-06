"""
Pydantic models for Davis Vision benefit extraction results.
"""
from typing import Dict, Optional, Union, List, Any
from pydantic import BaseModel, Field
import json

# Using Union[int, float, str, None] for flexibility as initial extraction might yield strings like "Included"
# before final processing converts them to numbers or None. Using Optional for fields that might not be present.
BenefitValue = Union[int, float, str, None]

class BenefitItem(BaseModel):
    """Base model for individual benefit items"""
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
    routine_exam: Optional[BenefitItem] = Field(None, alias="Routine Exam")

class SpectacleLensBenefits(BaseModel):
    """Models spectacle lens benefits"""
    bifocal_spectacle_lens: Optional[BenefitItem] = Field(None, alias="Bifocal - Spectacle Lens (Plan)")
    single_vision_spectacle_lens: Optional[BenefitItem] = Field(None, alias="Single Vision - Spectacle Lens (Plan)")
    trifocal_spectacle_lens: Optional[BenefitItem] = Field(None, alias="Trifocal - Spectacle Lens (Plan)")
    single_vision_lenticular_myodisc: Optional[BenefitItem] = Field(None, alias="Single Vision - Lenticular Myodisc")

class SpectacleLensOptionsBenefits(BaseModel):
    """Models spectacle lens option benefits"""
    # Anti-reflective coatings
    ar_coating_standard: Optional[BenefitItem] = Field(None, alias="AR Coating Standard")
    ar_coating_premium: Optional[BenefitItem] = Field(None, alias="AR Coating Premium")
    ar_coating_ultra: Optional[BenefitItem] = Field(None, alias="AR Coating Ultra")
    ar_coating_ultimate: Optional[BenefitItem] = Field(None, alias="AR Coating Ultimate")
    
    # Progressive lenses
    progressive_standard: Optional[BenefitItem] = Field(None, alias="Progressive Standard")
    progressive_premium: Optional[BenefitItem] = Field(None, alias="Progressive Premium")
    progressive_ultra: Optional[BenefitItem] = Field(None, alias="Progressive Ultra")
    progressive_ultimate: Optional[BenefitItem] = Field(None, alias="Progressive Ultimate")
    
    # Polycarbonate options
    polycarbonate_single_vision: Optional[BenefitItem] = Field(None, alias="Polycarbonate - Single Vision")
    polycarbonate_provided: Optional[BenefitItem] = Field(None, alias="Polycarbonate Provided")
    hd_polycarbonate_single_vision: Optional[BenefitItem] = Field(None, alias="HD Polycarbonate - Single Vision")
    hd_polycarbonate_multifocal: Optional[BenefitItem] = Field(None, alias="HD Polycarbonate - Multifocal")
    
    # High index lenses
    high_index_167_single_vision: Optional[BenefitItem] = Field(None, alias="HighIndex 1.67 - Single Vision")
    high_index_174_single_vision: Optional[BenefitItem] = Field(None, alias="HighIndex 1.74 - Single Vision")
    high_index_174_multifocal: Optional[BenefitItem] = Field(None, alias="HighIndex 1.74 - Multifocal")
    
    # Tints and photochromic options
    tint: Optional[BenefitItem] = Field(None, alias="Tint")
    tint_solid: Optional[BenefitItem] = Field(None, alias="Tint Solid")
    tint_gradient: Optional[BenefitItem] = Field(None, alias="Tint Gradient")
    tint_gg: Optional[BenefitItem] = Field(None, alias="Tint GG")
    single_vision_tint_photogrey: Optional[BenefitItem] = Field(None, alias="Single Vision - Tint Photogrey")
    multivision_tint_photogrey: Optional[BenefitItem] = Field(None, alias="Multivision - Tint Photogrey")
    single_vision_tint_plastic_photosensitive: Optional[BenefitItem] = Field(None, alias="Single Vision - Tint Plastic - Photosensitive")
    multivision_tint_plastic_photosensitive: Optional[BenefitItem] = Field(None, alias="Multivision - Tint Plastic - Photosensitive")
    
    # Other lens options
    blue_light_filtering_ebs: Optional[BenefitItem] = Field(None, alias="Blue Light Filtering - EBS")
    polarized: Optional[BenefitItem] = Field(None, alias="Polarized")
    intermediate_vision: Optional[BenefitItem] = Field(None, alias="Intermediate Vision")
    ultraviolet_coating: Optional[BenefitItem] = Field(None, alias="Ultraviolet Coating")
    scratch_resistant_coating: Optional[BenefitItem] = Field(None, alias="Scratch Resistant Coating")
    scratch_resistant_coating_premium: Optional[BenefitItem] = Field(None, alias="Scratch Resistant Coating Premium")
    single_vision_scratch_resistant_coating_protection: Optional[BenefitItem] = Field(None, alias="Single Vision - Scratch Resistant Coating Protection")
    multivision_scratch_resistant_coating_protection: Optional[BenefitItem] = Field(None, alias="Multivision - Scratch Resistant Coating Protection")
    mirror_solid_single_double_gradient: Optional[BenefitItem] = Field(None, alias="Mirror - Solid, Single & Double Gradient")
    
    # Edge and special processing options
    edge_polish: Optional[BenefitItem] = Field(None, alias="Edge Polish")
    high_luster_edge_polish: Optional[BenefitItem] = Field(None, alias="High Luster Edge Polish")
    roll_polish: Optional[BenefitItem] = Field(None, alias="Roll Polish")
    roll_edge: Optional[BenefitItem] = Field(None, alias="Roll Edge")
    rimless_drill: Optional[BenefitItem] = Field(None, alias="Rimless Drill")
    slab_off: Optional[BenefitItem] = Field(None, alias="Slab Off")
    blended_segment: Optional[BenefitItem] = Field(None, alias="Blended Segment")
    oversized_lenses: Optional[BenefitItem] = Field(None, alias="Oversized Lenses")

class FrameBenefits(BaseModel):
    """Models frame benefits"""
    premier_frame: Optional[BenefitItem] = Field(None, alias="Premier Frame")
    designer_frame: Optional[BenefitItem] = Field(None, alias="Designer Frame")
    fashion_frame: Optional[BenefitItem] = Field(None, alias="Fashion Frame")
    frame_non_plan: Optional[BenefitItem] = Field(None, alias="Frame (Non Plan)")

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
    
    custom_id: Optional[str] = None # From template example
    error: Optional[str] = None # For reporting extraction errors

    class Config:
        allow_population_by_field_name = True # Allows using either field name or alias
        anystr_strip_whitespace = True
        
    def to_template_json(self) -> Dict[str, Any]:
        """
        Convert the model to a JSON dictionary that exactly matches the expected template format.
        Replaces all None values with the string "none" to ensure the calculator always has values.
        """
        # Get the model as a dictionary with aliases for field names
        raw_dict = self.dict(by_alias=True, exclude_none=False)
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Debug logging of the raw dictionary structure before conversion
        logger.debug(f"Raw dictionary before None replacement: {json.dumps(raw_dict, indent=2, default=str)}")
        
        # Recursive function to replace None values with "none" string
        def replace_none(obj):
            if isinstance(obj, dict):
                return {k: replace_none(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_none(item) for item in obj]
            elif obj is None:
                return "none"
            return obj
        
        # Apply the replacement and return the formatted dictionary
        result = replace_none(raw_dict)
        
        # Debug logging of the final dictionary after conversion
        logger.debug(f"Final dictionary after None replacement: {json.dumps(result, indent=2, default=str)}")
        
        return result