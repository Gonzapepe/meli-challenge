CLASSIFICATION_PROMPT = """You are an expert in data privacy regulations (GDPR, HIPAA, PCI DSS).

Classify this detected entity:

Entity Value: {entity_value}
Entity Type: {entity_type}
Context from regulations: {regulation_context}

Provide classification in JSON format:
{{
    "entity_type_refined": "specific type (e.g., person_name, patient_name, cardholder_name, email, etc.)",
    "sensitivity_level": "low|medium|high|critical",
    "applicable_regulations": ["GDPR", "HIPAA", "PCI DSS"],
    "justification": "Brief explanation citing specific articles"
}}

Classification guidelines:
- CRITICAL: CVV, PAN (credit card), SSN, medical record numbers
- HIGH: Names, addresses, national IDs, email, phone
- MEDIUM: Dates, organizations, job titles
- LOW: General location (city/country level)

Respond with JSON only."""


JUSTIFICATION_PROMPT = """Generate a justification for this anonymization decision:

Entity: {entity_value}
Type: {entity_type}
Sensitivity: {sensitivity_level}
Regulation: {regulation}
Technique Applied: {technique}
Regulation Article: {article}

Generate a 2-3 sentence justification that:
1. Cites the specific regulation article
2. Explains why this entity needs protection
3. Justifies why this technique is appropriate

Respond in professional, concise language."""


QUALITY_CHECK_PROMPT = """Review this anonymized text for any remaining sensitive data:

ANONYMIZED TEXT:
{anonymized_text}

Check for:
1. Any remaining personal names
2. Email addresses or phone numbers
3. Credit card numbers or financial data
4. Medical information that could identify patients
5. Any other PII/PHI/PCI data

Respond with JSON:
{{
    "contains_pii": true/false,
    "issues": ["list of any detected sensitive data still present"],
    "confidence": 0.0-1.0
}}

Be thorough but avoid false positives on properly anonymized tokens like [PATIENT] or Subject-001."""


REGULATION_DETECTION_PROMPT = """Analyze this text to determine which data protection regulations apply:

TEXT:
{text}

Detected entity types: {entity_types}

Consider:
- GDPR: Personal data of EU/Chilean citizens (emails, names, addresses, national IDs)
- HIPAA: Protected health information (patient data, diagnoses, medical records)
- PCI DSS: Payment card data (credit card numbers, CVV, cardholder info)

Respond with JSON:
{{
    "applicable_regulations": ["GDPR", "HIPAA", "PCI DSS"],
    "primary_regulation": "most restrictive regulation",
    "reasoning": "brief explanation"
}}"""
