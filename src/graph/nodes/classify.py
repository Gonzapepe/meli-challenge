import json
from typing import Dict, Any, List, Set
from src.graph.state import WorkflowState
from src.schemas.entities import ClassifiedEntity, Regulation, SensitivityLevel
from src.llm.groq_client import generate_json_completion
from src.llm.prompts import CLASSIFICATION_PROMPT

QUICK_CLASSIFICATION = {
    "email": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "phone": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "credit_card": {
        "sensitivity": SensitivityLevel.CRITICAL,
        "regulations": [Regulation.PCI_DSS, Regulation.GDPR]
    },
    "cvv": {
        "sensitivity": SensitivityLevel.CRITICAL,
        "regulations": [Regulation.PCI_DSS]
    },
    "expiry_date": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.PCI_DSS]
    },
    "account_number": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "rut_chile": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "date_dmy": {
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "date_ymd": {
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "birthdate": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "admission_date": {
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.HIPAA]
    },
    "discharge_date": {
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.HIPAA]
    },
    "death_date": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.HIPAA]
    },
    
    "person_name": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "medical_diagnosis": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.HIPAA]
    },
    "medication": {
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.HIPAA]
    },
    "medical_record_number": { 
        "sensitivity": SensitivityLevel.CRITICAL,
        "regulations": [Regulation.HIPAA]
    },
    "health_plan_number": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.HIPAA]
    },
    
    "address": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "zip_code": { 
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "ip_address": { 
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "url": { 
        "sensitivity": SensitivityLevel.LOW,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "device_identifier": { 
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    
    "biometric_identifier": { 
        "sensitivity": SensitivityLevel.CRITICAL,
        "regulations": [Regulation.HIPAA]
    },
    "facial_image": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.HIPAA]
    },
    
    "certificate_number": { 
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.HIPAA]
    },
    "license_plate": { 
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.HIPAA]
    },
    
    "organization": {
        "sensitivity": SensitivityLevel.MEDIUM,
        "regulations": [Regulation.GDPR]
    },
    "job_title": {
        "sensitivity": SensitivityLevel.LOW,
        "regulations": [Regulation.GDPR]
    },
    
    "phone_chile": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
    "phone_intl": { 
        "sensitivity": SensitivityLevel.HIGH,
        "regulations": [Regulation.GDPR, Regulation.HIPAA]
    },
}


def classify_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Classify detected entities and determine applicable regulations.
    
    Uses:
    1. Quick rules for known entity types
    2. LLM for unknown/contextual entities
    """
    detected_entities = state["detected_entities"]
    classified_entities: List[ClassifiedEntity] = []
    regulation_flags: Set[Regulation] = set()
    entity_types: Set[str] = set()
    
    for entity in detected_entities:
        entity_type = entity.entity_type
        entity_types.add(entity_type)
        
        if entity_type in QUICK_CLASSIFICATION:
            quick_class = QUICK_CLASSIFICATION[entity_type]
            classified = ClassifiedEntity(
                value_detected=entity.value,
                entity_type=entity_type,
                sensitivity_level=quick_class["sensitivity"],
                applicable_regulations=quick_class["regulations"],
                justification_citations=[],
                confidence=entity.confidence,
                start=entity.start,
                end=entity.end
            )
        else:
            classified = _classify_with_llm(entity)
        
        classified_entities.append(classified)
        regulation_flags.update(classified.applicable_regulations)
    
    primary_regulation = _determine_primary_regulation(regulation_flags, entity_types)
    
    return {
        "classified_entities": classified_entities,
        "regulation_flags": regulation_flags,
        "primary_regulation": primary_regulation
    }


def _classify_with_llm(entity) -> ClassifiedEntity:
    """Use LLM to classify unknown entity types."""
    try:
        prompt = CLASSIFICATION_PROMPT.format(
            entity_value=entity.value,
            entity_type=entity.entity_type,
            regulation_context="GDPR, HIPAA, PCI DSS general context"
        )
        
        response = generate_json_completion(prompt)
        data = json.loads(response)
        
        regs = []
        for reg_name in data.get("applicable_regulations", ["GDPR"]):
            if "GDPR" in reg_name:
                regs.append(Regulation.GDPR)
            elif "HIPAA" in reg_name:
                regs.append(Regulation.HIPAA)
            elif "PCI" in reg_name:
                regs.append(Regulation.PCI_DSS)
        
        sensitivity_map = {
            "low": SensitivityLevel.LOW,
            "medium": SensitivityLevel.MEDIUM,
            "high": SensitivityLevel.HIGH,
            "critical": SensitivityLevel.CRITICAL
        }
        sensitivity = sensitivity_map.get(
            data.get("sensitivity_level", "high").lower(),
            SensitivityLevel.HIGH
        )
        
        return ClassifiedEntity(
            value_detected=entity.value,
            entity_type=data.get("entity_type_refined", entity.entity_type),
            sensitivity_level=sensitivity,
            applicable_regulations=regs or [Regulation.GDPR],
            justification_citations=[data.get("justification", "")],
            confidence=0.85,
            start=entity.start,
            end=entity.end
        )
    except Exception as e:
        print(f"LLM classification failed: {e}")

        return ClassifiedEntity(
            value_detected=entity.value,
            entity_type=entity.entity_type,
            sensitivity_level=SensitivityLevel.HIGH,
            applicable_regulations=[Regulation.GDPR],
            justification_citations=[],
            confidence=0.5,
            start=entity.start,
            end=entity.end
        )


def _determine_primary_regulation(flags: Set[Regulation], entity_types: Set[str]) -> Regulation:
    """
    Determine the primary (most restrictive) regulation.
    
    Priority order:
    1. PCI DSS - Only if actual payment card data (credit_card or CVV) is present
       (not just expiry_date, which could be a false positive)
    2. HIPAA - Only if health-related/medical identifiers are actually present
       (not just general personal data shared between GDPR/HIPAA)
    3. GDPR - Default for general personal data
    
    Args:
        flags: Set of all applicable regulations
        entity_types: Set of entity types that were actually detected
        
    Returns:
        The primary regulation to apply
    """
    pci_core_entities = {"credit_card", "cvv"}
    
    hipaa_specific_entities = {
        "medical_diagnosis", "medication", "medical_record_number", 
        "health_plan_number", "biometric_identifier", "facial_image",
        "admission_date", "discharge_date", "death_date", "patient_name"
    }
    
    if Regulation.PCI_DSS in flags and pci_core_entities.intersection(entity_types):
        return Regulation.PCI_DSS
    
    if Regulation.HIPAA in flags and hipaa_specific_entities.intersection(entity_types):
        return Regulation.HIPAA
    
    return Regulation.GDPR
