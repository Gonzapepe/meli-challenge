from typing import List, Dict, Any
from pydantic import BaseModel, Field


class EntityResult(BaseModel):
    """Single entity in the results output."""
    value_detected: str
    entity_type: str
    sensitivity_level: str
    applicable_regulations: List[str]
    justification_citations: List[str]
    action_taken: str
    anonymized_value: str


class ProcessingMetadata(BaseModel):
    """Metadata about the processing run."""
    processing_time_ms: int
    entities_detected: int
    techniques_applied: List[str]


class TextResult(BaseModel):
    """Result for a single processed text."""
    text_id: str
    regulation: str
    original_text: str
    anonymized_text: str
    entities: List[EntityResult]
    metadata: ProcessingMetadata


class ResultsOutput(BaseModel):
    """Complete results.json schema."""
    results: List[TextResult] = Field(default_factory=list)
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return self.model_dump()
