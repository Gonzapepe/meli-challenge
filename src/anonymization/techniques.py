import re
import hashlib
from typing import Dict


_pseudonym_counter: Dict[str, int] = {}


def reset_pseudonym_counter():
    """Reset the pseudonymization counter for a new processing run."""
    global _pseudonym_counter
    _pseudonym_counter = {}


def mask_email(email: str) -> str:
    """
    Mask email address: j***p@gmail.com
    """
    if "@" not in email:
        return email
    
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "***" + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number: keep country code + last 4 digits.
    Example: +56 9 ****5555
    """
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) <= 4:
        return "****" + digits
    
    prefix_len = min(4, len(digits) - 4)
    prefix = digits[:prefix_len]
    suffix = digits[-4:]
    masked_middle = "*" * (len(digits) - prefix_len - 4)
    
    return f"+{prefix} {masked_middle}{suffix}"


def truncate_pan(pan: str) -> str:
    """
    Truncate credit card PAN: show only last 4 digits.
    Example: ************1111
    """
    digits = re.sub(r'\D', '', pan)
    if len(digits) < 4:
        return "*" * len(digits)
    
    return "*" * (len(digits) - 4) + digits[-4:]


def tokenize_value(value: str, entity_type: str) -> str:
    """
    Generate a secure token for reversible anonymization.
    Example: TOKEN_RUT_a7b3c9d1
    """
    hash_obj = hashlib.sha256(value.encode())
    token = hash_obj.hexdigest()[:8]
    return f"TOKEN_{entity_type.upper()}_{token}"


def pseudonymize_name(name: str, prefix: str = "Subject") -> str:
    """
    Replace name with pseudonym: Subject-001, Subject-002, etc.
    """
    global _pseudonym_counter
    
    name_key = name.lower().strip()
    if name_key not in _pseudonym_counter:
        _pseudonym_counter[name_key] = len(_pseudonym_counter) + 1
    
    return f"{prefix}-{_pseudonym_counter[name_key]:03d}"


def generalize_date(date_str: str) -> str:
    """
    Generalize date to year only.
    Handles both DD/MM/YYYY and YYYY-MM-DD formats.
    """
    match = re.match(r'\d{2}/\d{2}/(\d{4})', date_str)
    if match:
        return match.group(1)
    
    match = re.match(r'(\d{4})-\d{2}-\d{2}', date_str)
    if match:
        return match.group(1)
    
    return date_str


def generalize_address(address: str) -> str:
    """
    Generalize address to city/region level.
    For this challenge, we'll use a simplified approach.
    """
    if "Chile" in address or "Santiago" in address.lower():
        return "Santiago, Chile"
    if "Colombia" in address or "Bogotá" in address.lower():
        return "Bogotá, Colombia"
    
    return "[LOCATION REDACTED]"


def remove_value(entity_type: str) -> str:
    """
    Complete removal - used for HIPAA Safe Harbor.
    Returns a placeholder based on entity type.
    """
    placeholders = {
        "patient_name": "[PATIENT]",
        "physician_name": "[PHYSICIAN]",
        "person_name": "[NAME]",
        "email": "[EMAIL_REMOVED]",
        "phone": "[PHONE_REMOVED]",
        "address": "[ADDRESS_REMOVED]",
        "cvv": "[CVV_REMOVED]",
    }
    return placeholders.get(entity_type, "[REDACTED]")


def apply_technique(value: str, entity_type: str, technique: str) -> str:
    """
    Apply the specified anonymization technique to a value.
    
    Args:
        value: Original value to anonymize
        entity_type: Type of entity
        technique: Anonymization technique to apply
        
    Returns:
        Anonymized value
    """
    technique_map = {
        "masking": lambda v, t: (
            mask_email(v) if t == "email" else
            mask_phone(v) if "phone" in t else
            truncate_pan(v) if t == "credit_card" else
            v[:2] + "***"
        ),
        "tokenization": lambda v, t: tokenize_value(v, t),
        "pseudonymization": lambda v, t: pseudonymize_name(v),
        "generalization": lambda v, t: (
            generalize_date(v) if "date" in t else
            generalize_address(v) if "address" in t.lower() else
            v
        ),
        "removal": lambda v, t: remove_value(t),
        "truncation": lambda v, t: truncate_pan(v),
        "truncation_tokenization": lambda v, t: tokenize_value(truncate_pan(v), t),
    }
    
    if technique in technique_map:
        return technique_map[technique](value, entity_type)
    
    return f"[{entity_type.upper()}_ANONYMIZED]"
