from typing import TypedDict, List, Set, Optional, Dict, Any
from src.schemas.entities import DetectedEntity, ClassifiedEntity, Regulation


class WorkflowState(TypedDict, total=False):
    """State passed between LangGraph nodes."""
    
    raw_text: str
    text_id: str
    detected_entities: List[DetectedEntity]
    
    classified_entities: List[ClassifiedEntity]
    regulation_flags: Set[Regulation]
    primary_regulation: Regulation
    
    anonymization_strategies: Dict[str, Dict[str, Any]]
    policy_context: List[str]
    
    anonymized_text: str
    transformation_log: List[Dict[str, Any]]
    justifications: List[Dict[str, str]]
    
    quality_passed: bool
    issues_found: List[str]
    retry_count: int
    
    processing_time_ms: int
    error: Optional[str]
