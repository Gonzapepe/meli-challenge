import json
import re
from typing import List, Optional
from src.schemas.entities import DetectedEntity, DetectionMethod


NER_PROMPT = """You are an expert in identifying personally identifiable information (PII), protected health information (PHI), and payment card information (PCI).

Analyze this text and extract ALL sensitive entities:

TEXT:
{text}

ENTITY CATEGORIES TO DETECT:
- Person names (full names, first/last names)
- Geographic locations (addresses, cities, countries)
- Medical information (diagnoses, conditions, medications, procedures)
- Organizations (companies, hospitals, institutions)
- Job titles and professional roles
- Any other personally identifiable information

RESPOND WITH JSON ARRAY ONLY (no markdown, no explanation):
[
    {{
        "value": "exact text extracted",
        "type": "category name (person_name, address, organization, medical_diagnosis, medication, job_title, physician_name, patient_name)",
        "context": "brief explanation of why this is sensitive"
    }}
]

Be thorough. Extract every sensitive piece of information. The text is in Spanish."""


def consolidate_llm_entities(entities: List[DetectedEntity]) -> List[DetectedEntity]:
    """
    Remove self-overlapping entities from LLM detection, keeping the most specific.
    """
    if not entities:
        return []
    
    type_priority = {
        "physician_name": 1,
        "patient_name": 1,
        "person_name": 2,
        "organization": 3,
        "job_title": 3,
        "address": 4,
    }
    
    sorted_entities = sorted(
        entities,
        key=lambda e: (
            e.start,
            type_priority.get(e.entity_type, 10),
            -(e.end - e.start)
        )
    )
    
    consolidated = []
    last_end = -1
    
    for entity in sorted_entities:
        if entity.start >= last_end:
            consolidated.append(entity)
            last_end = entity.end
        elif entity.end <= last_end:
            continue
        else:
            if consolidated:
                last_entity = consolidated[-1]
                current_priority = type_priority.get(entity.entity_type, 10)
                last_priority = type_priority.get(last_entity.entity_type, 10)
                current_span = entity.end - entity.start
                last_span = last_entity.end - last_entity.start
                
                if current_priority < last_priority or (
                    current_priority == last_priority and current_span > last_span
                ):
                    consolidated[-1] = entity
                    last_end = entity.end
    
    return consolidated


def extract_entities_with_llm(
    text: str,
    llm_client,
    model: str = "llama-3.1-70b-versatile"
) -> List[DetectedEntity]:
    """
    Extract contextual entities using LLM.
    
    Args:
        text: Input text to analyze
        llm_client: Groq client instance
        model: Model to use for extraction
        
    Returns:
        List of detected entities
    """
    try:
        response = llm_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in PII/PHI/PCI detection. Always respond with valid JSON array only."
                },
                {
                    "role": "user",
                    "content": NER_PROMPT.format(text=text)
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        
        entities_data = _parse_llm_response(content)
        
        entities = []
        for entity_data in entities_data:
            start, end = _find_entity_position(text, entity_data["value"])
            
            if start >= 0:
                entities.append(DetectedEntity(
                    value=entity_data["value"],
                    entity_type=entity_data.get("type", "unknown"),
                    start=start,
                    end=end,
                    detection_method=DetectionMethod.LLM,
                    confidence=0.85
                ))
        
        consolidated_entities = consolidate_llm_entities(entities)
        return consolidated_entities
        
    except Exception as e:
        print(f"LLM detection error: {e}")
        return []


def _parse_llm_response(content: str) -> List[dict]:
    """Parse LLM response, handling potential markdown code blocks."""
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r'^```\w*\n?', '', content)
        content = re.sub(r'\n?```$', '', content)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return []


def _find_entity_position(text: str, entity_value: str) -> tuple[int, int]:
    """
    Find the position of an entity value in the text.
    
    Returns:
        Tuple of (start, end) positions, or (-1, -1) if not found
    """
    start = text.find(entity_value)
    if start >= 0:
        return start, start + len(entity_value)
    
    text_lower = text.lower()
    value_lower = entity_value.lower()
    start = text_lower.find(value_lower)
    if start >= 0:
        return start, start + len(entity_value)
    
    return -1, -1


def merge_entities(
    regex_entities: List[DetectedEntity],
    llm_entities: List[DetectedEntity]
) -> List[DetectedEntity]:
    """
    Combine deterministic and LLM detections.
    Regex takes precedence for overlapping structured data.
    
    Args:
        regex_entities: Entities from regex detection
        llm_entities: Entities from LLM detection
        
    Returns:
        Merged list of unique entities
    """
    all_entities = regex_entities.copy()
    
    for llm_entity in llm_entities:
        overlaps = False
        for regex_entity in regex_entities:
            if _entities_overlap(llm_entity, regex_entity):
                overlaps = True
                break
        
        if not overlaps:
            all_entities.append(llm_entity)
    
    return all_entities


def _entities_overlap(e1: DetectedEntity, e2: DetectedEntity) -> bool:
    """Check if two entities overlap in text position."""
    return not (e1.end <= e2.start or e2.end <= e1.start)
