"""
Test script to verify the pattern_base.py import is working after fixes.
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Test import of the pattern base classes
try:
    from app.core.pattern_library.base.pattern_base import (
        PatternGroup, ExtractionPattern, RegexPattern, 
        TablePattern, SectionPattern, FuzzyPattern,
        PatternType, ConfidenceLevel
    )
    print("✓ Successfully imported pattern_base classes")
    
    # Test creating a RegexPattern
    try:
        pattern = RegexPattern(
            name="test_pattern",
            description="Test pattern for eligibility",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.test_eligible",
            confidence=ConfidenceLevel.HIGH,
            patterns=[r"Test\s+Yes\s+"]
        )
        print("✓ Successfully created a RegexPattern instance")
        
        # Test the compiled_patterns attribute
        print(f"✓ Pattern has {len(pattern.compiled_patterns)} compiled pattern(s)")
        
        # Test the extract method with a matching text
        sample_text = "Test Yes is found in the text"
        result = pattern.extract(sample_text)
        if result:
            print(f"✓ Extract method returned: {result}")
        else:
            print("✗ Extract method didn't match pattern")
            
    except Exception as e:
        print(f"✗ Error creating RegexPattern: {e}")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}") 