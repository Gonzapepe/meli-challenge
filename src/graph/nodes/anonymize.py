"""Anonymize node - apply transformations to create anonymized text."""

from typing import Dict, Any, List
from src.graph.state import WorkflowState
from src.anonymization.techniques import apply_technique, reset_pseudonym_counter
from src.schemas.entities import ClassifiedEntity


def filter_overlapping_entities(entities: List[ClassifiedEntity]) -> List[ClassifiedEntity]:
    """
    Keep only the largest entity when overlaps occur.
    Args:
        entities: List of classified entities that may overlap
        
    Returns:
        Filtered list with no overlaps (larger spans preferred)
    """
    if not entities:
        return []
    
    sorted_entities = sorted(
        entities,
        key=lambda e: (e.start, -(e.end - e.start))
    )
    
    filtered = []
    last_end = -1
    
    for entity in sorted_entities:
        if entity.start >= last_end:
            filtered.append(entity)
            last_end = entity.end
        elif entity.end <= last_end:
            continue
        else:
            if filtered and (entity.end - entity.start) > (filtered[-1].end - filtered[-1].start):
                filtered[-1] = entity
                last_end = entity.end
    
    return filtered


def anonymize_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Apply anonymization transformations to the text.
    
    Processing:
    1. Filter overlapping entities (keep largest spans)
    2. Sort entities by position (reverse order)
    3. Apply transformations sequentially
    4. Log all transformations
    """
    raw_text = state["raw_text"]
    classified_entities = state["classified_entities"]
    strategies = state["anonymization_strategies"]
    
    reset_pseudonym_counter()
    
    anonymized = raw_text
    transformation_log: List[Dict[str, Any]] = []
    
    filtered_entities = filter_overlapping_entities(classified_entities)
    
    sorted_entities = sorted(
        filtered_entities,
        key=lambda e: e.start,
        reverse=True
    )
    
    for entity in sorted_entities:
        value = entity.value_detected
        
        if value in strategies:
            strategy = strategies[value]
            technique = strategy["technique"]
        else:
            technique = "pseudonymization"
        
        if technique == "keep":
            transformation_log.append({
                "original": value,
                "anonymized": value,
                "technique": "keep",
                "entity_type": entity.entity_type,
                "position": entity.start,
                "kept_reason": "Clinical data, not a direct identifier"
            })
            continue
        
        replacement = apply_technique(value, entity.entity_type, technique)
        
        anonymized = (
            anonymized[:entity.start] +
            replacement +
            anonymized[entity.end:]
        )
        
        transformation_log.append({
            "original": value,
            "anonymized": replacement,
            "technique": technique,
            "entity_type": entity.entity_type,
            "position": entity.start
        })
    
    return {
        "anonymized_text": anonymized,
        "transformation_log": transformation_log
    }
