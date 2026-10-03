"""
CASCADE — Failure Simulation Agent
Responsibilities:
- Ingest failure scenario query (e.g. "What happens if Supplier A is unavailable for 7 days?")
- Trigger deterministic NetworkX graph traversal and blast radius calculation
- Compute deterministic inventory coverage and outage gap (days)
- Synthesize an evidence-backed narrative explanation of the deterministic results
- NEVER invent affected nodes or alter calculated metrics
"""

from typing import Dict, List, Any, Optional
import networkx as nx
from core.models import ImpactResult
from tools.simulation_tools import run_deterministic_simulation, parse_scenario_query
from core.llm import call_groq_llm, is_groq_available


class CascadeAgent:
    """CASCADE Failure Simulation Agent."""
    
    def __init__(self):
        self.name = "CASCADE"
        self.role = "Failure Simulation & Blast Radius Reasoning"
        
    def simulate(
        self,
        graph: nx.DiGraph,
        scenario_query: str,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Executes deterministic simulation and produces evidence-backed narrative.
        """
        all_nodes = list(graph.nodes())
        target_node, outage_days = parse_scenario_query(scenario_query, all_nodes)
        
        # 1. Deterministic Calculation (Python/NetworkX Ground Truth)
        impact_result: ImpactResult = run_deterministic_simulation(graph, target_node, outage_days)
        
        # 2. LLM Narrative Explanation (Grounded strictly on the deterministic figures)
        explanation = ""
        if use_llm and is_groq_available():
            explanation = self._generate_llm_explanation(impact_result, scenario_query)
        else:
            explanation = self._generate_deterministic_explanation(impact_result)
            
        return {
            "impact_result": impact_result,
            "explanation": explanation,
            "failed_node": target_node,
            "outage_days": outage_days,
            "status": "success"
        }
        
    def _generate_llm_explanation(self, result: ImpactResult, query: str) -> str:
        """Prompts Groq to explain the deterministic results without hallucination."""
        prompt = f"""You are CASCADE, an AI failure simulation agent in NEXUS.
Explain the following DETERMINISTIC simulation results for the query: "{query}".

CRITICAL CONSTRAINTS:
1. You MUST NOT invent any new machines, suppliers, or products.
2. Only mention the exact affected nodes listed in the data.
3. The inventory coverage is {result.inventory_coverage_days} days. The outage is {result.outage_duration_days} days. The gap is {result.inventory_gap_days} days. Do NOT change these numbers.
4. If there is an inventory gap, explain exactly when production will halt.

DETERMINISTIC SIMULATION DATA:
- Failed Node: {result.failed_node}
- Outage Duration: {result.outage_duration_days} days
- Direct Downstream Impact: {', '.join(result.direct_impact) if result.direct_impact else 'None'}
- Indirect / Cascading Impact: {', '.join(result.indirect_impact) if result.indirect_impact else 'None'}
- Finished Products Stalled: {', '.join(result.terminal_products) if result.terminal_products else 'None'}
- Primary Impact Chains: {[' -> '.join(p) for p in result.impact_chains[:3]]}
- Inventory Coverage: {result.inventory_coverage_days} days
- Inventory Gap: {result.inventory_gap_days} days
- Single Point of Failure: {'YES' if result.is_single_point_of_failure else 'NO'}
- Documented Backup: {result.documented_backup_name if result.has_documented_backup else 'No documented backup certified'}

Provide a structured, executive-grade debrief (3-4 concise paragraphs) explaining the failure cascade.
"""
        res = call_groq_llm([{"role": "user", "content": prompt}], temperature=0.2)
        if res.get("success"):
            return res.get("content", "").strip()
        return self._generate_deterministic_explanation(result)
        
    def _generate_deterministic_explanation(self, result: ImpactResult) -> str:
        """Deterministic narrative generation for zero-latency, offline, or fallback mode."""
        lines = []
        lines.append(f"### [DETERMINISTIC BLAST RADIUS] Failure of {result.failed_node}")
        lines.append(
            f"When **{result.failed_node}** experiences an outage of **{result.outage_duration_days:g} days**, "
            f"the failure propagates directly to **{len(result.direct_impact)}** direct dependent entity(s): "
            f"`{', '.join(result.direct_impact)}`."
        )
        
        if result.indirect_impact:
            lines.append(
                f"Through cascading propagation, an additional **{len(result.indirect_impact)}** downstream "
                f"manufacturing process(es) and component(s) are compromised: `{', '.join(result.indirect_impact)}`."
            )
            
        if result.terminal_products:
            lines.append(
                f"⚠️ **Production Line Stoppage**: Output of finished products **{', '.join(result.terminal_products)}** "
                f"will be halted due to absence of necessary upstream sub-assemblies."
            )
            
        # Inventory Buffer Narrative
        if result.inventory_gap_days > 0:
            lines.append(
                f"📦 **Inventory Buffer Analysis**: Current inventory provides **{result.inventory_coverage_days:g} days** of buffer. "
                f"Because the outage duration is **{result.outage_duration_days:g} days**, on-hand stock will be completely exhausted after Day {result.inventory_coverage_days:g}, "
                f"resulting in a critical unbuffered downtime gap of **{result.inventory_gap_days:g} days**."
            )
        else:
            lines.append(
                f"🛡️ **Inventory Buffer Analysis**: Existing stock of **{result.inventory_coverage_days:g} days** is sufficient "
                f"to absorb this **{result.outage_duration_days:g} day** outage without halting final production."
            )
            
        if result.is_single_point_of_failure:
            lines.append(
                f"🚨 **Single Point of Failure Warning**: **{result.failed_node}** has zero certified backup suppliers in company records. "
                "The entire production chain is vulnerable to severe disruption."
            )
            
        return "\n\n".join(lines)
