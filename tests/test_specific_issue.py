"""
Tests for specific tier validation issues.
"""
import pytest
from app.core.extractors.eyemed_extractor import EyeMedExtractor

def test_validate_progressive_tiers_cleanup():
    """Test the _validate_progressive_tiers method directly with problematic data."""
    extractor = EyeMedExtractor()
    
    # Simulate extracted data with individual problems in each tier
    problematic_data = {
        "standard": "$25",
        "premium_tier_1": "$45 copay Progressive - Premium", # Simple copay only
        "premium_tier_2": "$55 copay Progressive - Premium Tier 3", # Has tier 3 content
        "premium_tier_3": "$70 copay Progressive - Premium Tier 4", # Has tier 4 content
        "premium_tier_4": "$25 copay; 20% off retail price less $120 allowance Lens Options" # Has lens options content
    }
    
    # Run the validation function
    cleaned_data = extractor._validate_progressive_tiers(problematic_data)
    
    # Print results for debugging
    print("\nValidation results:")
    for key, value in cleaned_data.items():
        print(f"  {key}: {value}")
    
    # Assert that each tier now only contains its own data
    assert cleaned_data["standard"] == "$25"
    assert cleaned_data["premium_tier_1"] == "$45 copay" 
    assert cleaned_data["premium_tier_2"] == "$55 copay"
    assert cleaned_data["premium_tier_3"] == "$70 copay"
    assert cleaned_data["premium_tier_4"] == "$25 copay; 20% off retail price less $120 allowance"

def test_double_validation_bug():
    """Test for a possible bug where validation gets applied twice and causes issues."""
    extractor = EyeMedExtractor()
    
    # Create data that's already clean
    clean_data = {
        "standard": "$25",
        "premium_tier_1": "$45 copay",
        "premium_tier_2": "$55 copay",
        "premium_tier_3": "$70 copay",
        "premium_tier_4": "$25 copay; 20% off retail price less $120 allowance"
    }
    
    # Run validation to ensure it doesn't corrupt already clean data
    validated_clean = extractor._validate_progressive_tiers(clean_data)
    
    # Print results for debugging
    print("\nValidation of already clean data:")
    for key, value in validated_clean.items():
        print(f"  {key}: {value}")
    
    # Assert that the data remains unchanged
    assert validated_clean["standard"] == "$25"
    assert validated_clean["premium_tier_1"] == "$45 copay"
    assert validated_clean["premium_tier_2"] == "$55 copay"
    assert validated_clean["premium_tier_3"] == "$70 copay"
    assert validated_clean["premium_tier_4"] == "$25 copay; 20% off retail price less $120 allowance"
    
    # Test running validation twice on problematic data
    problematic_data = {
        "standard": "$25",
        "premium_tier_1": "$45 copay Progressive - Premium Tier 2 $55 copay Progressive - Premium Tier 3 $70 copay Progressive - Premium Tier 4 $25 copay; 20% off retail price less $120 allowance Lens Options",
        "premium_tier_2": "$55 copay Progressive - Premium Tier 3 $70 copay Progressive - Premium Tier 4 $25 copay; 20% off retail price less $120 allowance Lens Options",
        "premium_tier_3": "$70 copay Progressive - Premium Tier 4 $25 copay; 20% off retail price less $120 allowance Lens Options",
        "premium_tier_4": "$25 copay; 20% off retail price less $120 allowance"
    }
    
    # Run validation once
    validated_once = extractor._validate_progressive_tiers(problematic_data)
    
    # Run validation again on the already validated data
    validated_twice = extractor._validate_progressive_tiers(validated_once)
    
    # Print results for debugging
    print("\nValidation applied twice to problematic data:")
    for key, value in validated_twice.items():
        print(f"  {key}: {value}")
    
    # Assert that the data is still correct after double validation
    assert validated_twice["standard"] == "$25"
    assert validated_twice["premium_tier_1"] == "$45 copay"
    assert validated_twice["premium_tier_2"] == "$55 copay"
    assert validated_twice["premium_tier_3"] == "$70 copay"
    assert validated_twice["premium_tier_4"] == "$25 copay; 20% off retail price less $120 allowance"

if __name__ == "__main__":
    # Run the tests directly
    test_validate_progressive_tiers_cleanup()
    test_double_validation_bug() 