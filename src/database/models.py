from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ProcessingLog(Base):
    """Entity for tracking individual data processing operations."""
    
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.current_timestamp(), nullable=False)
    text_id = Column(String, nullable=False, index=True)
    detected_entity = Column(Text, nullable=False)
    entity_type = Column(String, nullable=False, index=True)
    sensitivity_level = Column(String, nullable=True)
    applicable_regulations = Column(Text, nullable=True)
    applied_technique = Column(String, nullable=False)
    justification = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    original_value = Column(Text, nullable=True)
    anonymized_value = Column(Text, nullable=True)
    position_start = Column(Integer, nullable=True)
    position_end = Column(Integer, nullable=True)
    
    def __repr__(self):
        return (
            f"<ProcessingLog(id={self.id}, "
            f"entity_type='{self.entity_type}', "
            f"text_id='{self.text_id}')>"
        )
    
    def to_dict(self):
        """Convert entity to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'text_id': self.text_id,
            'detected_entity': self.detected_entity,
            'entity_type': self.entity_type,
            'sensitivity_level': self.sensitivity_level,
            'applicable_regulations': self.applicable_regulations,
            'applied_technique': self.applied_technique,
            'justification': self.justification,
            'confidence_score': self.confidence_score,
            'original_value': self.original_value,
            'anonymized_value': self.anonymized_value,
            'position_start': self.position_start,
            'position_end': self.position_end
        }


class RegulationRule(Base):
    """Entity for storing regulatory compliance rules."""
    
    __tablename__ = 'regulation_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String, nullable=False, index=True)
    regulation = Column(String, nullable=False)
    article_citation = Column(Text, nullable=True)
    required_technique = Column(String, nullable=False)
    sensitivity_level = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index('idx_entity_regulation', 'entity_type', 'regulation', unique=True),
    )
    
    def __repr__(self):
        return (
            f"<RegulationRule(id={self.id}, "
            f"entity_type='{self.entity_type}', "
            f"regulation='{self.regulation}')>"
        )
    
    def to_dict(self):
        """Convert entity to dictionary."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'regulation': self.regulation,
            'article_citation': self.article_citation,
            'required_technique': self.required_technique,
            'sensitivity_level': self.sensitivity_level,
            'description': self.description,
            'is_active': self.is_active
        }


class ProcessingSession(Base):
    """Entity for tracking text processing sessions."""
    
    __tablename__ = 'processing_sessions'
    
    session_id = Column(String, primary_key=True)
    text_id = Column(String, nullable=False)
    started_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default='in_progress', nullable=False)
    total_entities_detected = Column(Integer, default=0, nullable=False)
    total_entities_anonymized = Column(Integer, default=0, nullable=False)
    primary_regulation = Column(String, nullable=True)
    quality_check_passed = Column(Boolean, nullable=True)
    
    def __repr__(self):
        return (
            f"<ProcessingSession(session_id='{self.session_id}', "
            f"text_id='{self.text_id}', "
            f"status='{self.status}')>"
        )
    
    def to_dict(self):
        """Convert entity to dictionary."""
        return {
            'session_id': self.session_id,
            'text_id': self.text_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'total_entities_detected': self.total_entities_detected,
            'total_entities_anonymized': self.total_entities_anonymized,
            'primary_regulation': self.primary_regulation,
            'quality_check_passed': self.quality_check_passed
        }
