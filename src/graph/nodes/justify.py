from typing import Dict, Any, List
from src.graph.state import WorkflowState
from src.schemas.entities import Regulation
from src.anonymization.strategies import get_strategy_for_entity
from src.llm.groq_client import generate_completion
from src.llm.prompts import JUSTIFICATION_PROMPT


def justify_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate detailed justifications for each anonymization decision.
    
    Uses regulation-specific strategies and LLM to create
    proper citations and explanations.
    """
    classified_entities = state["classified_entities"]
    primary_regulation = state.get("primary_regulation", Regulation.GDPR)
    
    anonymization_strategies = {}
    justifications = []
    
    for entity in classified_entities:
        strategy = get_strategy_for_entity(
            entity.entity_type,
            primary_regulation
        )
        
        anonymization_strategies[entity.value_detected] = {
            "technique": strategy["technique"],
            "regulation_article": strategy["article"],
            "entity_type": entity.entity_type
        }
        
        justification = _generate_justification(
            entity,
            strategy,
            primary_regulation
        )
        
        justifications.append({
            "entity": entity.value_detected,
            "entity_type": entity.entity_type,
            "technique": strategy["technique"],
            "regulation": primary_regulation.value,
            "citation": strategy["article"],
            "justification": justification
        })
    
    return {
        "anonymization_strategies": anonymization_strategies,
        "justifications": justifications
    }


def _generate_justification(entity, strategy: Dict, regulation: Regulation) -> str:
    """Generate a detailed justification using LLM."""
    if strategy["technique"] == "keep":
        return strategy["justification"]
    
    try:
        prompt = JUSTIFICATION_PROMPT.format(
            entity_value=entity.value_detected,
            entity_type=entity.entity_type,
            sensitivity_level=entity.sensitivity_level.value,
            regulation=regulation.value,
            technique=strategy["technique"],
            article=strategy["article"]
        )
        
        response = generate_completion(
            prompt,
            system_prompt="You are a data privacy expert. Provide concise, professional justifications.",
            temperature=0.3,
            max_tokens=200
        )
        
        return response.strip()
    except Exception as e:
        return strategy.get("justification", f"Applied {strategy['technique']} per {strategy['article']}")
