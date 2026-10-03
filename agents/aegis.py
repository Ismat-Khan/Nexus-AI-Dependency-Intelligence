"""
AEGIS — Recovery Planning Agent
Responsibilities:
- Inspect company documentation for certified backup suppliers, inventory buffers, and SOP workarounds
- If no documented alternative exists, strictly output:
  "No documented alternative was found in the provided data."
- Clearly distinguish documented recovery facts from AI-generated suggestions
"""

from typing import Dict, List, Any, Optional
import networkx as nx
from core.models import RecoveryPlan, ImpactResult
from tools.evidence_tools import get_alternative_status_message
from core.llm import call_groq_llm, is_groq_available


class AegisAgent:
    """AEGIS Recovery Planning Agent."""
    
    def __init__(self):
        self.name = "AEGIS"
        self.role = "Recovery Planning & Evidence Verification"
        
    def plan_recovery(
        self,
        graph: nx.DiGraph,
        impact_result: ImpactResult,
        use_llm: bool = True
    ) -> RecoveryPlan:
        """
        Formulates recovery plan based strictly on documented alternatives and inventory math.
        """
        failed_node = impact_result.failed_node
        node_data = graph.nodes[failed_node] if graph.has_node(failed_node) else {}
        
        documented_options = []
        no_alternative = False
        
        # 1. Documented Supplier Backup Check
        has_backup = impact_result.has_documented_backup
        backup_name = impact_result.documented_backup_name
        
        if has_backup and backup_name:
            sla_text = f"Activation SLA: {impact_result.backup_sla_days:.0f} business days." if impact_result.backup_sla_days else "Review contract for lead time."
            documented_options.append({
                "title": f"Activate Approved Secondary Supplier: {backup_name}",
                "description": f"Company agreements designate {backup_name} as certified secondary source. {sla_text}",
                "type": "DOCUMENTED_FACT",
                "evidence": f"Recorded under Supply_Contracts.pdf / Suppliers.xlsx for {failed_node}."
            })
        else:
            no_alternative = True
            
        # 2. Inventory Buffer Strategy
        cov_days = impact_result.inventory_coverage_days
        gap_days = impact_result.inventory_gap_days
        
        if cov_days > 0:
            if gap_days == 0:
                inv_advice = {
                    "strategy": "Inventory Buffer Absorption",
                    "detail": f"Available stock covers {cov_days:g} days. Outage of {impact_result.outage_duration_days:g} days is 100% absorbed with 0 downtime.",
                    "coverage_days": cov_days,
                    "gap_days": 0.0
                }
            else:
                inv_advice = {
                    "strategy": "Partial Buffer - Emergency Rationing",
                    "detail": f"On-hand inventory provides {cov_days:g} days of runway. Production halt begins after Day {cov_days:g}. Immediate {gap_days:g} days gap requires emergency response.",
                    "coverage_days": cov_days,
                    "gap_days": gap_days
                }
        else:
            inv_advice = {
                "strategy": "Zero Inventory Runway",
                "detail": "No on-hand buffer exists. Immediate factory floor stoppage on Day 1.",
                "coverage_days": 0.0,
                "gap_days": impact_result.outage_duration_days
            }
            
        # 3. AI-Generated Suggestions (Explicitly labeled, NOT documented facts)
        ai_suggestions = []
        if use_llm and is_groq_available():
            ai_suggestions = self._generate_ai_suggestions(failed_node, impact_result)
        else:
            ai_suggestions = self._generate_rule_suggestions(failed_node, impact_result)
            
        summary_lines = []
        if documented_options:
            summary_lines.append(f"**Documented Option 1**: {documented_options[0]['title']}")
            summary_lines.append(f"Evidence: {documented_options[0]['evidence']}")
        if no_alternative:
            summary_lines.append("**No documented alternative was found in the provided data.**")
            
        summary_lines.append(f"**Inventory Runway**: {cov_days:g} days coverage ({inv_advice['strategy']})")
        
        return RecoveryPlan(
            documented_options=documented_options,
            inventory_buffer_advice=inv_advice,
            no_documented_alternative_found=no_alternative,
            ai_generated_suggestions=ai_suggestions,
            raw_summary="\n\n".join(summary_lines)
        )
        
    def _generate_ai_suggestions(self, failed_node: str, result: ImpactResult) -> List[str]:
        """Prompts LLM for general suggestions, strictly segregated from documented facts."""
        prompt = f"""You are AEGIS, an operational resilience planner.
The node "{failed_node}" has failed for {result.outage_duration_days} days.
Current inventory covers {result.inventory_coverage_days} days (gap: {result.inventory_gap_days} days).
Documented backup: {'Available: ' + str(result.documented_backup_name) if result.has_documented_backup else 'NONE FOUND IN DATA'}.

Provide 3 concise tactical suggestions for operational contingency.
DO NOT claim these are in company contracts. These are AI advisory suggestions.
Respond ONLY with 3 bullet points starting with "[AI-GENERATED SUGGESTION]".
"""
        res = call_groq_llm([{"role": "user", "content": prompt}], temperature=0.3)
        if res.get("success"):
            lines = [l.strip() for l in res.get("content", "").splitlines() if l.strip()]
            suggestions = [l for l in lines if l.startswith("-") or l.startswith("•") or "SUGGESTION" in l.upper()]
            if suggestions:
                return [s.lstrip("-• ") for s in suggestions[:3]]
        return self._generate_rule_suggestions(failed_node, result)
        
    def _generate_rule_suggestions(self, failed_node: str, result: ImpactResult) -> List[str]:
        return [
            f"[AI-GENERATED SUGGESTION] Initiate emergency expedited shipping or spot-market purchasing for {failed_node} alternatives.",
            "[AI-GENERATED SUGGESTION] Shift assembly plant shift schedule from double shift to single shift to extend inventory runway by up to 40%.",
            "[AI-GENERATED SUGGESTION] Reassign assembly labor to vehicle pre-wiring and sub-assembly staging while awaiting primary component replenishment."
        ]
