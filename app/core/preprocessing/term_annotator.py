"""
Term recognition and annotation for insurance terminology
"""
from typing import Dict, Any, List
import re

from app.core.models.insurance_types import InsuranceProvider
from app.config.term_dictionary import TERM_DICTIONARY


def annotate_terms(document_structure: Dict[str, Any], provider: InsuranceProvider) -> Dict[str, Any]:
    """
    Recognize and annotate insurance terminology in document
    
    Args:
        document_structure: Document structure with sections
        provider: Detected insurance provider
        
    Returns:
        Document structure with annotated terms
    """
    # Make a copy to avoid modifying original
    annotated_structure = document_structure.copy()
    
    # Annotate terms in each section
    sections = annotated_structure.get("sections", [])
    for i, section in enumerate(sections):
        sections[i] = _annotate_section(section, provider)
    
    return annotated_structure


def _annotate_section(section: Dict[str, Any], provider: InsuranceProvider) -> Dict[str, Any]:
    """
    Annotate terms in a single document section
    
    Args:
        section: Document section data
        provider: Detected insurance provider
        
    Returns:
        Section with annotated terms
    """
    annotated_section = section.copy()
    content = annotated_section.get("content", [])
    
    # Find and annotate terms in each line
    annotated_content = []
    for line in content:
        annotated_line = {
            "text": line,
            "annotations": _annotate_line(line, provider)
        }
        annotated_content.append(annotated_line)
    
    annotated_section["content"] = annotated_content
    return annotated_section


def _annotate_line(line: str, provider: InsuranceProvider) -> List[Dict[str, Any]]:
    """
    Annotate terms in a single line of text
    
    Args:
        line: Line of text
        provider: Detected insurance provider
        
    Returns:
        List of term annotations
    """
    annotations = []
    
    # Get provider-specific terms
    terms = TERM_DICTIONARY.get(provider, {})
    
    # Check each term category
    for category, category_terms in terms.items():
        for term_name, patterns in category_terms.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, line, re.IGNORECASE))
                for match in matches:
                    annotations.append({
                        "start": match.start(),
                        "end": match.end(),
                        "text": match.group(),
                        "category": category,
                        "term": term_name,
                        "normalized_term": term_name.lower().replace(" ", "_")
                    })
    
    return annotations 