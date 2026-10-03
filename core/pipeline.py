"""
NEXUS Pipeline Controller
Coordinates high-level state, caching, and multi-agent execution
between the Streamlit interface and the deterministic core.
"""

from typing import Dict, List, Any, Optional, Callable
import networkx as nx
from core.models import Entity, Dependency, ImpactResult, RiskAnalysis, RecoveryPlan
from core.crew import NexusCrewEngine
from core.cache import get_default_demo_dataset


class NexusPipeline:
    """Central controller for NEXUS operations."""
    
    def __init__(self, status_callback: Optional[Callable[[str, str, str], None]] = None):
        self.engine = NexusCrewEngine(status_callback=status_callback)
        self.current_state: Optional[Dict[str, Any]] = None
        
    def load_demo(self) -> Dict[str, Any]:
        """Loads pre-compiled Voltra Mobility demo state in 0.05 seconds."""
        demo_data = get_default_demo_dataset()
        self.current_state = demo_data
        return demo_data
        
    def ingest_files(self, files: List[Dict[str, Any]], use_llm: bool = True) -> Dict[str, Any]:
        """Runs ORION -> MAPPER -> GRAPHFORGE on uploaded files."""
        result = self.engine.run_ingestion_pipeline(files, use_llm=use_llm)
        result["is_demo"] = False
        result["organization"] = "Uploaded Workspace"
        result["file_names"] = [f["name"] for f in files]
        self.current_state = result
        return result
        
    def run_scenario(self, scenario_query: str, use_llm: bool = True) -> Dict[str, Any]:
        """Runs CASCADE -> SENTINEL -> AEGIS on current active graph."""
        if not self.current_state or "graph" not in self.current_state:
            raise ValueError("No active dependency graph. Ingest files or load demo first.")
            
        graph = self.current_state["graph"]
        return self.engine.run_scenario_pipeline(graph, scenario_query, use_llm=use_llm)
