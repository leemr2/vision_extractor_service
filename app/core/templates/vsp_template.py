"""
VSP Template - Defines the standard output structure for VSP vision insurance data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LensOption(BaseModel):
    """Individual lens option with pricing information."""
    code: str = Field(..., description="VSP lens option code")
    description: str = Field(..., description="Description of the lens option")
    single_cost: Optional[int] = Field(None, description="Cost for single vision lenses")
    multi_cost: Optional[int] = Field(None, description="Cost for multi-focal lenses")
    cost: Optional[int] = Field(None, description="General cost when not specific to lens type")

class LensSubcategory(BaseModel):
    """Subcategory of lens options."""
    name: str = Field(..., description="Name of the lens subcategory")
    options: List[LensOption] = Field(default_factory=list, description="Available options within this subcategory")

class LensCategory(BaseModel):
    """Category of lens options."""
    category: str = Field(..., description="Main category name")
    subcategories: List[LensSubcategory] = Field(default_factory=list, description="Subcategories of lens options")

class EligibilityInfo(BaseModel):
    """Information about what services are eligible under the plan."""
    exam: Optional[bool] = Field(None, description="Eye exam eligibility")
    lens: Optional[bool] = Field(None, description="Lens eligibility")
    frame: Optional[bool] = Field(None, description="Frame eligibility")
    contact_lens_exam: Optional[bool] = Field(None, description="Contact lens exam eligibility")
    contacts: Optional[bool] = Field(None, description="Contacts eligibility")

class FrameAllowance(BaseModel):
    """Frame allowance details."""
    promotion: Optional[float] = Field(None, description="Promotional allowance amount")
    altair_marchon: Optional[float] = Field(None, description="Allowance for Altair/Marchon frames")
    non_altair_marchon: Optional[float] = Field(None, description="Allowance for non-Altair/Marchon frames")

class PlanDetails(BaseModel):
    """Details about the VSP plan."""
    plan_name: Optional[str] = Field(None, description="Name of the VSP plan")
    copays: Optional[Dict[str, float]] = Field(None, description="Copay amounts")
    frame_allowance: Optional[FrameAllowance] = Field(None, description="Frame allowance details")

class Metadata(BaseModel):
    """Metadata about the document processing."""
    processingDate: Optional[str] = Field(None, description="Date and time of document processing")

class VSPTemplate(BaseModel):
    """Standard data structure for VSP vision benefits information."""
    
    document_type: Optional[str] = Field(None, description="Type of document")
    document_title: Optional[str] = Field(None, description="Title of the document")
    
    # Eligibility information
    eligibility_info: Optional[EligibilityInfo] = Field(None, description="Information about eligible services")
    
    # Plan details 
    plan_details: Optional[PlanDetails] = Field(None, description="Details about the VSP plan")
    
    # Lens categories and options
    lens_categories: Optional[List[LensCategory]] = Field(None, description="Categories of lens options")
    
    # Identification
    custom_id: Optional[str] = Field(None, description="Custom identification number")
    
    # Metadata
    metadata: Optional[Metadata] = Field(None, description="Processing metadata") 