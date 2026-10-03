"""
NEXUS Multi-Agent Orchestration Engine (CrewAI Architecture)
Orchestrates the 6 core agents:
1. ORION (Document Intelligence)
2. NEXUS-MAPPER (Dependency Discovery)
3. GRAPHFORGE (Graph Engine)
4. CASCADE (Failure Simulation)
5. SENTINEL (Risk Analysis)
6. AEGIS (Recovery Planning)

Enforces strict separation: LLMs reason and synthesize; Python tools calculate and verify.
Supports both native CrewAI classes and native deterministic multi-agent orchestration
for guaranteed resilience on Streamlit Cloud.
"""

import time
from typing import Dict, List, Any, Optional, Callable
import networkx as nx

from agents.orion import OrionAgent
from agents.mapper import MapperAgent
from agents.graphforge import GraphForgeAgent
from agents.cascade import CascadeAgent
from agents.sentinel import SentinelAgent
from agents.aegis import AegisAgent
from core.models import Entity, Dependency, ImpactResult, RiskAnalysis, RecoveryPlan, AgentStatusRecord
from core.llm import is_groq_available, get_groq_api_key

# Check if native CrewAI is available in the environment
HAS_CREWAI = False
try:
    from crewai import Agent as CrewAgent, Task as CrewTask, Crew as CrewRunner, Process
    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False


class NexusCrewEngine:
    """Multi-Agent Orchestrator for NEXUS."""
    
    def __init__(self, status_callback: Optional[Callable[[str, str, str], None]] = None):
        """
        status_callback signature: callback(agent_name, status, detail_message)
        """
        self.status_callback = status_callback
        self.orion = OrionAgent()
        self.mapper = MapperAgent()
        self.graphforge = GraphForgeAgent()
        self.cascade = CascadeAgent()
        self.sentinel = SentinelAgent()
        self.aegis = AegisAgent()
        
    def _notify(self, agent_name: str, status: str, detail: str):
        if self.status_callback:
            try:
                self.status_callback(agent_name, status, detail)
            except Exception:
                pass
                
    def run_ingestion_pipeline(
        self,
        files: List[Dict[str, Any]],
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Executes ORION -> NEXUS-MAPPER -> GRAPHFORGE data ingestion and graph construction.
        """
        # Step 1: ORION
        self._notify("ORION", "running", f"Analyzing {len(files)} uploaded document(s)...")
        t0 = time.time()
        orion_res = self.orion.analyze_documents(files, use_llm=use_llm)
        t_orion = time.time() - t0
        self._notify("ORION", "completed", f"Extracted {len(orion_res['entities'])} entities with evidence ({t_orion:.1f}s)")
        
        entities: List[Entity] = orion_res["entities"]
        raw_docs = orion_res["raw_documents"]
        supplier_data = orion_res["supplier_data"]
        inventory_data = orion_res["inventory_data"]
        
        # Step 2: NEXUS-MAPPER
        self._notify("NEXUS-MAPPER", "running", "Discovering dependency links & mapping relationships...")
        t0 = time.time()
        dependencies: List[Dependency] = self.mapper.discover_dependencies(
            entities, raw_docs, supplier_data, use_llm=use_llm
        )
        t_map = time.time() - t0
        self._notify("NEXUS-MAPPER", "completed", f"Discovered {len(dependencies)} grounded relationships ({t_map:.1f}s)")
        
        # Step 3: GRAPHFORGE
        self._notify("GRAPHFORGE", "running", "Building NetworkX directed dependency graph...")
        t0 = time.time()
        forge_res = self.graphforge.build_graph(entities, dependencies)
        t_forge = time.time() - t0
        self._notify("GRAPHFORGE", "completed", f"Built graph: {forge_res['node_count']} nodes, {forge_res['edge_count']} edges ({t_forge:.1f}s)")
        
        return {
            "entities": entities,
            "dependencies": dependencies,
            "graph": forge_res["graph"],
            "metrics": forge_res["metrics"],
            "raw_documents": raw_docs,
            "inventory_data": inventory_data,
            "supplier_data": supplier_data
        }
        
    def run_scenario_pipeline(
        self,
        graph: nx.DiGraph,
        scenario_query: str,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Executes CASCADE -> SENTINEL -> AEGIS for a failure simulation scenario.
        """
        # Step 4: CASCADE
        self._notify("CASCADE", "running", f"Simulating failure scenario: '{scenario_query}'...")
        t0 = time.time()
        cascade_res = self.cascade.simulate(graph, scenario_query, use_llm=use_llm)
        impact_result: ImpactResult = cascade_res["impact_result"]
        t_cas = time.time() - t0
        self._notify(
            "CASCADE",
            "completed",
            f"Blast radius: {len(impact_result.all_affected_nodes)} affected nodes, {impact_result.inventory_gap_days:g}d gap ({t_cas:.1f}s)"
        )
        
        # Step 5: SENTINEL
        self._notify("SENTINEL", "running", "Auditing operational risks & single points of failure...")
        t0 = time.time()
        risk_analysis: RiskAnalysis = self.sentinel.analyze_risks(graph, impact_result, use_llm=use_llm)
        t_sen = time.time() - t0
        self._notify(
            "SENTINEL",
            "completed",
            f"Risk Level: {risk_analysis.risk_level} (Score: {risk_analysis.overall_risk_score}/100) ({t_sen:.1f}s)"
        )
        
        # Step 6: AEGIS
        self._notify("AEGIS", "running", "Searching documented evidence for certified recovery alternatives...")
        t0 = time.time()
        recovery_plan: RecoveryPlan = self.aegis.plan_recovery(graph, impact_result, use_llm=use_llm)
        t_aeg = time.time() - t0
        rec_status = "Backup Found" if not recovery_plan.no_documented_alternative_found else "No Alternative Found in Data"
        self._notify("AEGIS", "completed", f"Plan finalized: {rec_status} ({t_aeg:.1f}s)")
        
        return {
            "impact_result": impact_result,
            "risk_analysis": risk_analysis,
            "recovery_plan": recovery_plan,
            "narrative": cascade_res["explanation"],
            "failed_node": cascade_res["failed_node"],
            "outage_days": cascade_res["outage_days"]
        }
