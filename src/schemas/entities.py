from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SensitivityLevel(str, Enum):
    """Sensitivity classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Regulation(str, Enum):
    """Supported data protection regulations."""
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI DSS"


class DetectionMethod(str, Enum):
    """How the entity was detected."""
    REGEX = "regex"
    LLM = "llm"


class DetectedEntity(BaseModel):
    """Entity detected in text before classification."""
    value: str = Field(..., description="The detected value")
    entity_type: str = Field(..., description="Type of entity (email, name, etc.)")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    detection_method: DetectionMethod = Field(..., description="How it was detected")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ClassifiedEntity(BaseModel):
    """Entity after classification with regulation info."""
    value_detected: str = Field(..., description="Original detected value")
    entity_type: str = Field(..., description="Refined entity type")
    sensitivity_level: SensitivityLevel = Field(..., description="Sensitivity classification")
    applicable_regulations: List[Regulation] = Field(default_factory=list)
    justification_citations: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")


class AnonymizationStrategy(BaseModel):
    """Strategy for anonymizing a specific entity."""
    entity_value: str
    technique: str = Field(..., description="Anonymization technique to apply")
    regulation_article: Optional[str] = None
    justification: str = Field(default="")
