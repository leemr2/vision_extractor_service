"""
EyeMed-specific patterns for progressive lenses with enhanced flexibility
to handle all pricing formats and tier structures
"""
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup, 
    SectionPattern, TablePattern, ContextualPattern
)
import re
import logging
from typing import Dict, Tuple, List, Optional, Any, Pattern

logger = logging.getLogger(__name__)

# Dynamic pricing format patterns that can be applied to any tier
PRICING_FORMATS = {
    "simple_copay": r"\$(\d+(?:\.\d+)?)\s*copay",
    "percentage_discount": r"(\d+)%\s+(?:off|of)\s+retail(?:\s+price)?",
    "copay_with_percentage_less_allowance": r"\$(\d+(?:\.\d+)?)\s*copay;\s*(\d+)%\s+off\s+retail(?:\s+price)?\s+less\s+\$(\d+(?:\.\d+)?)\s+allowance",
    "copay_with_percentage_over_allowance": r"\$(\d+(?:\.\d+)?)\s*copay;\s*(\d+)%\s+off\s+balance\s+over\s+\$(\d+(?:\.\d+)?)\s+allowance",
    "applied_to_remaining_balance": r"\$(\d+(?:\.\d+)?)\s+applied\s+to\s+remaining\s+balance",
    "percentage_of_retail_to_remaining_balance": r"(\d+)%\s+of\s+retail\s+price\s+applied\s+to\s+remaining\s+balance"
}

# Document structure detection patterns
TIER_STRUCTURE_DETECTION = {
    "has_standard": re.compile(r"Progressive\s*[-\s]*Standard", re.IGNORECASE),
    "has_premium_generic": re.compile(r"Progressive\s*[-\s]*Premium(?!\s+Tier)", re.IGNORECASE),
    "has_premium_tier_1": re.compile(r"Progressive\s*[-\s]*Premium\s+Tier\s+1", re.IGNORECASE),
    "has_premium_tier_2": re.compile(r"Progressive\s*[-\s]*Premium\s+Tier\s+2", re.IGNORECASE),
    "has_premium_tier_3": re.compile(r"Progressive\s*[-\s]*Premium\s+Tier\s+3", re.IGNORECASE),
    "has_premium_tier_4": re.compile(r"Progressive\s*[-\s]*Premium\s+Tier\s+4", re.IGNORECASE),
    "has_premium_tier_5": re.compile(r"(?:Progressive\s*[-\s]*Premium\s+Tier\s+5|Tier\s+5\s+Innovations)", re.IGNORECASE),
    "has_declining_balance": re.compile(r"(?:applied\s+to\s+remaining\s+balance|Declining\s+Balance)", re.IGNORECASE),
    "has_complex_pricing": re.compile(r"(?:Premium\s+Tier\s+\d[^$]*?\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off|copay;\s*\d+%\s+off|less\s+\$\d+\s+allowance)", re.IGNORECASE)
}

# New pattern detection for single progressive price
PROGRESSIVE_SINGLE_PRICE_PATTERN = re.compile(r"Progressive(?![^.]*?(?:Standard|Premium|Tier))[^.]*?\$\d+(?:\.\d+)?", re.IGNORECASE)

# Complex pricing patterns for different formats
COMPLEX_PRICING_PATTERNS = {
    # Format 1: "$X copay; Y% off retail price less $Z allowance"
    "percent_less_allowance": re.compile(r"\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?\s+less\s+\$\d+(?:\.\d+)?\s+allowance", re.IGNORECASE),
    
    # Format 2: "$X copay, then Y% of charge less $Z allowance"
    "then_percent_less_allowance": re.compile(r"\$\d+(?:\.\d+)?\s*copay,?\s+then\s+\d+%\s+of\s+charge\s+less\s+\$\d+(?:\.\d+)?\s+allowance", re.IGNORECASE),
    
    # Format 3: "$X copay, 80% of charge less $Y allowance"
    "percent_of_charge_less": re.compile(r"\$\d+(?:\.\d+)?\s*copay,?\s+\d+%\s+of\s+charge\s+less\s+\$\d+(?:\.\d+)?\s+allowance", re.IGNORECASE),
    
    # Format 4: "$X copay, Y% of balance over $Z allowance"
    "percent_over_allowance": re.compile(r"\$\d+(?:\.\d+)?\s*copay,?\s+\d+%\s+of\s+balance\s+over\s+\$\d+(?:\.\d+)?\s+allowance", re.IGNORECASE),
    
    # Format 5: Mixed complex price with retail, balance and/or allowance
    "mixed_complex": re.compile(r"\$\d+(?:\.\d+)?\s*copay(?:;|,)?\s+(?:\d+%\s+(?:of|off)\s+(?:charge|retail|balance|price)(?:\s+(?:less|over|up to)\s+\$\d+(?:\.\d+)?)?(?:\s+allowance)?)", re.IGNORECASE),
}

# Define table row patterns for progressive lens tiers
# Each tier has two patterns: same-line and next-line pricing formats
# Capture stops at next table row or section boundary
TABLE_ROW_PATTERNS = {
    "standard": [
        re.compile(r"Progressive\s+[-\s]+Standard\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),  # Same line
        re.compile(r"Progressive\s+[-\s]+Standard\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),  # Next line
    ],
    "premium": [
        re.compile(r"Progressive\s+[-\s]+Premium(?!\s+Tier)\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),  # Same line
        re.compile(r"Progressive\s+[-\s]+Premium(?!\s+Tier)\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),  # Next line
    ],
    1: [
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+1\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+1\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
    ],
    2: [
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+2\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+2\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
    ],
    3: [
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+3\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+3\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
    ],
    4: [
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+4\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+4\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
    ],
    5: [
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+5\s+(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
        re.compile(r"Progressive\s+[-\s]+Premium\s+Tier\s+5\s*\n\s*(\$[^\n]+?)(?=\n|$)", re.IGNORECASE),
    ],
}

# Patterns for detecting progressive lens benefit tables
TABLE_SECTION_PATTERNS = [
    # Pattern for finding the start of the lens options section
    re.compile(r"((?:LENS OPTIONS|LENS CHOICES|VISION CARE SERVICES).*?(?:Progressive.*?(?:\$\d+|\d+%).*?)(?:FRAMES|CONTACT LENSES|CONTACT|FREQUENCY|FREQUENCY OF SERVICE))", re.DOTALL | re.IGNORECASE),
    
    # Narrower pattern focusing specifically on progressive lens table rows
    re.compile(r"(Progressive\s+-\s+Standard.*?(?:(?:Progressive\s+-\s+Premium\s+Tier\s+\d)|(?:FRAMES|CONTACT LENSES|CONTACT|FREQUENCY|FREQUENCY OF SERVICE)))", re.DOTALL | re.IGNORECASE),
    
    # General lens benefits table pattern
    re.compile(r"(Lens Options.*?(?:Progressive.*?(?:\$\d+|\d+%).*?)(?:FRAMES|CONTACT LENSES|CONTACT|FREQUENCY|FREQUENCY OF SERVICE))", re.DOTALL | re.IGNORECASE),
]

# Table boundary indicators
TABLE_BOUNDARY_MARKERS = [
    "FRAMES", "CONTACT LENSES", "CONTACT LENS", "FREQUENCY", "FREQUENCY OF SERVICE", "LASER VISION",
    "ADDITIONAL PAIRS", "ADDITIONAL ITEMS", "OTHER SERVICES"
]

class ProgressivePatternFactory:
    """Creates appropriate progressive lens patterns based on document structure"""
    
    @staticmethod
    def analyze_document(document_text: str) -> Dict[str, bool]:
        """
        Analyze document to detect if it contains complex pricing formats or certain progressive lens patterns
        
        Args:
            document_text: The document text to analyze
            
        Returns:
            Dictionary with detection results
        """
        results = {}
        
        # Check if complex pricing exists anywhere in document
        complex_found = False
        for section in document_text.split('\n'):
            format_name, _ = detect_complex_pricing_format(section)
            if format_name:
                complex_found = True
                results["has_complex_pricing"] = True
                break
                    
        if not complex_found:
            results["has_complex_pricing"] = False
        
        # Look for table with tier headers to determine if document has progressive tiers
        results["has_progressive_tiers"] = False
        progressive_table = locate_progressive_table(document_text)
        
        if progressive_table:
            # Check for tier headers in the table
            tier_headers = re.findall(r"Progressive\s+(?:-|\s+)?Premium\s+Tier\s+\d", progressive_table, re.IGNORECASE)
            if tier_headers:
                results["has_progressive_tiers"] = True
                # Count unique tier numbers
                tier_numbers = set()
                for header in tier_headers:
                    tier_match = re.search(r"Tier\s+(\d)", header, re.IGNORECASE)
                    if tier_match:
                        tier_numbers.add(int(tier_match.group(1)))
                results["tier_count"] = len(tier_numbers)
        
        # Check for tiers if no table was found
        if not results.get("has_progressive_tiers", False):
            # Look for tier mentions using a broader search
            tier_mentions = re.findall(r"Premium\s+Tier\s+\d", document_text, re.IGNORECASE)
            if tier_mentions:
                results["has_progressive_tiers"] = True
                # Count unique tier numbers
                tier_numbers = set()
                for mention in tier_mentions:
                    tier_match = re.search(r"Tier\s+(\d)", mention, re.IGNORECASE)
                    if tier_match:
                        tier_numbers.add(int(tier_match.group(1)))
                results["tier_count"] = len(tier_numbers)
        
        # Check for standard/premium split without tiers
        # Fixed regex to properly match "Progressive - Standard" and "Progressive - Premium"
        standard_premium_split = (
            re.search(r"Progressive\s+[-\s]+Standard", document_text, re.IGNORECASE) is not None and
            re.search(r"Progressive\s+[-\s]+Premium(?!\s+Tier)", document_text, re.IGNORECASE) is not None and
            not results.get("has_progressive_tiers", False)
        )
        results["has_standard_premium_split"] = standard_premium_split
        
        # Check for single price
        has_general_progressive = (
            PROGRESSIVE_SINGLE_PRICE_PATTERN.search(document_text) is not None and
            not results.get("has_progressive_tiers", False) and
            not results.get("has_standard_premium_split", False)
        )
        results["has_single_price"] = has_general_progressive
        
        return results
    
    @staticmethod
    def _determine_pattern_type(detection_results, document_text):
        """
        Determine which of the four progressive pattern types is present:
        1: Single progressive price pattern
        2: Standard/Premium split (two-tier) pattern
        3: Standard + Premium tiers 1-4 pattern
        4: Standard + Premium tiers 1-5 pattern
        """
        # Count the number of tier indicators detected
        tier_count = sum(1 for i in range(1, 6) if detection_results.get(f"has_premium_tier_{i}", False))
        
        # Check for single progressive price pattern (Pattern 1)
        if (not detection_results.get("has_standard", False) and 
            not detection_results.get("has_premium_generic", False) and
            tier_count == 0 and
            PROGRESSIVE_SINGLE_PRICE_PATTERN.search(document_text)):
            return 1
        
        # Check for Standard/Premium split (Pattern 2)
        elif (detection_results.get("has_standard", False) and 
              detection_results.get("has_premium_generic", False) and
              tier_count == 0):
            return 2
        
        # Check for Standard + Premium tiers 1-5 pattern (Pattern 4)
        # This check comes before Pattern 3 to ensure Pattern 4 takes precedence if tier 5 is present
        elif detection_results.get("has_premium_tier_5", False):
            return 4
        
        # Check for Standard + Premium tiers 1-4 pattern (Pattern 3)
        elif tier_count > 0:
            return 3
        
        # Default to standard/premium split if we can't determine clearly
        else:
            # If we at least have a standard progressive, default to pattern 2
            if detection_results.get("has_standard", False):
                return 2
            # Last resort default to single pattern
            return 1
    
    @staticmethod
    def create_patterns_for_document(document_text: str) -> Tuple[Dict[str, bool], int]:
        """
        Detect which pattern type this document uses and create appropriate patterns
        
        Args:
            document_text: The document text to analyze
            
        Returns:
            Tuple of (detection_results, pattern_type)
            Pattern types:
            1 - Single price pattern
            2 - Standard/Premium split pattern
            3 - Standard + Premium tiers 1-4 pattern
            4 - Standard + Premium tiers 1-5 pattern
        """
        # Analyze document to identify patterns
        detection_results = ProgressivePatternFactory.analyze_document(document_text)
        
        # Determine pattern type based on detection results
        if detection_results.get("has_progressive_tiers", False):
            # Check if document contains 5 tiers
            if detection_results.get("tier_count", 0) >= 5:
                logger.debug("Detected pattern type 4: Standard + Premium tiers 1-5")
                return detection_results, 4
            else:
                logger.debug("Detected pattern type 3: Standard + Premium tiers 1-4")
                return detection_results, 3
        elif detection_results.get("has_standard_premium_split", False):
            logger.debug("Detected pattern type 2: Standard/Premium split")
            return detection_results, 2
        else:
            logger.debug("Detected pattern type 1: Single price pattern")
            return detection_results, 1

# New pattern for single progressive price
def create_single_progressive_pattern():
    """Create pattern group for single progressive price"""
    return PatternGroup(
        name="single_progressive",
        patterns=[
            RegexPattern(
                name="single_progressive_price",
                description="Single progressive lens price",
                pattern_type=PatternType.EXACT,
                target_field="progressive_lenses.single_price",
                confidence=ConfidenceLevel.HIGH,
                patterns=[
                    r"Progressive:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)(?:\s|$|;)",
                    r"Progressive\s+Lenses:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)(?:\s|$|;)",
                    r"Progressive(?![^.]*?(?:Standard|Premium|Tier))[^.]*?(\$\d+(?:\.\d+)?)"
                ]
            ),
            SectionPattern(
                name="single_progressive_section",
                description="Section-based pattern for single progressive",
                pattern_type=PatternType.SECTION,
                target_field="progressive_lenses.single_price",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Lenses",
                value_pattern=r"Progressive:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)"
            ),
            TablePattern(
                name="single_progressive_table",
                description="Table-based pattern for single progressive",
                pattern_type=PatternType.TABLE,
                target_field="progressive_lenses.single_price",
                confidence=ConfidenceLevel.MEDIUM,
                row_header="Progressive",
                column_header="In-Network Member Cost"
            )
        ]
    )

# Updated detection for complex pricing formats
def detect_complex_pricing_format(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect if text contains a complex pricing format and return the format name and matched text
    
    Args:
        text: Text to analyze for complex pricing formats
        
    Returns:
        Tuple of (format_name, matched_text) or (None, None) if no complex format detected
    """
    if not text or "$" not in text:
        return None, None
        
    # Check each complex pricing pattern
    for format_name, pattern in COMPLEX_PRICING_PATTERNS.items():
        match = pattern.search(text)
        if match:
            return format_name, match.group(0)
            
    return None, None

# New function to locate progressive lens benefit table in document
def locate_progressive_table(document_text):
    """
    Locates the progressive lens benefits table in the document
    Returns the table text if found, otherwise None
    """
    # Try each pattern to locate the progressive lens table section
    for pattern in TABLE_SECTION_PATTERNS:
        match = pattern.search(document_text)
        if match:
            table_text = match.group(1)
            logger.debug(f"Found progressive lens table section with length {len(table_text)}")
            return table_text
    
    # If no specific table found, try to extract a section around progressive lens mentions
    progressive_mentions = list(re.finditer(r"Progressive", document_text, re.IGNORECASE))
    if progressive_mentions:
        # Get the position of the first mention
        first_pos = progressive_mentions[0].start()
        
        # Find a reasonable section boundary before this position
        section_start = 0
        for i in range(first_pos-1, max(0, first_pos-500), -1):
            if document_text[i] == '\n' and any(marker in document_text[i:i+30] for marker in ["LENS", "LENSES", "VISION"]):
                section_start = i
                break
        
        # Find a reasonable section boundary after the last mention
        last_pos = progressive_mentions[-1].end()
        section_end = min(len(document_text), last_pos + 500)
        for i in range(last_pos, section_end):
            if i >= len(document_text):
                break
            if document_text[i] == '\n' and any(marker in document_text[i:i+30] for marker in TABLE_BOUNDARY_MARKERS):
                section_end = i
                break
        
        # Extract the approximate section
        if section_end > section_start:
            table_section = document_text[section_start:section_end]
            if len(table_section) > 50:  # Ensure we have a meaningful section
                logger.debug(f"Extracted approximate progressive lens section with length {len(table_section)}")
                return table_section
    
    logger.debug("No specific progressive lens table section found")
    return None

# Enhanced function to extract tier-specific pricing from table
def extract_tier_from_table(document_text: str, tier_key: Any) -> Optional[str]:
    """
    Extract pricing for specific progressive lens tier from table row
    
    Args:
        document_text: The document text to search (full doc or table section)
        tier_key: The tier key to extract ('standard', 'premium', or tier number 1-5)
        
    Returns:
        Extracted pricing string or None if not found
    """
    # Get patterns for this tier
    if tier_key not in TABLE_ROW_PATTERNS:
        logger.debug(f"No table row pattern available for tier {tier_key}")
        return None
        
    patterns = TABLE_ROW_PATTERNS[tier_key]
    
    # Try each pattern (same-line first, then next-line)
    for pattern in patterns:
        match = pattern.search(document_text)
        if match:
            value = match.group(1).strip()
            tier_name = f"Tier {tier_key}" if isinstance(tier_key, int) else tier_key.capitalize()
            logger.debug(f"Found {tier_name} progressive pricing from table row: {value}")
            return value
    
    # If standard tier and no direct match, try alternative patterns
    if tier_key == "standard":
        alt_patterns = [
            re.compile(r"Standard\s+Progressive\s+([^\n]+)", re.IGNORECASE),
            re.compile(r"Standard\s+Progressive\s*\n\s*([^\n]+)", re.IGNORECASE),
        ]
        for alt_pattern in alt_patterns:
            alt_match = alt_pattern.search(document_text)
            if alt_match:
                value = alt_match.group(1).strip()
                logger.debug(f"Found Standard progressive from alternative table row: {value}")
                return value
    
    # If premium tier (without number) and no direct match, try alternative patterns
    if tier_key == "premium":
        alt_patterns = [
            re.compile(r"Premium\s+Progressive(?!\s+Tier)\s+([^\n]+)", re.IGNORECASE),
            re.compile(r"Premium\s+Progressive(?!\s+Tier)\s*\n\s*([^\n]+)", re.IGNORECASE),
        ]
        for alt_pattern in alt_patterns:
            alt_match = alt_pattern.search(document_text)
            if alt_match:
                value = alt_match.group(1).strip()
                logger.debug(f"Found Premium progressive from alternative table row: {value}")
                return value
    
    logger.debug(f"No table row found for progressive {tier_key}")
    return None

# Updated extraction for premium tier complex pricing
def extract_premium_tier_complex(document_text: str, tier: int) -> Optional[str]:
    """
    Extract complex pricing for a specific premium tier
    
    Args:
        document_text: Document text to search
        tier: The premium tier number (1-5)
        
    Returns:
        Complex pricing string if found, None otherwise
    """
    # First look for complex pricing in exact tier section
    tier_section_pattern = re.compile(
        rf"Progressive(?:\s+-|\s+)Premium\s+Tier\s+{tier}[^\n]*?(\$\d+(?:\.\d+)?[^\n]*?(?:%|percent|allowance|retail|balance)(?:[^\n$]+\$\d+)?[^\n]+)",
        re.IGNORECASE | re.DOTALL
    )
    
    tier_section_match = tier_section_pattern.search(document_text)
    if tier_section_match:
        # Extract the section text for this tier
        section_text = tier_section_match.group(1)
        
        # Detect if it contains complex pricing
        format_name, complex_value = detect_complex_pricing_format(section_text)
        if complex_value:
            logger.debug(f"Found complex pricing format '{format_name}' for tier {tier}: {complex_value}")
            return complex_value
    
    # Special handling for tier 4 which often has complex pricing
    if tier == 4:
        # Broader pattern for tier 4
        tier4_pattern = re.compile(
            r"(?:Progressive\s+-\s+Premium\s+Tier\s+4|Tier\s+4|Premium\s+Tier\s+4).*?(\$\d+(?:\.\d+)?\s*copay[^$]*?(?:%|percent|allowance|retail|balance)(?:[^$]*?\$\d+(?:\.\d+)?)?[^\n]+)",
            re.IGNORECASE | re.DOTALL
        )
        
        tier4_match = tier4_pattern.search(document_text)
        if tier4_match:
            # Extract the section text for tier 4
            section_text = tier4_match.group(1)
            
            # Detect if it contains complex pricing
            format_name, complex_value = detect_complex_pricing_format(section_text)
            if complex_value:
                logger.debug(f"Found complex pricing format '{format_name}' for tier 4 (special handling): {complex_value}")
                return complex_value
    
    return None

# Pattern for exact tier match when complex pricing is detected
def create_exact_tier_match_pattern(tier, value):
    """Create a pattern group for exact tier match with complex pricing"""
    # Check if the value is one of our complex pricing formats
    format_name, _ = detect_complex_pricing_format(value)
    confidence = ConfidenceLevel.HIGH if format_name else ConfidenceLevel.MEDIUM
    
    return PatternGroup(
                                    name=f"premium_tier_{tier}_exact_match",
                                    patterns=[
                                        RegexPattern(
                                            name=f"tier_{tier}_exact_match",
                                            description=f"Exact matched pattern for Premium Tier {tier} progressive",
                                            pattern_type=PatternType.EXACT,
                                            target_field=f"progressive_lenses.premium_tier_{tier}",
                confidence=confidence,
                patterns=[
                    rf"Progressive - Premium Tier {tier}\s+({re.escape(value)})",
                    rf"Premium Tier {tier}\s+({re.escape(value)})"
                ]
            )
        ]
    )

# Standard progressive patterns with all pricing variants
def create_standard_progressive_pattern():
    """Create pattern group for standard progressive lenses"""
    return PatternGroup(
        name="standard_progressive",
        patterns=[
            RegexPattern(
                name="standard_progressive_copay",
                description="Standard progressive lenses with simple copay",
                pattern_type=PatternType.EXACT,
                target_field="progressive_lenses.standard",
                confidence=ConfidenceLevel.HIGH,
                patterns=[
                    r"(?:Progressive|Standard Progressive):?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)(?:\s|$|;)",
                    r"Progressive - Standard\s+(\$\d+(?:\.\d+)?)(?:\s|$)",
                    r"Standard Progressive[^$]*?(\$\d+(?:\.\d+)?)"
                ]
            ),
            ContextualPattern(
                name="standard_progressive_context",
                description="Contextual pattern for standard progressive",
                pattern_type=PatternType.CONTEXTUAL,
                target_field="progressive_lenses.standard",
                confidence=ConfidenceLevel.MEDIUM,
                context_identifier="Progressive - Standard",
                max_distance=100,
                value_patterns=[
                    r"\$\d+(?:\.\d+)?\s*(?:copay)?",
                    r"\d+%\s+(?:off|of)\s+retail(?:\s+price)?"
                ]
            ),
            SectionPattern(
                name="standard_progressive_section",
                description="Section-based pattern for standard progressive",
                pattern_type=PatternType.SECTION,
                target_field="progressive_lenses.standard",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Progressive Lenses",
                value_pattern=r"(?:Progressive|Standard Progressive):?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)"
            ),
            TablePattern(
                name="standard_progressive_table",
                description="Table-based pattern for standard progressive",
                pattern_type=PatternType.TABLE,
                target_field="progressive_lenses.standard",
                confidence=ConfidenceLevel.MEDIUM,
                row_header="Progressive - Standard",
                column_header="In-Network Member Cost"
            )
        ]
    )

# Generic premium pattern (when no tiers are specified)
def create_generic_premium_pattern():
    """Create pattern group for generic premium progressive lenses (no tiers)"""
    return PatternGroup(
        name="generic_premium_progressive",
        patterns=[
            RegexPattern(
                name="premium_progressive_simple",
                description="Premium progressive lenses with simple pricing",
                pattern_type=PatternType.EXACT,
                target_field="progressive_lenses.premium",
                confidence=ConfidenceLevel.HIGH,
                patterns=[
                    r"Progressive - Premium\s+(\$\d+(?:\.\d+)?)(?:\s|$)",
                    r"Premium Progressive[^$]*?(\$\d+(?:\.\d+)?)",
                    r"Progressive(?:\s+-|\s+)Premium(?!\s+Tier)[^$]*?(\$\d+(?:\.\d+)?(?:\s*copay)?)",
                    r"Progressive(?:\s+-|\s+)Premium(?!\s+Tier)[^%]*?(\d+%\s+(?:off|of)\s+retail(?:\s+price)?)"
                ]
            ),
            RegexPattern(
                name="premium_progressive_complex",
                description="Premium progressive lenses with complex pricing",
                pattern_type=PatternType.EXACT,
                target_field="progressive_lenses.premium",
                confidence=ConfidenceLevel.HIGH,
                patterns=[
                    r"Progressive(?:\s+-|\s+)Premium(?!\s+Tier)[^$]*?(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?\s+less\s+\$\d+(?:\.\d+)?\s+allowance)",
                    r"Progressive(?:\s+-|\s+)Premium(?!\s+Tier)[^$]*?(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+balance\s+over\s+\$\d+(?:\.\d+)?\s+allowance)"
                ]
            ),
            SectionPattern(
                name="premium_progressive_section",
                description="Section-based pattern for premium progressive",
                pattern_type=PatternType.SECTION,
                target_field="progressive_lenses.premium",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Progressive Lenses",
                value_pattern=r"(?:Progressive - Premium|Premium Progressive)(?:[^$]*?)(\$\d+(?:\.\d+)?|\d+%\s+(?:off|of)\s+retail)"
            ),
            TablePattern(
                name="premium_progressive_table",
                description="Table-based pattern for premium progressive",
                pattern_type=PatternType.TABLE,
                target_field="progressive_lenses.premium",
                confidence=ConfidenceLevel.MEDIUM,
                row_header="Progressive - Premium",
                column_header="In-Network Member Cost"
            )
        ]
    )

# Premium tier pattern with all pricing variants
def create_premium_tier_pattern(tier):
    """Create pattern group for a specific premium tier"""
    # Create patterns for this specific tier
    tier_patterns = [
        # Simple dollar amount - modified to be less greedy with line/field boundaries
        rf"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+{tier}:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)(?:\s|$|;|\n)",
        rf"Premium Progressive - Tier\s+{tier}:?\s*(\$\d+(?:\.\d+)?)(?:\s|$|\n)",
        rf"Progressive Premium Tier\s+{tier}\s+(\$\d+(?:\.\d+)?)(?:\s|$|\n)"
    ]
    
    # Percentage discount
    percentage_patterns = [
        rf"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+{tier}:?\s*(\d+%\s+(?:off|of)\s+retail(?:\s+price)?)(?:\s|$|\n)",
        rf"Premium Progressive - Tier\s+{tier}:?\s*(\d+%\s+(?:off|of)\s+retail(?:\s+price)?)(?:\s|$|\n)"
    ]
    
    # Complex pricing patterns - capturing the FULL pricing text but with proper boundaries
    complex_patterns = [
        # Copay with % off retail less allowance - with boundary control
        rf"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+{tier}:?\s*(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?\s+less\s+\$\d+(?:\.\d+)?\s+allowance)(?:\s|$|\n)",
        rf"Premium Tier\s+{tier}[^$\n]*?(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?\s+less\s+\$\d+(?:\.\d+)?\s+allowance)(?:\s|$|\n)",
        # Copay with % off balance over allowance - with boundary control
        rf"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+{tier}:?\s*(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+balance\s+over\s+\$\d+(?:\.\d+)?\s+allowance)(?:\s|$|\n)",
        # Flexible matching with proper boundary enforcement
        rf"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+{tier}:?\s*(\$\d+(?:\.\d+)?\s*copay;[^$\n]*?(?:off|of)[^$\n]*?\$\d+(?:\.\d+)?(?:\s+allowance)?)(?:\s|$|\n|Progressive)"
    ]
    
    # Special handling for Tier 4 which often has complex formatting
    if tier == 4:
        # Add more specific tier 4 patterns that capture the full pricing structure with boundary control
        complex_tier4_patterns = [
            # More precise patterns for tier 4 with boundaries
            r"Progressive(?:\s+-|:|\s+)Premium\s+Tier\s+4:?\s*(\$\d+(?:\.\d+)?\s*copay;\s*20%\s+off\s+retail\s+price\s+less\s+\$120\s+allowance)(?:\s|$|\n)",
            r"Progressive - Premium Tier 4\s+(\$\d+(?:\.\d+)?\s*copay;\s*20%\s+off\s+retail\s+price\s+less\s+\$120\s+allowance)(?:\s|$|\n)",
            r"Premium Tier 4[^$\n]*?(\$\d+(?:\.\d+)?\s*copay;\s*20%\s+off\s+retail\s+price\s+less\s+\$120\s+allowance)(?:\s|$|\n)",
            # Looser pattern with boundaries
            r"Premium Tier 4[^$\n]*?(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail[^$\n]*?less\s+\$\d+)(?:\s|$|\n|Lens|Contact)"
        ]
        complex_patterns.extend(complex_tier4_patterns)
    
    # Combine all patterns
    all_patterns = tier_patterns + percentage_patterns + complex_patterns
    
    # Contextual patterns for when pricing appears near but not directly with the tier mention
    contextual_patterns = [
        rf"Premium\s+Tier\s+{tier}.*?(\$\d+(?:\.\d+)?)(?:\s|$|\n)",
        rf"Premium\s+Tier\s+{tier}.*?(\d+%\s+(?:off|of)\s+retail)(?:\s|$|\n)",
        # Enhanced contextual patterns for complex pricing with boundary control
        rf"Premium\s+Tier\s+{tier}.*?(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?(?:\s+less|\s+over)\s+\$\d+(?:\.\d+)?)(?:\s|$|\n|Lens|Progressive|Contact)"
    ]
    
    return PatternGroup(
        name=f"premium_tier_{tier}_progressive",
        patterns=[
            RegexPattern(
                name=f"tier_{tier}_exact",
                description=f"Exact pattern for Premium Tier {tier} progressive",
                pattern_type=PatternType.EXACT,
                target_field=f"progressive_lenses.premium_tier_{tier}",
                confidence=ConfidenceLevel.HIGH,
                patterns=all_patterns
            ),
            ContextualPattern(
                name=f"tier_{tier}_contextual",
                description=f"Contextual pattern for Premium Tier {tier} progressive",
                pattern_type=PatternType.CONTEXTUAL,
                target_field=f"progressive_lenses.premium_tier_{tier}",
                confidence=ConfidenceLevel.MEDIUM,
                context_identifier=f"Premium Tier {tier}",
                max_distance=150,
                value_patterns=[
                    r"\$\d+(?:\.\d+)?(?:\s*copay)?(?:\s|$|\n)",
                    r"\d+%\s+(?:off|of)\s+retail(?:\s+price)?(?:\s|$|\n)",
                    # Enhanced contextual value pattern for complex pricing with boundaries
                    r"\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?(?:\s+less|\s+over)\s+\$\d+(?:\.\d+)?\s+allowance(?:\s|$|\n)",
                    # Looser pattern with boundaries
                    r"\$\d+(?:\.\d+)?\s*copay;\s*[^$\n]*?off[^$\n]*?\$\d+(?:\.\d+)?(?:\s|$|\n|Lens|Progressive|Contact)"
                ]
            ),
            SectionPattern(
                name=f"tier_{tier}_section",
                description=f"Section-based pattern for Premium Tier {tier}",
                pattern_type=PatternType.SECTION,
                target_field=f"progressive_lenses.premium_tier_{tier}",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Progressive Lenses",
                # Enhanced section value pattern with better boundaries
                value_pattern=rf"(?:Premium Tier {tier}|Progressive - Premium Tier {tier})(?:[^$\n]*?)(\$\d+(?:\.\d+)?|\d+%\s+(?:off|of)\s+retail(?:\s+price)?|\$\d+(?:\.\d+)?\s*copay;\s*\d+%[^$\n]*?(?:less|over)\s+\$\d+(?:\.\d+)?)(?:\s|$|\n|Progressive|Lens|Contact)"
            ),
            TablePattern(
                name=f"tier_{tier}_table",
                description=f"Table-based pattern for Premium Tier {tier}",
                pattern_type=PatternType.TABLE,
                target_field=f"progressive_lenses.premium_tier_{tier}",
                confidence=ConfidenceLevel.HIGH if tier == 4 else ConfidenceLevel.MEDIUM,
                row_header=f"Progressive - Premium Tier {tier}",
                column_header="In-Network Member Cost"
            )
        ]
    )

# Special case for Tier 5 Innovations - similar to regular tiers but with special naming
TIER_5_INNOVATIONS_PATTERNS = PatternGroup(
    name="tier_5_innovations",
    patterns=[
        RegexPattern(
            name="tier_5_innovations_exact",
            description="Exact pattern for Tier 5 Innovations",
            pattern_type=PatternType.EXACT,
            target_field="progressive_lenses.premium_tier_5",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Premium\s+Tier\s+5|Tier\s+5\s+Innovations|Premium Tier 5 Innovations)(?:[^$]*?)(\$\d+(?:\.\d+)?\s*(?:copay)?)",
                r"(?:Premium\s+Tier\s+5|Tier\s+5\s+Innovations|Premium Tier 5 Innovations)(?:[^%]*?)((?:\d+)%\s+off\s+retail(?:\s+price)?)",
                r"(?:Premium\s+Tier\s+5|Tier\s+5\s+Innovations|Premium Tier 5 Innovations)(?:[^$]*?)(\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?\s+less\s+\$\d+(?:\.\d+)?\s+allowance)"
            ]
        ),
        ContextualPattern(
            name="tier_5_innovations_contextual",
            description="Contextual pattern for Tier 5 Innovations",
            pattern_type=PatternType.CONTEXTUAL,
            target_field="progressive_lenses.premium_tier_5",
            confidence=ConfidenceLevel.MEDIUM,
            context_identifier="Tier 5 Innovations",
            max_distance=150,
            value_patterns=[
                r"\$\d+(?:\.\d+)?(?:\s*copay)?",
                r"\d+%\s+(?:off|of)\s+retail(?:\s+price)?",
                r"\$\d+(?:\.\d+)?\s*copay;\s*\d+%\s+off\s+retail(?:\s+price)?(?:\s+less|\s+over)\s+\$\d+(?:\.\d+)?"
            ]
        ),
        SectionPattern(
            name="tier_5_innovations_section",
            description="Section-based pattern for Tier 5 Innovations",
            pattern_type=PatternType.SECTION,
            target_field="progressive_lenses.premium_tier_5",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Progressive Lenses",
            value_pattern=r"(?:Premium\s+Tier\s+5|Tier\s+5\s+Innovations|Premium Tier 5 Innovations)(?:[^$]*?)(\$\d+(?:\.\d+)?|\d+%\s+off\s+retail)"
        )
    ]
)

# Default patterns - will be used if structure detection fails
STANDARD_PROGRESSIVE_PATTERNS = create_standard_progressive_pattern()
PREMIUM_PROGRESSIVE_PATTERNS = create_generic_premium_pattern()
PREMIUM_TIER_PROGRESSIVE_PATTERNS = {
    # Use 1-indexed keys to match tier numbers
    1: create_premium_tier_pattern(1),
    2: create_premium_tier_pattern(2),
    3: create_premium_tier_pattern(3),
    4: create_premium_tier_pattern(4),
    5: TIER_5_INNOVATIONS_PATTERNS
}

# Export pattern groups for the pattern manager to find
EYEMED_PROGRESSIVE_PATTERNS = [
    STANDARD_PROGRESSIVE_PATTERNS,
    PREMIUM_PROGRESSIVE_PATTERNS,
]

# Add all premium tier patterns
EYEMED_PROGRESSIVE_PATTERNS.extend(PREMIUM_TIER_PROGRESSIVE_PATTERNS.values())

# Named export that pattern manager will look for
__all__ = ["EYEMED_PROGRESSIVE_PATTERNS", "ProgressivePatternFactory"]
