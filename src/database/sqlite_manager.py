from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, func, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from ..config import config
from .models import Base, ProcessingLog, RegulationRule, ProcessingSession


class SQLiteManager:
    """Manages SQLite database for audit logs and policy rules using SQLAlchemy ORM."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize SQLite manager with ORM.
        
        Args:
            db_path: Path to SQLite database file. Defaults to data/audit.db
        """
        self.db_path = db_path or config.DATA_DIR / "audit.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            echo=False,
            future=True
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self._init_database()
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions.
        
        Yields:
            SQLAlchemy Session object
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _init_database(self):
        """Initialize database schema using ORM models."""
        Base.metadata.create_all(bind=self.engine)
    
    def log_entity_processing(
        self,
        text_id: str,
        detected_entity: str,
        entity_type: str,
        applied_technique: str,
        **kwargs
    ) -> int:
        """Log a single entity processing action.
        
        Args:
            text_id: Identifier for the processed text
            detected_entity: The entity that was detected
            entity_type: Type of entity (email, credit_card, etc.)
            applied_technique: Anonymization technique applied
            **kwargs: Additional fields (justification, confidence_score, etc.)
        
        Returns:
            ID of the inserted log entry
        """
        with self.get_session() as session:
            log_entry = ProcessingLog(
                text_id=text_id,
                detected_entity=detected_entity,
                entity_type=entity_type,
                applied_technique=applied_technique,
                sensitivity_level=kwargs.get('sensitivity_level'),
                applicable_regulations=kwargs.get('applicable_regulations'),
                justification=kwargs.get('justification'),
                confidence_score=kwargs.get('confidence_score'),
                original_value=kwargs.get('original_value'),
                anonymized_value=kwargs.get('anonymized_value'),
                position_start=kwargs.get('position_start'),
                position_end=kwargs.get('position_end')
            )
            
            session.add(log_entry)
            session.flush()
            
            return log_entry.id
    
    def get_regulation_rule(
        self,
        entity_type: str,
        regulation: str
    ) -> Optional[Dict[str, Any]]:
        """Lookup regulation rule for a specific entity type.
        
        Args:
            entity_type: Type of entity
            regulation: Regulation name (GDPR, HIPAA, PCI DSS)
        
        Returns:
            Rule dictionary or None if not found
        """
        with self.get_session() as session:
            rule = session.query(RegulationRule).filter(
                RegulationRule.entity_type == entity_type,
                RegulationRule.regulation == regulation,
                RegulationRule.is_active == True
            ).first()
            
            return rule.to_dict() if rule else None
    
    def add_regulation_rule(
        self,
        entity_type: str,
        regulation: str,
        required_technique: str,
        article_citation: Optional[str] = None,
        sensitivity_level: Optional[str] = None,
        description: Optional[str] = None
    ) -> int:
        """Add or update a regulation rule.
        
        Args:
            entity_type: Type of entity
            regulation: Regulation name
            required_technique: Anonymization technique to apply
            article_citation: Citation reference
            sensitivity_level: Sensitivity classification
            description: Rule description
        
        Returns:
            ID of the inserted/updated rule
        """
        with self.get_session() as session:
            # Check if rule already exists
            existing_rule = session.query(RegulationRule).filter(
                RegulationRule.entity_type == entity_type,
                RegulationRule.regulation == regulation
            ).first()
            
            if existing_rule:
                existing_rule.required_technique = required_technique
                existing_rule.article_citation = article_citation
                existing_rule.sensitivity_level = sensitivity_level
                existing_rule.description = description
                existing_rule.is_active = True
                rule_id = existing_rule.id
            else:
                new_rule = RegulationRule(
                    entity_type=entity_type,
                    regulation=regulation,
                    required_technique=required_technique,
                    article_citation=article_citation,
                    sensitivity_level=sensitivity_level,
                    description=description
                )
                session.add(new_rule)
                session.flush()
                rule_id = new_rule.id
            
            return rule_id
    
    def create_session(
        self,
        session_id: str,
        text_id: str,
        primary_regulation: Optional[str] = None
    ) -> str:
        """Create a new processing session.
        
        Args:
            session_id: Unique session identifier
            text_id: Text being processed
            primary_regulation: Primary regulation being applied
        
        Returns:
            Session ID
        """
        with self.get_session() as session:
            processing_session = ProcessingSession(
                session_id=session_id,
                text_id=text_id,
                primary_regulation=primary_regulation
            )
            
            session.add(processing_session)
            
            return session_id
    
    def update_session(
        self,
        session_id: str,
        **kwargs
    ):
        """Update session information.
        
        Args:
            session_id: Session to update
            **kwargs: Fields to update (status, total_entities_detected, etc.)
        """
        with self.get_session() as session:
            processing_session = session.query(ProcessingSession).filter(
                ProcessingSession.session_id == session_id
            ).first()
            
            if not processing_session:
                return
            
            for key, value in kwargs.items():
                if hasattr(processing_session, key):
                    setattr(processing_session, key, value)
    
    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of log entries as dictionaries
        """
        with self.get_session() as session:
            processing_session = session.query(ProcessingSession).filter(
                ProcessingSession.session_id == session_id
            ).first()
            
            if not processing_session:
                return []
            
            logs = session.query(ProcessingLog).filter(
                ProcessingLog.text_id == processing_session.text_id
            ).order_by(ProcessingLog.timestamp.asc()).all()
            
            return [log.to_dict() for log in logs]
    
    def generate_compliance_report(
        self,
        text_id: Optional[str] = None,
        regulation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate compliance report from logs.
        
        Args:
            text_id: Filter by specific text (optional)
            regulation: Filter by regulation (optional)
        
        Returns:
            List of compliance records as dictionaries
        """
        with self.get_session() as session:
            query = session.query(ProcessingLog)
            
            if text_id:
                query = query.filter(ProcessingLog.text_id == text_id)
            
            if regulation:
                query = query.filter(
                    ProcessingLog.applicable_regulations.like(f'%{regulation}%')
                )
            
            logs = query.order_by(ProcessingLog.timestamp.desc()).all()
            
            return [log.to_dict() for log in logs]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.get_session() as session:
            stats = {}
            
            stats['total_logs'] = session.query(func.count(ProcessingLog.id)).scalar()
            
            stats['total_sessions'] = session.query(func.count(ProcessingSession.session_id)).scalar()
            
            entities_by_type = session.query(
                ProcessingLog.entity_type,
                func.count(ProcessingLog.id).label('count')
            ).group_by(ProcessingLog.entity_type).order_by(func.count(ProcessingLog.id).desc()).all()
            
            stats['entities_by_type'] = [
                {'entity_type': entity_type, 'count': count}
                for entity_type, count in entities_by_type
            ]
            
            regulations_applied = session.query(
                ProcessingLog.applicable_regulations,
                func.count(ProcessingLog.id).label('count')
            ).filter(
                ProcessingLog.applicable_regulations.isnot(None)
            ).group_by(ProcessingLog.applicable_regulations).order_by(func.count(ProcessingLog.id).desc()).all()
            
            stats['regulations_applied'] = [
                {'applicable_regulations': regulation, 'count': count}
                for regulation, count in regulations_applied
            ]
            
            return stats
