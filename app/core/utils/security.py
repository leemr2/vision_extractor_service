"""
Security utility functions for handling sensitive data
"""

import re
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)


async def redact_phi(text: str) -> str:
    """
    Redact potentially sensitive Protected Health Information (PHI) from extracted text
    
    Args:
        text: The text to redact
        
    Returns:
        Redacted text with sensitive information removed or masked
    """
    if not text:
        return ""
    
    # Redact social security numbers
    text = redact_ssn(text)
    
    # Redact dates of birth
    text = redact_dob(text)
    
    # Redact patient names (this would be more sophisticated in a real implementation)
    text = redact_patient_names(text)
    
    # Redact other PHI (addresses, phone numbers, etc.)
    text = redact_contact_info(text)
    
    return text


def redact_ssn(text: str) -> str:
    """
    Redact Social Security Numbers from text.
    
    Args:
        text: Text that may contain SSNs
        
    Returns:
        Text with SSNs redacted
    """
    # Pattern for SSN like XXX-XX-XXXX or XXXXXXXXX
    ssn_pattern = r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
    return re.sub(ssn_pattern, '[REDACTED_SSN]', text)


def redact_dob(text: str) -> str:
    """
    Redact dates of birth from text.
    
    Args:
        text: Text that may contain dates of birth
        
    Returns:
        Text with dates of birth redacted
    """
    # Look for common DOB patterns
    dob_patterns = [
        r'\b(?:DOB|Date\s+of\s+Birth|Birth\s+Date):?\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\s*(?:DOB|Date\s+of\s+Birth|Birth\s+Date)',
        r'\b(?:Born\s+on):?\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
    ]
    
    for pattern in dob_patterns:
        text = re.sub(pattern, '[REDACTED_DOB]', text, flags=re.IGNORECASE)
    
    return text


def redact_patient_names(text: str) -> str:
    """
    Redact patient names from text.
    
    Args:
        text: Text that may contain patient names
        
    Returns:
        Text with patient names redacted
    """
    # This is a simplified implementation
    # In a real system, would use NER (Named Entity Recognition) to identify names
    
    # Look for common patterns indicating a patient name
    name_patterns = [
        r'(?:Patient\s+Name|Name):?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'(?:Patient):?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
    ]
    
    for pattern in name_patterns:
        text = re.sub(pattern, r'Patient: [REDACTED_NAME]', text, flags=re.IGNORECASE)
    
    return text


def redact_contact_info(text: str) -> str:
    """
    Redact contact information from text.
    
    Args:
        text: Text that may contain contact information
        
    Returns:
        Text with contact information redacted
    """
    # Redact phone numbers
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, '[REDACTED_PHONE]', text)
    
    # Redact email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[REDACTED_EMAIL]', text)
    
    # Redact addresses (simplified)
    address_patterns = [
        r'\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Circle|Cir|Place|Pl)\b',
        r'(?:Address):?\s*\d+\s+[A-Za-z\s,]+\d{5}',
    ]
    
    for pattern in address_patterns:
        text = re.sub(pattern, '[REDACTED_ADDRESS]', text, flags=re.IGNORECASE)
    
    return text


def encrypt_patient_id(patient_id: str) -> str:
    """
    Encrypt a patient ID for secure storage (placeholder).
    
    Args:
        patient_id: The patient ID to encrypt
        
    Returns:
        Encrypted patient ID
    """
    # This is a placeholder for a real encryption implementation
    # In a real system, you would use proper cryptographic methods
    return f"ENCRYPTED_{patient_id}_ENCRYPTED"


def decrypt_patient_id(encrypted_id: str) -> str:
    """
    Decrypt an encrypted patient ID (placeholder).
    
    Args:
        encrypted_id: The encrypted patient ID
        
    Returns:
        Decrypted patient ID
    """
    # This is a placeholder for a real decryption implementation
    # In a real system, you would use proper cryptographic methods
    if encrypted_id.startswith("ENCRYPTED_") and encrypted_id.endswith("_ENCRYPTED"):
        return encrypted_id[10:-10]
    return encrypted_id 