"""
Standardized data models for benefits
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any


class PatientInfo(BaseModel):
    """
    Patient information model
    """
    id: Optional[str] = None
    id_number: Optional[str] = None
    patient_name: Optional[str] = None
    group_number: Optional[str] = None


class LensOption(BaseModel):
    """
    Lens option model (e.g., anti-reflective coating, polycarbonate)
    """
    code: Optional[str] = None
    description: str
    coverage_type: str
    single_cost: Union[float, int, None] = None
    multi_cost: Union[float, int, None] = None
    discount_percentage: Optional[int] = None
    allowance: Optional[float] = None
    notes: Optional[str] = None


class LensSubcategory(BaseModel):
    """
    Lens subcategory model (e.g., polycarbonate, anti-reflective)
    """
    name: str
    options: List[LensOption]
    notes: Optional[str] = None


class LensCategory(BaseModel):
    """
    Lens category model (e.g., frames, lenses, contacts)
    """
    category: str
    subcategories: List[LensSubcategory]
    frequency: Optional[str] = None
    notes: Optional[str] = None


class VisionBenefits(BaseModel):
    """
    Complete vision benefits model
    """
    document_type: str
    insurance_provider: str
    patient_info: Optional[PatientInfo] = None
    effective_date: Optional[str] = None
    expiration_date: Optional[str] = None
    lens_categories: List[LensCategory]
    frequencies: Optional[Dict[str, str]] = None
    copays: Optional[Dict[str, Union[float, int]]] = None
    raw_extracted_text: Optional[str] = None


class ExtractionResponse(BaseModel):
    """
    API response model for extraction endpoint
    """
    document_type: str
    insurance_provider: str
    patient_info: Optional[PatientInfo] = None
    lens_categories: List[LensCategory]
    frequencies: Optional[Dict[str, str]] = None
    copays: Optional[Dict[str, Union[float, int]]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "document_type": "vsp_lens_enhancement",
                "insurance_provider": "VSP",
                "patient_info": {
                    "id_number": "12345678",
                    "patient_name": "[REDACTED]"
                },
                "lens_categories": [
                    {
                        "category": "LENSES",
                        "subcategories": [
                            {
                                "name": "Polycarbonate",
                                "options": [
                                    {
                                        "code": "AD",
                                        "description": "Polycarbonate",
                                        "coverage_type": "covered",
                                        "single_cost": 0,
                                        "multi_cost": 0
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "frequencies": {
                    "EXAM": "12 months",
                    "FRAMES": "24 months",
                    "LENSES": "12 months"
                },
                "copays": {
                    "EXAM": 10,
                    "MATERIALS": 25
                }
            }
        } 