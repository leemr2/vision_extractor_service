"""
Utility functions for dynamically generating extraction patterns
"""
from typing import List, Dict, Any, Optional
import re
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup
)

def generate_cost_patterns(
    field_name: str,
    term_variations: List[str],
    target_field: str,
    include_copay: bool = True,
    include_discount: bool = True,
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
) -> RegexPattern:
    """
    Generate regex patterns for cost extraction based on term variations
    
    Args:
        field_name: Name of the field (for pattern naming)
        term_variations: List of term variations to match
        target_field: Target field path in the output model
        include_copay: Whether to include copay patterns
        include_discount: Whether to include discount patterns
        confidence: Confidence level for the pattern
    
    Returns:
        RegexPattern with dynamically generated patterns
    """
    patterns = []
    
    # Escape any regex special characters in the terms
    escaped_terms = [re.escape(term) for term in term_variations]
    
    # Join terms with OR operator
    terms_pattern = "(?:" + "|".join(escaped_terms) + ")"
    
    # Generate copay patterns
    if include_copay:
        patterns.extend([
            f"{terms_pattern}(?:[^$]*?)(?:Copay|Cost)?:?\\s*(\\$\\d+(?:\\.\\d+)?)",
            f"{terms_pattern}\\s+(\\$\\d+(?:\\.\\d+)?\\s+copay)",
            f"{terms_pattern}:?\\s*(\\$\\d+(?:\\.\\d+)?)"
        ])
    
    # Generate discount patterns
    if include_discount:
        patterns.extend([
            f"{terms_pattern}(?:[^%]*?)((?:\\d+)%\\s+off\\s+retail(?:\\s+price)?)",
            f"{terms_pattern}:?\\s*((?:\\d+)%\\s+discount)"
        ])
    
    # Generate allowance patterns
    patterns.extend([
        f"{terms_pattern}(?:[^$]*?)(?:allowance|Allowance):?\\s*(\\$\\d+(?:\\.\\d+)?)",
        f"{terms_pattern}(?:[^$]*?)(\\$\\d+(?:\\.\\d+)?\\s+allowance)"
    ])
    
    # Generate complex patterns with both copay and discount
    patterns.extend([
        f"{terms_pattern}(?:[^$]*?)(\\$\\d+(?:\\.\\d+)?\\s*(?:copay)?(?:;\\s+)?(?:\\d+)%\\s+off\\s+retail(?:\\s+price)?(?:\\s+less\\s+\\$\\d+(?:\\.\\d+)?\\s+allowance)?)"
    ])
    
    return RegexPattern(
        name=f"{field_name}_generated_pattern",
        description=f"Dynamically generated pattern for {field_name}",
        pattern_type=PatternType.EXACT,
        target_field=target_field,
        confidence=confidence,
        patterns=patterns
    )

def create_pattern_group_from_variations(
    group_name: str,
    term_variations: List[str],
    target_field: str,
    include_alternatives: bool = True
) -> PatternGroup:
    """
    Create a pattern group with multiple patterns based on term variations
    
    Args:
        group_name: Name for the pattern group
        term_variations: List of term variations to match
        target_field: Target field path in the output model
        include_alternatives: Whether to include alternative pattern formats
        
    Returns:
        PatternGroup with multiple patterns
    """
    patterns = []
    
    # Add the main cost pattern
    patterns.append(
        generate_cost_patterns(
            field_name=group_name,
            term_variations=term_variations,
            target_field=target_field,
            confidence=ConfidenceLevel.HIGH
        )
    )
    
    # Add table pattern for tabular formats
    if include_alternatives:
        for term in term_variations:
            # Add table patterns for common column headers
            for column in ["Copay", "Cost", "In-Network", "Member Pays"]:
                patterns.append(
                    TablePattern(
                        name=f"{group_name}_table_{column.lower()}",
                        description=f"Table pattern for {group_name} in {column} column",
                        pattern_type=PatternType.TABLE,
                        target_field=target_field,
                        confidence=ConfidenceLevel.MEDIUM,
                        row_header=term,
                        column_header=column
                    )
                )
    
    return PatternGroup(
        name=group_name,
        patterns=patterns
    )

def get_term_variations_from_dictionary(category: str, term: str, providers: List[str] = None) -> List[str]:
    """
    Get term variations from the term dictionary
    
    This is a placeholder function. In a real implementation, this would
    interface with the actual term dictionary.
    
    Args:
        category: Term category (e.g., 'lens_types', 'lens_treatments')
        term: Standard term to look up
        providers: List of providers to include specific variations for
        
    Returns:
        List of term variations
    """
    # Example hardcoded variations for common terms
    # In a real implementation, this would query the term dictionary
    variations = {
        "exam": [
            "Eye Exam", "Vision Exam", "Routine Exam", "Exam Services",
            "Comprehensive Exam", "Eye Examination"
        ],
        "retinal_imaging": [
            "Retinal Imaging", "Retinal Screening", "Digital Retinal Imaging",
            "Retinal Photography"
        ],
        "frames": [
            "Frame", "Frames", "Eyeglass Frames", "Frame Allowance",
            "Frame Benefit"
        ],
        "single_vision": [
            "Single Vision", "Single Vision Lenses", "SV Lenses"
        ],
        "bifocal": [
            "Bifocal", "Bifocal Lenses", "Bifocals"
        ],
        "trifocal": [
            "Trifocal", "Trifocal Lenses", "Trifocals"
        ],
        "standard_progressive": [
            "Standard Progressive", "Progressive - Standard",
            "Progressive Standard", "Std. Progressive"
        ],
        "premium_progressive": [
            "Premium Progressive", "Progressive - Premium", 
            "Progressive Premium"
        ]
    }
    
    # Check if we have variations for this term
    if term in variations:
        return variations[term]
        
    # Default to a list with just the term itself
    return [term] 