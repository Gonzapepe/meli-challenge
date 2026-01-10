from langgraph.graph import StateGraph, END
from src.graph.state import WorkflowState
from src.graph.nodes.ingest import ingest_node
from src.graph.nodes.classify import classify_node
from src.graph.nodes.route import determine_regulation_path
from src.graph.nodes.justify import justify_node
from src.graph.nodes.anonymize import anonymize_node
from src.graph.nodes.quality_check import quality_check_node, should_retry

import langchain
if not hasattr(langchain, 'debug'):
    langchain.debug = False


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow with conditional routing.
    
    Flow:
    START → ingest → classify → [route bifurcation] → justify → anonymize → quality_check → END
    
    The route node provides the REQUIRED BIFURCATION based on regulation.
    """
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("ingest", ingest_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("justify_gdpr", justify_node)
    workflow.add_node("justify_hipaa", justify_node)
    workflow.add_node("justify_pci", justify_node)
    workflow.add_node("anonymize", anonymize_node)
    workflow.add_node("quality_check", quality_check_node)
    
    workflow.set_entry_point("ingest")
    
    workflow.add_edge("ingest", "classify")
    
    workflow.add_conditional_edges(
        "classify",
        determine_regulation_path,
        {
            "gdpr_path": "justify_gdpr",
            "hipaa_path": "justify_hipaa",
            "pci_path": "justify_pci",
            "pci_gdpr_path": "justify_pci",
            "escalation_path": "justify_gdpr"
        }
    )
    
    workflow.add_edge("justify_gdpr", "anonymize")
    workflow.add_edge("justify_hipaa", "anonymize")
    workflow.add_edge("justify_pci", "anonymize")
    
    workflow.add_edge("anonymize", "quality_check")
    
    workflow.add_conditional_edges(
        "quality_check",
        should_retry,
        {
            "output": END,
            "retry": "anonymize"
        }
    )
    
    return workflow


def compile_workflow():
    """Compile the workflow for execution."""
    workflow = create_workflow()
    return workflow.compile()


def run_workflow(text: str, text_id: str) -> WorkflowState:
    """
    Run the complete workflow on a text.
    
    Args:
        text: Raw input text to process
        text_id: Identifier for the text (e.g., "texto1")
        
    Returns:
        Final workflow state with anonymized text and logs
    """
    import time
    
    app = compile_workflow()
    
    initial_state: WorkflowState = {
        "raw_text": text,
        "text_id": text_id,
        "retry_count": 0
    }
    
    start_time = time.time()
    final_state = app.invoke(initial_state)
    end_time = time.time()
    
    final_state["processing_time_ms"] = int((end_time - start_time) * 1000)
    
    return final_state
