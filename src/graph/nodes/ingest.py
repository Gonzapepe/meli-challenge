"""Ingest node - text preprocessing and entity detection."""

from typing import Dict, Any
from src.graph.state import WorkflowState
from src.detection.regex_detector import detect_with_regex
from src.detection.llm_detector import extract_entities_with_llm, merge_entities
from src.llm.groq_client import get_groq_client
from src.config import config


def ingest_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Preprocess text and detect entities using hybrid approach.
    
    Processing:
    1. Text normalization
    2. Deterministic detection (regex)
    3. LLM-based detection (contextual)
    4. Merge and deduplicate entities
    """
    raw_text = state["raw_text"]
    
    # Step 1: Normalize text
    normalized_text = raw_text.strip()
    
    # Step 2: Regex-based detection (structured data)
    regex_entities = detect_with_regex(normalized_text)
    
    # Step 3: LLM-based detection (contextual entities)
    try:
        client = get_groq_client()
        llm_entities = extract_entities_with_llm(
            normalized_text,
            client,
            config.LLM_MODEL
        )
    except Exception as e:
        print(f"LLM detection failed, using regex only: {e}")
        llm_entities = []
    
    # Step 4: Merge entities (regex takes precedence for overlaps)
    all_entities = merge_entities(regex_entities, llm_entities)
    
    return {
        "detected_entities": all_entities
    }
