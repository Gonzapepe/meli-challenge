from typing import Dict, List
from src.schemas.entities import Regulation


GDPR_STRATEGIES: Dict[str, Dict] = {
    "person_name": {
        "technique": "pseudonymization",
        "article": "GDPR Art. 4(5)",
        "justification": "Pseudonymization prevents attribution without additional info"
    },
    "email": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Pseudonymization as security measure while preserving domain structure"
    },
    "phone_chile": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Preserve country code, mask personal digits"
    },
    "phone_intl": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Preserve country code, mask personal digits"
    },
    "address": {
        "technique": "generalization",
        "article": "GDPR Art. 5(1)(c)",
        "justification": "Data minimization - reduce precision while maintaining regional utility"
    },
    "rut_chile": {
        "technique": "tokenization",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "High sensitivity national ID, enable reversibility if needed"
    },
    "date_dmy": {
        "technique": "generalization",
        "article": "GDPR Art. 5(1)(c)",
        "justification": "Data minimization, year sufficient for demographics"
    },
    "date_ymd": {
        "technique": "generalization",
        "article": "GDPR Art. 5(1)(c)",
        "justification": "Data minimization, year sufficient for demographics"
    },
    "organization": {
        "technique": "pseudonymization",
        "article": "GDPR Art. 4(5)",
        "justification": "Organization names can be indirect identifiers"
    },
}

HIPAA_STRATEGIES: Dict[str, Dict] = {
    "patient_name": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(A)",
        "justification": "Safe Harbor identifier #1 - names must be removed"
    },
    "person_name": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(A)",
        "justification": "Safe Harbor identifier #1 - names must be removed"
    },
    "physician_name": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(A)",
        "justification": "Safe Harbor identifier #1 - names must be removed"
    },
    "email": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(F)",
        "justification": "Safe Harbor identifier #6 - email addresses"
    },
    "phone_chile": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(D)",
        "justification": "Safe Harbor identifier #4 - telephone numbers"
    },
    "phone_intl": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(D)",
        "justification": "Safe Harbor identifier #4 - telephone numbers"
    },
    "date_dmy": {
        "technique": "generalization",
        "article": "HIPAA §164.514(b)(2)(i)(C)",
        "justification": "Safe Harbor #3 - dates except year"
    },
    "date_ymd": {
        "technique": "generalization",
        "article": "HIPAA §164.514(b)(2)(i)(C)",
        "justification": "Safe Harbor #3 - dates except year"
    },
    "address": {
        "technique": "removal",
        "article": "HIPAA §164.514(b)(2)(i)(B)",
        "justification": "Safe Harbor #2 - geographic subdivisions smaller than state"
    },
    "medical_diagnosis": {
        "technique": "keep",
        "article": "HIPAA §164.514(b)(2)",
        "justification": "Clinical data needed for research, not a direct identifier"
    },
    "medication": {
        "technique": "keep",
        "article": "HIPAA §164.514(b)(2)",
        "justification": "Clinical data, cannot identify individual without additional info"
    },
}

PCI_DSS_STRATEGIES: Dict[str, Dict] = {
    "credit_card": {
        "technique": "truncation",
        "article": "PCI DSS Req. 3.4",
        "justification": "PAN must be rendered unreadable - show only last 4 digits"
    },
    "cvv": {
        "technique": "removal",
        "article": "PCI DSS Req. 3.2",
        "justification": "CVV/CVC must NEVER be stored after authorization"
    },
    "expiry_date": {
        "technique": "tokenization",
        "article": "PCI DSS Req. 3.4",
        "justification": "Sensitive authentication data should be tokenized"
    },
    "person_name": {
        "technique": "pseudonymization",
        "article": "GDPR Art. 4(5) + PCI DSS context",
        "justification": "Cardholder name - apply GDPR pseudonymization"
    },
    "email": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Apply GDPR masking for contact data"
    },
    "phone_chile": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Apply GDPR masking for contact data"
    },
    "phone_intl": {
        "technique": "masking",
        "article": "GDPR Art. 32(1)(a)",
        "justification": "Apply GDPR masking for contact data"
    },
    "address": {
        "technique": "generalization",
        "article": "GDPR Art. 5(1)(c)",
        "justification": "Billing address - apply GDPR generalization"
    },
}


def get_strategy_for_entity(
    entity_type: str,
    regulation: Regulation
) -> Dict:
    """
    Get the anonymization strategy for a given entity type and regulation.
    
    Args:
        entity_type: Type of entity
        regulation: Applicable regulation
        
    Returns:
        Strategy dict with technique, article, and justification
    """
    strategy_maps = {
        Regulation.GDPR: GDPR_STRATEGIES,
        Regulation.HIPAA: HIPAA_STRATEGIES,
        Regulation.PCI_DSS: PCI_DSS_STRATEGIES,
    }
    
    strategies = strategy_maps.get(regulation, GDPR_STRATEGIES)
    
    if entity_type in strategies:
        return strategies[entity_type]
    
    defaults = {
        Regulation.GDPR: {
            "technique": "pseudonymization",
            "article": "GDPR Art. 4(5)",
            "justification": "Default pseudonymization for unspecified entity types"
        },
        Regulation.HIPAA: {
            "technique": "removal",
            "article": "HIPAA §164.514(b)(2)",
            "justification": "Default removal for potential PHI"
        },
        Regulation.PCI_DSS: {
            "technique": "tokenization",
            "article": "PCI DSS Req. 3.4",
            "justification": "Default tokenization for payment-related data"
        },
    }
    
    return defaults.get(regulation, defaults[Regulation.GDPR])


def get_all_strategies(regulation: Regulation) -> Dict[str, Dict]:
    """Get all strategies for a regulation."""
    strategy_maps = {
        Regulation.GDPR: GDPR_STRATEGIES,
        Regulation.HIPAA: HIPAA_STRATEGIES,
        Regulation.PCI_DSS: PCI_DSS_STRATEGIES,
    }
    return strategy_maps.get(regulation, GDPR_STRATEGIES)
