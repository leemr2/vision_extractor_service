"""
Tests for the entire extraction pipeline with complex progressive lens pricing.
"""
import pytest
import asyncio
from app.core.extractors.eyemed_extractor import EyeMedExtractor

@pytest.fixture
def complex_pricing_document():
    """Sample document text with complex pricing for multiple tiers."""
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
  Progressive - Standard                            $85 copay
  Progressive - Premium Tier 1                      $105 copay; 15% off retail price less $90 allowance
  Progressive - Premium Tier 2                      $115 copay; 15% off retail price less $90 allowance
  Progressive - Premium Tier 3                      $130 copay; 15% off retail price less $90 allowance
  Progressive - Premium Tier 4                      $85 copay; 20% off retail price less $120 allowance

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

@pytest.mark.asyncio
async def test_full_extraction_with_complex_pricing(complex_pricing_document):
    """Test the full extraction pipeline with complex pricing for multiple tiers."""
    extractor = EyeMedExtractor()
    
    # Extract all data
    result = await extractor.extract(complex_pricing_document, "test_document.pdf")
    
    # Get progressive lens benefits
    progressive_lenses = result["vision_benefits"]["progressive_lenses"]
    
    # Print the extracted values for debugging
    print("\nExtracted Progressive Lens Benefits:")
    for key, value in progressive_lenses.items():
        print(f"  {key}: {value}")
    
    # Verify the extracted values
    assert progressive_lenses["standard"] == "$85"
    assert "15% off retail price less $90 allowance" in progressive_lenses["premium_tier_1"]
    assert "15% off retail price less $90 allowance" in progressive_lenses["premium_tier_2"]
    assert "15% off retail price less $90 allowance" in progressive_lenses["premium_tier_3"]
    assert "20% off retail price less $120 allowance" in progressive_lenses["premium_tier_4"]
    
    # Check confidence score
    assert result["confidence_score"] > 0.8, "Confidence score should be high for this extraction"
    print(f"\nOverall confidence score: {result['confidence_score']}")

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_full_extraction_with_complex_pricing(complex_pricing_document())) 