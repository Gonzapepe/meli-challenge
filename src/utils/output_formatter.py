"""Output formatting utilities."""

import json
from pathlib import Path
from typing import List, Dict, Any
from src.graph.state import WorkflowState
from src.config import config


def format_results_json(states: List[WorkflowState]) -> Dict[str, Any]:
    """
    Format workflow results as the required results.json structure.
    """
    results = []
    
    for state in states:
        text_result = {
            "text_id": state.get("text_id", "unknown"),
            "regulation": state.get("primary_regulation", "GDPR").value if hasattr(state.get("primary_regulation"), 'value') else str(state.get("primary_regulation", "GDPR")),
            "original_text": state.get("raw_text", ""),
            "anonymized_text": state.get("anonymized_text", ""),
            "entities": _format_entities(state),
            "metadata": {
                "processing_time_ms": state.get("processing_time_ms", 0),
                "entities_detected": len(state.get("classified_entities", [])),
                "techniques_applied": _get_unique_techniques(state)
            }
        }
        results.append(text_result)
    
    return {"results": results}


def _format_entities(state: WorkflowState) -> List[Dict]:
    """Format classified entities with their transformations."""
    entities = []
    classified = state.get("classified_entities", [])
    justifications = {j["entity"]: j for j in state.get("justifications", [])}
    transformation_log = {t["original"]: t for t in state.get("transformation_log", [])}
    
    for entity in classified:
        value = entity.value_detected
        justification = justifications.get(value, {})
        transform = transformation_log.get(value, {})
        
        entities.append({
            "value_detected": value,
            "entity_type": entity.entity_type,
            "sensitivity_level": entity.sensitivity_level.value,
            "applicable_regulations": [r.value for r in entity.applicable_regulations],
            "justification_citations": [justification.get("citation", "")],
            "action_taken": transform.get("technique", "unknown"),
            "anonymized_value": transform.get("anonymized", value),
            "justification": justification.get("justification", "")
        })
    
    return entities


def _get_unique_techniques(state: WorkflowState) -> List[str]:
    """Get unique anonymization techniques used."""
    techniques = set()
    for log in state.get("transformation_log", []):
        techniques.add(log.get("technique", "unknown"))
    return list(techniques)


def format_results_md(states: List[WorkflowState]) -> str:
    """
    Format workflow results as the required results.md report.
    """
    lines = ["# PII Classification & Anonymization Results\n"]
    
    for state in states:
        text_id = state.get("text_id", "unknown")
        regulation = state.get("primary_regulation", "GDPR")
        reg_name = regulation.value if hasattr(regulation, 'value') else str(regulation)
        
        lines.append(f"\n## {text_id.upper()} - {reg_name}\n")
        
        # Original vs Anonymized
        lines.append("### Original Text\n")
        lines.append(f"```\n{state.get('raw_text', '')}\n```\n")
        
        lines.append("### Anonymized Text\n")
        lines.append(f"```\n{state.get('anonymized_text', '')}\n```\n")
        
        # Transformations table
        lines.append("### Transformations Applied\n")
        lines.append("| Entity | Type | Technique | Original | Anonymized | Justification |")
        lines.append("|--------|------|-----------|----------|------------|---------------|")
        
        justifications = {j["entity"]: j for j in state.get("justifications", [])}
        
        for log in state.get("transformation_log", []):
            original = log.get("original", "")
            anonymized = log.get("anonymized", "")
            technique = log.get("technique", "")
            entity_type = log.get("entity_type", "")
            justification = justifications.get(original, {})
            citation = justification.get("citation", "")
            
            lines.append(f"| {_truncate(original, 20)} | {entity_type} | {technique} | {_truncate(original, 15)} | {_truncate(anonymized, 15)} | {citation} |")
        
        # Processing info
        lines.append(f"\n**Processing Time**: {state.get('processing_time_ms', 0)}ms")
        lines.append(f"**Entities Detected**: {len(state.get('classified_entities', []))}")
        lines.append(f"**Quality Check Passed**: {state.get('quality_passed', False)}")
        
        if state.get("issues_found"):
            lines.append(f"\n**Issues Found**: {', '.join(state.get('issues_found', []))}")
        
        lines.append("\n---")
    
    return "\n".join(lines)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text for table display."""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


def save_results(states: List[WorkflowState], output_dir: Path = None) -> tuple:
    """
    Save results to files.
    
    Returns:
        Tuple of (json_path, md_path)
    """
    output_dir = output_dir or config.OUTPUTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_path = output_dir / "results.json"
    json_data = format_results_json(states)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Save Markdown
    md_path = output_dir / "results.md"
    md_content = format_results_md(states)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return json_path, md_path
