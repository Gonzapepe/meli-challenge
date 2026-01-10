import json
import re
from typing import Dict, Any, List
from src.graph.state import WorkflowState
from src.detection.regex_detector import detect_with_regex
from src.llm.groq_client import generate_json_completion
from src.llm.prompts import QUALITY_CHECK_PROMPT


MAX_RETRIES = 2


def quality_check_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Validate that no sensitive data leaked in anonymized text.
    
    Checks:
    1. Regex pattern detection on output
    2. LLM review for residual PII
    3. Compare original entities vs anonymized text
    """
    anonymized_text = state["anonymized_text"]
    original_entities = state["classified_entities"]
    retry_count = state.get("retry_count", 0)
    
    issues_found: List[str] = []
    
    leaked_patterns = detect_with_regex(anonymized_text)
    
    leaked_patterns = [
        p for p in leaked_patterns
        if not _is_false_positive(p, state)
    ]
    
    if leaked_patterns:
        for pattern in leaked_patterns:
            issues_found.append(f"Leaked {pattern.entity_type}: {pattern.value}")
    
    for entity in original_entities:
        original_value = entity.value_detected
        if _was_kept_intentionally(original_value, state):
            continue
        if original_value in anonymized_text:
            issues_found.append(f"Original value still present: {original_value}")
    
    if not issues_found:
        llm_issues = _llm_quality_check(anonymized_text)
        issues_found.extend(llm_issues)
    
    quality_passed = len(issues_found) == 0
    
    new_retry_count = retry_count
    if not quality_passed and retry_count < MAX_RETRIES:
        new_retry_count = retry_count + 1
    
    return {
        "quality_passed": quality_passed,
        "issues_found": issues_found,
        "retry_count": new_retry_count
    }


def _is_false_positive(pattern, state: WorkflowState) -> bool:
    """Check if detected pattern is a false positive."""
    value = pattern.value
    anonymized_text = state.get("anonymized_text", "")
    
    if pattern.entity_type in ["date_dmy", "date_ymd"]:
        if re.match(r'^\d{4}$', value):
            return True
    
    if value.startswith("TOKEN_") or value.startswith("Subject-"):
        return True
    
    if value in ["[PATIENT]", "[PHYSICIAN]", "[REDACTED]", "[EMAIL_REMOVED]"]:
        return True

    if pattern.entity_type == "email":
        start_pos = pattern.start
        context_start = max(0, start_pos - 10)
        context_before = anonymized_text[context_start:start_pos]
        if "***" in context_before or re.search(r'\*+', context_before):
            return True
    
    return False


def _was_kept_intentionally(value: str, state: WorkflowState) -> bool:
    """Check if entity was intentionally kept (not anonymized)."""
    transformation_log = state.get("transformation_log", [])
    for log_entry in transformation_log:
        if log_entry.get("original") == value and log_entry.get("technique") == "keep":
            return True
    return False


def _llm_quality_check(anonymized_text: str) -> List[str]:
    """Use LLM to check for remaining PII."""
    try:
        prompt = QUALITY_CHECK_PROMPT.format(anonymized_text=anonymized_text)
        response = generate_json_completion(prompt)
        
        if not response or response.strip() == "":
            print("LLM quality check: Empty response received")
            return []
        
        data = json.loads(response)
        
        if "error" in data:
            print(f"LLM quality check: Error in response - {data.get('error')}")
            return []
        
        if data.get("contains_pii", False):
            return data.get("issues", [])
        
        return []
    except json.JSONDecodeError as e:
        print(f"LLM quality check error (JSON parse): {e}")
        print(f"LLM quality check: Failed to parse response (not valid JSON)")
        return []
    except Exception as e:
        print(f"LLM quality check error: {e}")
        return []


def should_retry(state: WorkflowState) -> str:
    """Conditional edge: retry anonymization or proceed to output."""
    if state.get("quality_passed", False):
        return "output"
    
    retry_count = state.get("retry_count", 0)
    if retry_count < MAX_RETRIES:
        return "retry"
    
    return "output"
