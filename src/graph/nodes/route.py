from typing import Literal
from src.graph.state import WorkflowState
from src.schemas.entities import Regulation


def determine_regulation_path(state: WorkflowState) -> str:
    """
    Route workflow based on detected regulations.
    
    This is the REQUIRED BIFURCATION for the challenge.
    Routes to regulation-specific processing paths.
    
    Returns:
        Path name for conditional edge routing
    """
    regulation_flags = state.get("regulation_flags", set())
    
    if Regulation.PCI_DSS in regulation_flags and Regulation.GDPR in regulation_flags:
        return "pci_gdpr_path"
    elif Regulation.PCI_DSS in regulation_flags:
        return "pci_path"
    elif Regulation.HIPAA in regulation_flags:
        return "hipaa_path"
    elif Regulation.GDPR in regulation_flags:
        return "gdpr_path"
    elif len(regulation_flags) == 0:
        return "escalation_path"
    else:
        return "gdpr_path"


ROUTING_PATHS = Literal[
    "gdpr_path",
    "hipaa_path",
    "pci_path",
    "pci_gdpr_path",
    "escalation_path"
]
