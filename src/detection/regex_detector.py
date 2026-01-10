import re
from typing import List, Dict, Tuple
from src.schemas.entities import DetectedEntity, DetectionMethod

REGEX_PATTERNS: Dict[str, str] = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    
    "phone": r'\+?\d{1,3}[\s\.-]?\(?\d{2,4}\)?[\s\.-]?\d{3,4}[\s\.-]?\d{3,4}',
    
    "credit_card": r'\b\d{4}[\s\.-]?\d{4}[\s\.-]?\d{4}[\s\.-]?\d{4}\b',
    "expiry_date": r'(?<!\d/)\b(0[1-9]|1[0-2])/(\d{2}|\d{4})\b(?!/)',
    
    "rut_chile": r'\b\d{1,2}\.\d{3}\.\d{3}-[\dkK]\b',
    "ssn_us": r'\b\d{3}-\d{2}-\d{4}\b',
    
    "date_dmy": r'\b\d{2}/\d{2}/\d{4}\b',
    "date_ymd": r'\b\d{4}-\d{2}-\d{2}\b',
    
    "zip_code": r'\b\d{5}(?:-\d{4})?\b',
    
    "ip_address": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    
    "url": r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
    
    "account_number": r'\b(?:ACC|ACCT|Account)[\s#:]*\d{8,17}\b',
    
    "device_identifier": r'\b(?:[0-9A-F]{2}[:-]){5}(?:[0-9A-F]{2})|(?:SN|Serial)[\s#:]*[A-Z0-9]{8,20}\b',
}

CVV_CONTEXT_KEYWORDS = ["cvv", "cvc", "código de seguridad", "security code"]


def detect_with_regex(text: str) -> List[DetectedEntity]:
    """
    Detect entities using deterministic regex patterns.
    
    Args:
        text: Input text to scan for entities
        
    Returns:
        List of detected entities with positions
    """
    entities: List[DetectedEntity] = []
    
    for entity_type, pattern in REGEX_PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(DetectedEntity(
                value=match.group(),
                entity_type=entity_type,
                start=match.start(),
                end=match.end(),
                detection_method=DetectionMethod.REGEX,
                confidence=1.0
            ))
    
    entities.extend(_detect_cvv_in_context(text))
    
    return entities


def _detect_cvv_in_context(text: str) -> List[DetectedEntity]:
    """
    Detect CVV only when it appears near payment-related keywords.
    
    This prevents false positives on random 3-4 digit numbers.
    """
    entities: List[DetectedEntity] = []
    text_lower = text.lower()
    
    for keyword in CVV_CONTEXT_KEYWORDS:
        if keyword in text_lower:
            keyword_pos = text_lower.find(keyword)
            
            search_region = text[keyword_pos:keyword_pos + 50]
            cvv_pattern = r'\b\d{3,4}\b'
            
            for match in re.finditer(cvv_pattern, search_region):
                actual_start = keyword_pos + match.start()
                actual_end = keyword_pos + match.end()
                
                entities.append(DetectedEntity(
                    value=match.group(),
                    entity_type="cvv",
                    start=actual_start,
                    end=actual_end,
                    detection_method=DetectionMethod.REGEX,
                    confidence=0.95
                ))
    
    return entities


def get_supported_patterns() -> Dict[str, str]:
    """Return all supported regex patterns."""
    return REGEX_PATTERNS.copy()
