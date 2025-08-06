"""
Pydantic models for Spectera vision benefits extraction
"""
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class EligibilityCategory(BaseModel):
    """Simplified eligibility: just indicates if the category is currently available."""
    name: str
    is_eligible: bool = False # Default to False


class PatientInfo(BaseModel):
    """Patient information"""
    member_name: Optional[str] = Field(default="[REDACTED]")
    subscriber_id: Optional[str] = ""
    product_name: Optional[str] = ""


class EligibilityInfo(BaseModel):
    """Eligibility information for all service categories"""
    categories: List[EligibilityCategory] = []


class CostItem(BaseModel):
    """Base class for items with a patient responsibility"""
    provider_name: str
    patient_responsibility: str = ""
    # cost_value removed as per Option 1

class AgeCostItem(CostItem):
    """Cost item with age-specific information (e.g., Polycarbonate Adult)"""
    age_note: Optional[str] = None # Keep age_note if needed for specific cases like Polycarbonate Adult

# Removed ContactLensItem as it's not in the target output

class ProfessionalServices(BaseModel):
    """Professional services section"""
    exam: CostItem = Field(default_factory=lambda: CostItem(provider_name="Exam"))
    # maternity_exam removed - not in target output
    # selection_contact_lens_fit removed - not in target output
    # non_selection_contact_lens_fit removed - not in target output
    retinal_screening: CostItem = Field(default_factory=lambda: CostItem(provider_name="Retinal Screening Photography for Diabetics"))


class FrameItem(BaseModel): # Simplified based on Option 1
    provider_name: str
    patient_responsibility: str = ""
    # discount_percentage removed
    # allowance removed


class StandardLenses(BaseModel):
    """Standard lens options"""
    standard_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Standard Lenses"))
    blended_bifocals: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Blended Bifocals"))
    free_form_sv_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Free-form SV Lenses"))
    sv_aspheric_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / SV Aspheric Lenses"))
    mf_aspheric_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / MF Aspheric Lenses"))
    occupational_double_seg_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Occupational Double Seg Lenses"))


class ProgressiveLenses(BaseModel):
    """Progressive lens options"""
    non_formulary: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Non-Formulary"))
    tier_1: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Tier I"))
    tier_2: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Tier II"))
    tier_3: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Tier III"))
    tier_4: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Tier IV"))
    tier_5: CostItem = Field(default_factory=lambda: CostItem(provider_name="Lenses / Progressive Lenses: Tier V"))


class LensMaterials(BaseModel):
    """Lens material options"""
    high_index_standard: CostItem = Field(default_factory=lambda: CostItem(provider_name="High Index less than or equal to 1.66"))
    high_index_premium: CostItem = Field(default_factory=lambda: CostItem(provider_name="High Index 1.66 - 1.73"))
    high_index_ultra: CostItem = Field(default_factory=lambda: CostItem(provider_name="High Index, >= 1.74"))
    polycarbonate_child: CostItem = Field(default_factory=lambda: CostItem(provider_name="Polycarbonate Lenses"))
    polycarbonate_adult: AgeCostItem = Field(default_factory=lambda: AgeCostItem(provider_name="Polycarbonate Lenses", age_note="for Ages 19+"))


class AntiReflectiveCoating(BaseModel):
    """Anti-reflective coating options"""
    non_formulary: CostItem = Field(default_factory=lambda: CostItem(provider_name="Anti-Reflective Coating: Non-Formulary"))
    tier_1: CostItem = Field(default_factory=lambda: CostItem(provider_name="Anti-Reflective Coating: Tier I"))
    tier_2: CostItem = Field(default_factory=lambda: CostItem(provider_name="Anti-Reflective Coating: Tier II"))
    tier_3: CostItem = Field(default_factory=lambda: CostItem(provider_name="Anti-Reflective Coating: Tier III"))
    tier_4: CostItem = Field(default_factory=lambda: CostItem(provider_name="Anti-Reflective Coating: Tier IV"))


class LensOptions(BaseModel):
    """Lens enhancement options"""
    anti_reflective_coating: AntiReflectiveCoating = Field(default_factory=AntiReflectiveCoating)
    scratch_coating: CostItem = Field(default_factory=lambda: CostItem(provider_name="Scratch Coating"))
    one_year_scratch_warranty: CostItem = Field(default_factory=lambda: CostItem(provider_name="One Year Scratch Warranty"))
    edge_coating: CostItem = Field(default_factory=lambda: CostItem(provider_name="Edge Coating"))
    photochromic: CostItem = Field(default_factory=lambda: CostItem(provider_name="Photochromic"))
    polarized: CostItem = Field(default_factory=lambda: CostItem(provider_name="Polarized"))
    tint: CostItem = Field(default_factory=lambda: CostItem(provider_name="Tint"))
    uv_coating: CostItem = Field(default_factory=lambda: CostItem(provider_name="UV Coating"))
    polished_edges: CostItem = Field(default_factory=lambda: CostItem(provider_name="Polished Edges / Roll & Polish"))
    oversize_lenses: CostItem = Field(default_factory=lambda: CostItem(provider_name="Oversize Lenses"))
    chemistrie_clip: CostItem = Field(default_factory=lambda: CostItem(provider_name="Chemistrie Clip"))
    miscellaneous_lens_options: CostItem = Field(default_factory=lambda: CostItem(provider_name="Miscellaneous Lens Options"))


# Removed ContactLenses model as it's not in the target output

class VisionBenefits(BaseModel):
    """Vision benefits structure"""
    professional_services: ProfessionalServices = Field(default_factory=ProfessionalServices)
    frames: FrameItem = Field(default_factory=lambda: FrameItem(provider_name="Frame"))
    lenses: StandardLenses = Field(default_factory=StandardLenses)
    progressive_lenses: ProgressiveLenses = Field(default_factory=ProgressiveLenses)
    lens_materials: LensMaterials = Field(default_factory=LensMaterials)
    lens_options: LensOptions = Field(default_factory=LensOptions)


class SpecteraTemplate(BaseModel):
    """Main Spectera template"""
    provider: str = "Spectera"
    patient_info: PatientInfo = Field(default_factory=PatientInfo)
    eligibility_info: EligibilityInfo = Field(default_factory=EligibilityInfo)
    vision_benefits: VisionBenefits = Field(default_factory=VisionBenefits)
    # confidence removed - not in target output
    # confidence_scores removed - not in target output