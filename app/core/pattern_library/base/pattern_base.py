"""
Base classes for the extraction pattern library
"""
from typing import Dict, List, Optional, Pattern, Union, Any, Callable
import re
from dataclasses import dataclass, field
from enum import Enum

class PatternType(Enum):
    """
    Types of extraction patterns
    """
    EXACT = "exact"        # Exact text match
    FUZZY = "fuzzy"        # Fuzzy text match
    TABLE = "table"        # Tabular data pattern
    SECTION = "section"    # Section-based pattern
    KEY_VALUE = "key_value" # Key-value format
    CONTEXTUAL = "contextual" # Uses surrounding context

class ConfidenceLevel(Enum):
    """
    Confidence levels for extraction results
    """
    HIGH = 0.9
    MEDIUM = 0.8
    LOW = 0.7
    FALLBACK = 0.6

@dataclass
class ExtractionPattern:
    """Base class for all extraction patterns"""
    name: str
    description: str
    pattern_type: PatternType
    target_field: str  # Field in the final output model
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract data using this pattern"""
        raise NotImplementedError("Subclasses must implement extract()")
    
    def validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate the extracted result"""
        return True if result else False

@dataclass
class RegexPattern(ExtractionPattern):
    """Pattern based on regular expressions"""
    patterns: List[str] = field(default_factory=list)  # Multiple regex patterns for fallback
    regex_flags: int = re.IGNORECASE
    
    def __post_init__(self):
        """Compile patterns after initialization"""
        self.compiled_patterns = [
            re.compile(pattern, self.regex_flags) for pattern in self.patterns
        ]
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Try each pattern in order until one succeeds"""
        for i, pattern in enumerate(self.compiled_patterns):
            match = pattern.search(text)
            if match:
                # Apply decreasing confidence with each fallback pattern
                conf_adjustment = -0.05 * i  # Reduce confidence for fallback patterns
                
                # For eligibility patterns, always return "Yes" as the value
                if "eligible" in self.target_field.lower():
                    return {
                        "value": "Yes",
                        "confidence": max(0.5, self.confidence.value + conf_adjustment),
                        "pattern_index": i
                    }
                else:
                    return {
                        "value": match.group(1).strip() if match.groups() else match.group(0).strip(),
                        "confidence": max(0.5, self.confidence.value + conf_adjustment),
                        "pattern_index": i
                    }
        return None

@dataclass
class FuzzyPattern(ExtractionPattern):
    """Pattern using fuzzy matching for benefit names"""
    key_terms: List[str] = field(default_factory=list)  # Terms to match
    value_pattern: str = ""  # Pattern to extract the value once key is found
    proximity: int = 100  # Character proximity to search after key match
    
    def __post_init__(self):
        """Compile value pattern after initialization"""
        self.compiled_value_pattern = re.compile(self.value_pattern, re.IGNORECASE)
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Use fuzzy matching to find key terms and extract values"""
        # Simplified implementation - in production would use a proper fuzzy matching library
        for term in self.key_terms:
            # Simple case-insensitive contains search - would be replaced with fuzzy matching
            idx = text.lower().find(term.lower())
            if idx >= 0:
                # Search for the value pattern in proximity to the key term
                search_text = text[idx:idx + self.proximity]
                match = self.compiled_value_pattern.search(search_text)
                if match:
                    return {
                        "value": match.group(1).strip() if match.groups() else match.group(0).strip(),
                        "confidence": self.confidence.value,
                        "key_term": term
                    }
        return None

@dataclass
class TablePattern(ExtractionPattern):
    """Pattern for extracting from tabular data"""
    row_header: str = ""  # Row identifier
    column_header: str = ""  # Column identifier
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract values from tabular data by identifying row and column intersections"""
        # This is a simplified implementation - would need to be expanded for production
        
        # Find the row containing our row header
        row_pattern = re.compile(f".*{re.escape(self.row_header)}.*", re.IGNORECASE | re.MULTILINE)
        row_match = row_pattern.search(text)
        if not row_match:
            return None
            
        row_text = row_match.group(0)
        
        # Find the column position (this is simplified and would need to be more robust)
        lines = text.split('\n')
        header_line = None
        for line in lines:
            if self.column_header.lower() in line.lower():
                header_line = line
                break
                
        if not header_line:
            return None
            
        # Find the column position (simplified)
        col_pos = header_line.lower().find(self.column_header.lower())
        if col_pos < 0:
            return None
        
        # Special case for eligibility fields - check for "Yes"
        if "eligible" in self.target_field.lower():
            yes_pattern = re.compile(r"Yes", re.IGNORECASE)
            yes_match = yes_pattern.search(row_text)
            if yes_match:
                return {
                    "value": "Yes",
                    "confidence": self.confidence.value,
                    "row": self.row_header,
                    "column": self.column_header
                }
            return None
            
        # Extract value from row at column position (simplified)
        # For a robust implementation, we would need to properly parse the table structure
        value_pattern = r"\$\d+(?:\.\d+)?|(?:\d+)%\s+off\s+retail(?:\s+price)?(?:\s+less\s+\$\d+(?:\.\d+)?\s+allowance)?|(?:Yes|No)"
        value_matches = list(re.finditer(value_pattern, row_text))
        
        # Find the value closest to the column position
        closest_match = None
        min_distance = float('inf')
        
        for match in value_matches:
            distance = abs(match.start() - col_pos)
            if distance < min_distance:
                min_distance = distance
                closest_match = match
                
        if closest_match and min_distance < 50:  # Arbitrary threshold
            return {
                "value": closest_match.group(0).strip(),
                "confidence": max(0.6, self.confidence.value - (min_distance / 100)),
                "row": self.row_header,
                "column": self.column_header
            }
            
        return None

@dataclass
class SectionPattern(ExtractionPattern):
    """Pattern for extracting from specific document sections"""
    section_identifier: str = ""  # Text that identifies the section
    value_pattern: str = ""  # Pattern to extract the value within the section
    max_section_length: int = 500  # Maximum characters to include in section
    
    def __post_init__(self):
        """Compile patterns after initialization"""
        self.compiled_value_pattern = re.compile(self.value_pattern, re.IGNORECASE)
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract value from a specific document section"""
        # Find the section
        section_pattern = f"{re.escape(self.section_identifier)}(.*?)(?:(?:{self._get_section_boundary_pattern()})|$)"
        section_match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not section_match:
            return None
            
        # Extract section text with length limit to avoid PHI
        section_text = section_match.group(1)[:self.max_section_length]
        
        # Find the value within the section
        value_match = self.compiled_value_pattern.search(section_text)
        if value_match:
            # For eligibility checks, return "Yes" as the value
            if "eligible" in self.target_field.lower():
                return {
                    "value": "Yes",
                    "confidence": self.confidence.value,
                    "section": self.section_identifier
                }
            else:
                return {
                    "value": value_match.group(1).strip() if value_match.groups() else value_match.group(0).strip(),
                    "confidence": self.confidence.value,
                    "section": self.section_identifier
                }
            
        return None
        
    def _get_section_boundary_pattern(self) -> str:
        """Get common section boundary patterns"""
        common_boundaries = [
            "Vision Care Services",
            "Frame",
            "Lens(es)",
            "Lenses",
            "Exam",
            "Contact",
            "Lens Options",
            "Additional Pairs",
            "Frequency"
        ]
        return "|".join([re.escape(boundary) for boundary in common_boundaries])

@dataclass
class ContextualPattern(ExtractionPattern):
    """Pattern for extracting values based on surrounding context"""
    context_identifier: str = ""  # Text that identifies the context
    value_patterns: List[str] = field(default_factory=list)  # Patterns to extract values near the context
    max_distance: int = 100  # Maximum characters to search after the context
    
    def __post_init__(self):
        """Compile patterns after initialization"""
        self.compiled_value_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.value_patterns
        ]
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract value based on surrounding context"""
        # Find the context
        context_idx = text.lower().find(self.context_identifier.lower())
        if context_idx < 0:
            return None
            
        # Search for values near the context
        search_text = text[context_idx:context_idx + self.max_distance]
        
        # Try each value pattern
        for i, pattern in enumerate(self.compiled_value_patterns):
            match = pattern.search(search_text)
            if match:
                # Apply decreasing confidence with each fallback pattern
                conf_adjustment = -0.05 * i
                
                return {
                    "value": match.group(1).strip() if match.groups() else match.group(0).strip(),
                    "confidence": max(0.5, self.confidence.value + conf_adjustment),
                    "context": self.context_identifier,
                    "pattern_index": i
                }
                
        return None

@dataclass
class PatternGroup:
    """Group of related patterns with fallback logic"""
    name: str = ""
    patterns: List[ExtractionPattern] = field(default_factory=list)
    
    def extract(self, text: str) -> Optional[Dict[str, Any]]:
        """Try each pattern in the group until one succeeds"""
        results = []
        for pattern in self.patterns:
            result = pattern.extract(text)
            if result:
                results.append((pattern, result))
        
        if not results:
            return None
            
        # Return the highest confidence result
        results.sort(key=lambda x: x[1].get("confidence", 0), reverse=True)
        pattern, result = results[0]
        return {
            "field": pattern.target_field,
            "value": result["value"],
            "confidence": result["confidence"],
            "pattern_name": pattern.name
        } 