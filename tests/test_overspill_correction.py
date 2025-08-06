"""
Tests for the progressive tier extraction overspill correction.
"""
import pytest
import asyncio
from app.core.extractors.eyemed_extractor import EyeMedExtractor

@pytest.fixture
def problematic_document_text():
    """Sample document text that could cause overspill in captured tier values."""
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
  Progressive - Standard                            $25 copay
  Progressive - Premium Tier 1                      $45 copay
  Progressive - Premium Tier 2                      $55 copay
  Progressive - Premium Tier 3                      $70 copay
  Progressive - Premium Tier 4                      $25 copay; 20% off retail price less $120 allowance

Lens Options
  Anti-Reflective Coating - Standard                $40 copay
  Anti-Reflective Coating - Premium Tier 1          $52 copay
  Anti-Reflective Coating - Premium Tier 2          $65 copay
  Anti-Reflective Coating - Premium Tier 3          $80 copay
  Polycarbonate - Standard                          $40
  Scratch Coating                                   $15
  Tint                                              $15
  UV Treatment                                      $15
  Other Add-ons                                     20% off retail
"""

@pytest.mark.asyncio
async def test_progressive_overspill_correction(problematic_document_text):
    """Test that the validation step corrects overspill in tier extraction."""
    extractor = EyeMedExtractor()
    
    # Initialize pattern manager
    extractor._register_patterns()
    
    # Extract progressive lens benefits
    progressive_benefits = await extractor.extract_progressive_lens_benefits(problematic_document_text)
    
    # Print the extracted values for debugging
    print("\nExtracted and validated progressive tier values:")
    for key, value in progressive_benefits.items():
        print(f"  {key}: {value}")
    
    # Verify standard progressive tier
    assert progressive_benefits["standard"] == "$25"
    
    # Verify each premium tier only has its own data
    assert progressive_benefits["premium_tier_1"] == "$45 copay"
    assert "Tier 2" not in progressive_benefits["premium_tier_1"]
    assert "Lens Options" not in progressive_benefits["premium_tier_1"]
    
    assert progressive_benefits["premium_tier_2"] == "$55 copay"
    assert "Tier 3" not in progressive_benefits["premium_tier_2"]
    assert "Lens Options" not in progressive_benefits["premium_tier_2"]
    
    assert progressive_benefits["premium_tier_3"] == "$70 copay"
    assert "Tier 4" not in progressive_benefits["premium_tier_3"]
    assert "Lens Options" not in progressive_benefits["premium_tier_3"]
    
    # Verify the complex pricing of tier 4 is correctly captured
    assert progressive_benefits["premium_tier_4"] == "$25 copay; 20% off retail price less $120 allowance"
    assert "Lens Options" not in progressive_benefits["premium_tier_4"]
    assert "Anti-Reflective" not in progressive_benefits["premium_tier_4"]

@pytest.mark.asyncio
async def test_full_extraction_with_validation(problematic_document_text):
    """Test that the full extraction process correctly handles tier validation."""
    extractor = EyeMedExtractor()
    
    # Extract all data
    result = await extractor.extract(problematic_document_text, "test_document.pdf")
    
    # Get progressive lens benefits
    progressive_lenses = result["vision_benefits"]["progressive_lenses"]
    
    # Print the extracted values for debugging
    print("\nFull extraction progressive tier values after validation:")
    for key, value in progressive_lenses.items():
        print(f"  {key}: {value}")
    
    # Validate the extracted values
    assert progressive_lenses["standard"] == "$25"
    assert progressive_lenses["premium_tier_1"] == "$45 copay"
    assert progressive_lenses["premium_tier_2"] == "$55 copay"
    assert progressive_lenses["premium_tier_3"] == "$70 copay"
    assert progressive_lenses["premium_tier_4"] == "$25 copay; 20% off retail price less $120 allowance"
    
    # Check that there's no content overlap between tiers
    for tier in range(1, 4):
        assert f"Tier {tier+1}" not in progressive_lenses[f"premium_tier_{tier}"]
    
    # Check that lens options are not included in any progressive tier
    for tier in range(1, 5):
        assert "Lens Options" not in progressive_lenses[f"premium_tier_{tier}"]
        assert "Anti-Reflective" not in progressive_lenses[f"premium_tier_{tier}"]

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_progressive_overspill_correction(problematic_document_text())) 