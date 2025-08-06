"""
Spectera document pattern library for text extraction
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Pattern

# Key section header patterns
SECTION_HEADERS = {
    "member_info": re.compile(r"(?:MEMBER\s+INFORMATION|Patient Information|PATIENT\s+INFORMATION)", re.IGNORECASE),
    "eligibility": re.compile(r"(?:ELIGIBILITY|Service\s+Frequency|Coverage\s+Frequency)", re.IGNORECASE),
    "in_network": re.compile(r"(?:IN-NETWORK\s+COVERAGE|Network\s+Benefits|COVERED\s+BENEFITS)", re.IGNORECASE),
    "out_network": re.compile(r"(?:OUT-OF-NETWORK\s+REIMBURSEMENT|Out-of-Network\s+Benefits)", re.IGNORECASE),
    "vision_services": re.compile(r"(?:Vision\s+Care\s+Services|VISION\s+SERVICES|COVERED\s+SERVICES)", re.IGNORECASE),
    "patient_responsibility": re.compile(r"(?:Patient\s+Responsibility|MEMBER\s+COST|MEMBER\s+PAYS)", re.IGNORECASE),
}

# Pattern for identifying rows with vision care services and patient responsibility
TABLE_ROW_PATTERN = re.compile(
    r"([A-Za-z0-9\s\-\.\,\(\)\/]+)\s{2,}([A-Za-z0-9\s\$\-\.\%\,\(\)\/]+)$"
)

# Pattern for identifying table headers
TABLE_HEADER_PATTERN = re.compile(
    r"(?:Vision\s+Care\s+Services|VISION\s+SERVICES).{1,50}(?:Patient\s+Responsibility|MEMBER\s+COST)", 
    re.IGNORECASE
)

# Pattern for finding the patient responsibility column
PATIENT_RESPONSIBILITY_COLUMN = re.compile(
    r"Patient\s+Responsibility(?:\s+\(includes\s+applicable\s+copay\))?", 
    re.IGNORECASE
)

# Pattern for extracting dollar amounts
DOLLAR_AMOUNT_PATTERN = re.compile(r"\$(\d+(?:\.\d+)?)")

# Pattern for extracting percentages
PERCENTAGE_PATTERN = re.compile(r"(\d+)%")

# Pattern for extracting covered-in-full statements
COVERED_IN_FULL_PATTERN = re.compile(r"(Covered(?:\-in\-Full)?)", re.IGNORECASE)

# Pattern for extracting age-specific information
AGE_SPECIFIC_PATTERN = re.compile(r"for\s+Ages\s+(\d+(?:\-\d+|\+))", re.IGNORECASE)

# Pattern for extracting quantity-limited benefits
QUANTITY_PATTERN = re.compile(r"(?:up\s+to\s+(\d+)\s+Boxes|(\d+)\s+boxes)", re.IGNORECASE)

# Pattern for extracting allowance information
ALLOWANCE_PATTERN = re.compile(r"(?:Allowance\s+up\s+to\s+\$(\d+(?:\.\d+)?)|\$(\d+(?:\.\d+)?)\s+Allowance)", re.IGNORECASE)

# Pattern for identifying safety eyewear sections (to skip)
SAFETY_EYEWEAR_PATTERN = re.compile(r"(?:SAFETY\s+EYEWEAR|Safety\s+Glasses|SAFETY\s+GLASSES)", re.IGNORECASE)

# Pattern for identifying post-cataract sections (to skip)
POST_CATARACT_PATTERN = re.compile(r"(?:POST\-CATARACT|Post\s+Cataract)", re.IGNORECASE)

# Pattern for identifying maternity sections
MATERNITY_PATTERN = re.compile(r"(?:MATERNITY|Maternity\s+Benefits|MATERNITY\s+BENEFIT)", re.IGNORECASE)

# Functions for pattern matching
def find_section_start(text: str, section_pattern: Pattern) -> Optional[int]:
    """
    Find the starting position of a section in the document text.
    
    Args:
        text: The document text
        section_pattern: Compiled regex pattern for the section header
        
    Returns:
        Start position of the section or None if not found
    """
    match = section_pattern.search(text)
    if match:
        return match.start()
    return None


def find_section_text(text: str, section_start_pattern: Pattern, 
                      section_end_patterns: List[Pattern]) -> Optional[str]:
    """
    Extract the text of a specific section from the document.
    
    Args:
        text: The document text
        section_start_pattern: Compiled regex pattern for the section header
        section_end_patterns: List of compiled regex patterns that may indicate section end
        
    Returns:
        Extracted section text or None if section not found
    """
    # Find section start
    start_match = section_start_pattern.search(text)
    if not start_match:
        return None
    
    start_pos = start_match.end()
    end_pos = len(text)
    
    # Find the nearest end pattern match
    for end_pattern in section_end_patterns:
        end_match = end_pattern.search(text, start_pos)
        if end_match and end_match.start() < end_pos:
            end_pos = end_match.start()
    
    return text[start_pos:end_pos].strip()


def extract_table_rows(section_text: str) -> List[Tuple[str, str]]:
    """
    Extract rows from a table section as (service, responsibility) pairs.
    
    Args:
        section_text: The section text containing the table
        
    Returns:
        List of (service, responsibility) tuples
    """
    rows = []
    lines = section_text.split('\n')
    
    # Skip the table header line(s)
    start_line = 0
    for i, line in enumerate(lines):
        if TABLE_HEADER_PATTERN.search(line):
            start_line = i + 1
            break
    
    # Process each line as a potential table row
    for line in lines[start_line:]:
        match = TABLE_ROW_PATTERN.search(line.strip())
        if match:
            service = match.group(1).strip()
            responsibility = match.group(2).strip()
            rows.append((service, responsibility))
    
    return rows


def extract_age_specific_values(responsibility: str) -> Dict[str, str]:
    """
    Extract age-specific responsibility values.
    
    Args:
        responsibility: The responsibility text
        
    Returns:
        Dictionary mapping age range to value
    """
    result = {}
    
    # Check for children/adult specific values (e.g., "Covered-in-Full for Ages 0-18" and "$33.00 for Ages 19+")
    child_match = re.search(r"(.+?)\s+for\s+Ages\s+(\d+)\-(\d+)", responsibility, re.IGNORECASE)
    adult_match = re.search(r"(.+?)\s+for\s+Ages\s+(\d+)\+", responsibility, re.IGNORECASE)
    
    if child_match:
        child_value = child_match.group(1).strip()
        min_age = child_match.group(2)
        max_age = child_match.group(3)
        result[f"ages_{min_age}_{max_age}"] = child_value
    
    if adult_match:
        adult_value = adult_match.group(1).strip()
        min_age = adult_match.group(2)
        result[f"ages_{min_age}_plus"] = adult_value
    
    return result


def extract_money_value(text: str) -> Optional[float]:
    """
    Extract a dollar amount from text.
    
    Args:
        text: Text containing potential dollar amount
        
    Returns:
        Extracted dollar amount as float or None
    """
    match = DOLLAR_AMOUNT_PATTERN.search(text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None


def extract_percentage(text: str) -> Optional[int]:
    """
    Extract a percentage value from text.
    
    Args:
        text: Text containing potential percentage
        
    Returns:
        Extracted percentage as integer or None
    """
    match = PERCENTAGE_PATTERN.search(text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def extract_allowance(text: str) -> Optional[float]:
    """
    Extract an allowance amount from text.
    
    Args:
        text: Text containing potential allowance
        
    Returns:
        Extracted allowance as float or None
    """
    match = ALLOWANCE_PATTERN.search(text)
    if match:
        try:
            value = match.group(1) or match.group(2)
            return float(value)
        except (ValueError, IndexError):
            pass
    return None


def extract_quantity(text: str) -> Optional[int]:
    """
    Extract a quantity value from text.
    
    Args:
        text: Text containing potential quantity
        
    Returns:
        Extracted quantity as integer or None
    """
    match = QUANTITY_PATTERN.search(text)
    if match:
        try:
            value = match.group(1) or match.group(2)
            return int(value)
        except (ValueError, IndexError):
            pass
    return None 