"""
Tests for progressive lens pattern extraction.
"""
import pytest
from app.core.pattern_library.providers.eyemed.progressive import extract_premium_tier_complex

def test_extract_premium_tier_complex():
    """Test the extract_premium_tier_complex function directly."""
    # Sample document text with complex pricing for tier 4
    document_text = """
    Progressive Lenses
      Progressive - Standard                            $85 copay
      Progressive - Premium Tier 1                      $105 copay
      Progressive - Premium Tier 2                      $115 copay
      Progressive - Premium Tier 3                      $130 copay
      Progressive - Premium Tier 4                      $85 copay; 20% off retail price less $120 allowance
    """
    
    # Extract tier 4 complex pricing
    tier4_pricing = extract_premium_tier_complex(document_text, 4)
    print(f"Extracted Tier 4 pricing: {tier4_pricing}")
    
    # Assertion
    assert tier4_pricing == "$85 copay; 20% off retail price less $120 allowance"
    
    # Test extracting other tiers
    tier1_pricing = extract_premium_tier_complex(document_text, 1)
    assert tier1_pricing is None or tier1_pricing == "$105 copay"
    
    # Test with a different format of complex pricing
    document_text2 = """
    Progressive Lenses
      Progressive - Standard                            $85 copay
      Progressive - Premium Tier 1                      $105 copay; 15% off retail price less $90 allowance
      Progressive - Premium Tier 2                      $115 copay
      Progressive - Premium Tier 3                      $130 copay
      Progressive - Premium Tier 4                      $85 copay; 20% off balance over $120 allowance
    """
    
    tier1_complex = extract_premium_tier_complex(document_text2, 1)
    print(f"Extracted Tier 1 complex pricing: {tier1_complex}")
    assert tier1_complex == "$105 copay; 15% off retail price less $90 allowance"
    
    tier4_alternative = extract_premium_tier_complex(document_text2, 4)
    print(f"Extracted Tier 4 alternative pricing: {tier4_alternative}")
    assert tier4_alternative == "$85 copay; 20% off balance over $120 allowance"

if __name__ == "__main__":
    # Run the test directly
    test_extract_premium_tier_complex() 