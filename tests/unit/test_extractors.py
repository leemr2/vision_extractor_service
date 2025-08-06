"""
Unit tests for insurance provider extractors
"""
import pytest
import asyncio
from typing import Dict, Any

from app.core.extractors.vsp_extractor import VSPExtractor
from app.core.extractors.eyemed_extractor import EyeMedExtractor
from app.core.extractors.davis_extractor import DavisExtractor
from app.core.extractors.spectera_extractor import SpecteraExtractor
from app.core.extractors.versant_tabular_extractor import VersantTabularExtractor, SuperiorExtractor, VersantExtractor


def test_vsp_extractor():
    """Test VSP extractor with sample data"""
    # Arrange
    extractor = VSPExtractor()
    sample_data = {
        "provider": "VSP",
        "sections": [
            {
                "title": "LENSES",
                "content": [
                    {
                        "text": "Single Vision",
                        "annotations": [
                            {
                                "category": "lens_types",
                                "term": "single_vision",
                                "normalized_term": "single_vision"
                            }
                        ]
                    },
                    {
                        "text": "Covered in full",
                        "annotations": [
                            {
                                "category": "coverage_terms",
                                "term": "covered",
                                "normalized_term": "covered_in_full"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    # Act
    result = extractor.extract(sample_data)
    
    # Assert
    assert "document_type" in result
    assert "lens_categories" in result
    assert result["document_type"] == "vsp_benefits"


@pytest.mark.asyncio
async def test_eyemed_extractor():
    """Test EyeMed extractor with sample data"""
    # Arrange
    extractor = EyeMedExtractor()
    sample_text = """
    Member ID: ABC123456
    Member: John Doe
    Network: Insight
    Group: Group123
    Benefit Level: Enhanced
    
    EYE EXAM: Eligible: Yes
    Eligible as of: 01/01/2023
    Frequency: Once every 12 months
    Eye Exam Copay: $10
    Retinal Imaging Cost: Up to $39
    
    FRAMES: Eligible: Yes
    Eligible as of: 01/01/2023
    Frequency: Once every 24 months
    Frame Allowance: $150
    Frame Benefits: $150 allowance, 20% off balance over allowance
    
    LENSES: Eligible: Yes
    Eligible as of: 01/01/2023
    Frequency: Once every 12 months
    Single Vision: $10
    Bifocal: $10
    Trifocal: $10
    Lenticular: $10
    
    PROGRESSIVE LENSES:
    Standard Progressive: $75
    Premium Progressive - Tier 1: $95
    Premium Progressive - Tier 2: $105
    Premium Progressive - Tier 3: $120
    Premium Progressive - Tier 4: $75 copay + 80% of charge less $120 allowance
    
    LENS OPTIONS:
    UV Treatment: $15
    Tint: $15
    Standard Plastic Scratch Coating: $15
    Standard Polycarbonate: $40
    Standard Anti-Reflective Coating: $45
    Premium Anti-Reflective Coating - Tier 1: $57
    Premium Anti-Reflective Coating - Tier 2: $68
    Premium Anti-Reflective Coating - Tier 3: $85
    Photochromic/Transitions: $75
    
    CONTACT LENSES: Eligible: Yes
    Eligible as of: 01/01/2023
    Frequency: Once every 12 months
    Standard Contact Lens Fit: Up to $40
    Premium Contact Lens Fit: 10% off retail price
    Conventional Contacts: $150 allowance, 15% off balance over allowance
    Disposable Contacts: $150 allowance
    Medically Necessary Contacts: Covered in Full
    
    Service Restrictions: None
    """
    sample_path = "test_eyemed.pdf"
    
    # Act
    result = await extractor.extract(sample_text, sample_path)
    
    # Assert
    assert result["metadata"]["provider"] == "EyeMed"
    assert result["metadata"]["confidence"] > 0.7
    
    data = result["data"]
    
    # Check patient info
    assert data["patient_info"]["member_id"] == "ABC123456"
    assert data["patient_info"]["member_name"] == "John Doe"
    assert data["patient_info"]["network"] == "Insight"
    assert data["patient_info"]["group"] == "Group123"
    
    # Check eligibility info
    assert data["eligibility_info"]["exam"]["is_eligible"] == True
    assert data["eligibility_info"]["exam"]["eligible_as_of"] == "01/01/2023"
    assert data["eligibility_info"]["exam"]["frequency"] == "Once every 12 months"
    
    assert data["eligibility_info"]["frame"]["is_eligible"] == True
    assert data["eligibility_info"]["frame"]["frequency"] == "Once every 24 months"
    
    # Check vision benefits
    assert data["vision_benefits"]["exam_services"]["exam"]["cost_value"] == "$10"
    assert data["vision_benefits"]["exam_services"]["retinal_imaging"]["cost_value"] == "Up to $39"
    
    # Check frame details
    assert data["vision_benefits"]["frame"]["allowance"] == "$150"
    assert data["vision_benefits"]["frame"]["discount_percentage"] == "20%"
    
    # Check lens details
    assert data["vision_benefits"]["lenses"]["single_vision"]["cost_value"] == "$10"
    assert data["vision_benefits"]["lenses"]["bifocal"]["cost_value"] == "$10"
    assert data["vision_benefits"]["lenses"]["trifocal"]["cost_value"] == "$10"
    assert data["vision_benefits"]["lenses"]["lenticular"]["cost_value"] == "$10"
    
    # Check progressive lenses
    assert data["vision_benefits"]["progressive_lenses"]["standard"]["cost_value"] == "$75"
    assert data["vision_benefits"]["progressive_lenses"]["premium_tier_1"]["cost_value"] == "$95"
    
    # Check lens options
    assert data["vision_benefits"]["lens_options"]["uv_treatment"]["cost_value"] == "$15"
    assert data["vision_benefits"]["lens_options"]["tint"]["cost_value"] == "$15"
    assert data["vision_benefits"]["lens_options"]["scratch_coating"]["cost_value"] == "$15"
    assert data["vision_benefits"]["lens_options"]["anti_reflective_coating"]["standard"]["cost_value"] == "$45"
    
    # Check contact lenses
    assert data["vision_benefits"]["contact_lens_fit"]["standard"]["cost_value"] == "$40"
    assert data["vision_benefits"]["contact_lenses"]["conventional"]["allowance"] == "$150"
    assert data["vision_benefits"]["contact_lenses"]["conventional"]["discount_percentage"] == "15%"
    assert data["vision_benefits"]["contact_lenses"]["disposable"]["allowance"] == "$150"
    assert data["vision_benefits"]["contact_lenses"]["medically_necessary"]["cost_value"] == "Paid in Full"


def test_davis_extractor():
    """Test Davis Vision extractor with sample data"""
    # Arrange
    extractor = DavisExtractor()
    sample_data = {
        "provider": "Davis Vision",
        "sections": []
    }
    
    # Act
    result = extractor.extract(sample_data)
    
    # Assert
    assert "document_type" in result
    assert result["document_type"] == "davis_benefits"


def test_spectera_extractor():
    """Test Spectera extractor with sample data"""
    # Arrange
    extractor = SpecteraExtractor()
    sample_data = {
        "provider": "Spectera",
        "sections": []
    }
    
    # Act
    result = extractor.extract(sample_data)
    
    # Assert
    assert "document_type" in result
    assert result["document_type"] == "spectera_benefits"


def test_superior_extractor():
    """Test Superior Vision extractor with sample data"""
    # Arrange
    extractor = SuperiorExtractor()
    sample_data = {
        "provider": "Superior Vision",
        "sections": []
    }
    
    # Act
    result = extractor.extract(sample_data)
    
    # Assert
    assert "document_type" in result
    assert result["document_type"] == "superior_benefits"


def test_versant_extractor():
    """Test Versant Health extractor with sample data"""
    # Arrange
    extractor = VersantExtractor()
    
    # Act
    # Simulate extraction with the same test document that works with Davis tabular extractor
    result = extractor.extract(sample_data)
    
    # Assert
    assert "provider" in result
    assert result["provider"] == "Versant Health" 