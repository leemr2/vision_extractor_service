"""
Tests for the EyeMed extractor with focus on progressive lens pricing.
"""
import pytest
import os
import asyncio
from app.core.extractors.eyemed_extractor import EyeMedExtractor

@pytest.fixture
def sample_document_text():
    """Sample document text fixture with complex progressive pricing for testing."""
    return """
Vision Care Services                                In-Network Member Cost
Exam With Dilation as Necessary                     $10 copay
Retinal Imaging                                     Up to $39

Frames                                              $0 copay; 20% off balance over $230

Standard Plastic Lenses
  Single Vision                                     $20 copay
  Bifocal                                           $20 copay
  Trifocal                                          $20 copay
  Lenticular                                        20% off retail

Progressive Lenses
  Progressive - Standard                            $85
  Progressive - Premium Tier 1                      $110 copay
  Progressive - Premium Tier 2                      $120 copay
  Progressive - Premium Tier 3                      $135 copay
  Progressive - Premium Tier 4                      $85 copay; 20% off retail price less $80 allowance

Contact Lens Fit and Follow-up
  Standard                                          Up to $0
  Premium                                           10% off retail price

Lens Options:
  Anti-Reflective Coating - Standard                $45
  Anti-Reflective Coating - Premium Tier 1          $57
  Anti-Reflective Coating - Premium Tier 2          $68 
  Anti-Reflective Coating - Premium Tier 3          20% off retail price
  Polycarbonate                                     $40
  Scratch Coating                                   $15
  Tint                                              $15
  UV Treatment                                      $15
  Other Add-ons                                     20% off retail
"""

class TestEyeMedExtractor:
    """Test the EyeMed extractor functionality."""

    @pytest.mark.asyncio
    async def test_extract_progressive_lens_benefits(self, sample_document_text):
        """Test that complex progressive lens pricing is extracted correctly."""
        extractor = EyeMedExtractor()
        
        # Initialize pattern manager
        extractor._register_patterns()
        
        # Extract progressive lens benefits
        progressive_benefits = await extractor.extract_progressive_lens_benefits(sample_document_text)
        
        # Check standard progressive tier
        assert progressive_benefits["standard"] == "$85"
        
        # Check premium tiers
        assert "premium_tier_1" in progressive_benefits
        assert progressive_benefits["premium_tier_1"] == "$110 copay"
        
        assert "premium_tier_2" in progressive_benefits
        assert progressive_benefits["premium_tier_2"] == "$120 copay"
        
        assert "premium_tier_3" in progressive_benefits
        assert progressive_benefits["premium_tier_3"] == "$135 copay"
        
        assert "premium_tier_4" in progressive_benefits
        assert "copay; 20% off retail price less $80" in progressive_benefits["premium_tier_4"]
        
        print("Progressive Tier 4 value:", progressive_benefits["premium_tier_4"])
        
    @pytest.mark.asyncio
    async def test_full_extraction(self, sample_document_text):
        """Test the full extraction process with a focus on progressive lens benefits."""
        extractor = EyeMedExtractor()
        
        # Extract all data
        result = await extractor.extract(sample_document_text, "test_document.pdf")
        
        # Check progressive lens benefits in the full extraction
        assert "progressive_lenses" in result["vision_benefits"]
        progressive_lenses = result["vision_benefits"]["progressive_lenses"]
        
        assert progressive_lenses["standard"] == "$85"
        assert progressive_lenses["premium_tier_1"] == "$110 copay"
        assert progressive_lenses["premium_tier_2"] == "$120 copay"
        assert progressive_lenses["premium_tier_3"] == "$135 copay"
        assert "copay; 20% off retail price less $80" in progressive_lenses["premium_tier_4"]
        
        print("Full extraction Tier 4 value:", progressive_lenses["premium_tier_4"])

if __name__ == "__main__":
    pytest.main() 