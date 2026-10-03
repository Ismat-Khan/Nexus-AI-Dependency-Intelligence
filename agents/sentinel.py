"""
SENTINEL — Risk Analysis Agent
Responsibilities:
- Evaluate deterministic graph topology for critical vulnerabilities
- Distinguish critical dependencies with documented backups from unmitigated Single Points of Failure
- Pinpoint bottlenecks and single points of failure (SPOFs)
- Calculate normalized Risk Scores (0-100)
"""

from typing import Dict, List, Any, Optional
import networkx as nx
from core.models import RiskAnalysis, ImpactResult
from tools.graph_tools import find_single_points_of_failure, find_bottlenecks, get_graph_summary_metrics
from core.llm import call_groq_llm, is_groq_available


class SentinelAgent:
    """SENTINEL Risk Analysis Agent."""
    
    def __init__(self):
        self.name = "SENTINEL"
        self.role = "Operational Risk Analysis & Vulnerability Scoring"
        
    def analyze_risks(
        self,
        graph: nx.DiGraph,
        impact_result: Optional[ImpactResult] = None,
        use_llm: bool = True
    ) -> RiskAnalysis:
        """
        Computes deterministic risk metrics and generates risk assessments.
        """
        metrics = get_graph_summary_metrics(graph)
        spofs = metrics["spofs"]
        bottlenecks = metrics["bottlenecks"]
        
        # Build structured critical dependencies
        critical_deps = []
        for u, v, d in graph.edges(data=True):
            src_data = graph.nodes[u]
            tgt_data = graph.nodes[v]
            
            # Check criticality
            is_crit = (
                src_data.get("importance") == "critical" or
                tgt_data.get("importance") == "critical" or
                u in spofs or v in spofs
            )
            
            if is_crit:
                backup = src_data.get("backup_supplier") or tgt_data.get("backup_supplier")
                has_backup = bool(backup and str(backup).strip().lower() not in ["none", "n/a", "no", "false", ""])
                critical_deps.append({
                    "source": u,
                    "target": v,
                    "relation": d.get("relation", "depends_on"),
                    "has_backup": has_backup,
                    "backup_supplier": backup if has_backup else "None Documented",
                    "status": "Mitigated by Backup" if has_backup else "UNMITIGATED SPOF",
                    "source_doc": d.get("source_doc", "Extracted Graph")
                })
                
        # Risk score adjustments
        base_score = metrics["risk_score"]
        if impact_result and impact_result.is_single_point_of_failure:
            base_score = min(100, base_score + 15)
        if impact_result and impact_result.inventory_gap_days > 0:
            base_score = min(100, base_score + 10)
            
        risk_level = "LOW"
        if base_score >= 70:
            risk_level = "CRITICAL"
        elif base_score >= 45:
            risk_level = "HIGH"
        elif base_score >= 25:
            risk_level = "MODERATE"
            
        return RiskAnalysis(
            critical_dependencies=critical_deps,
            single_points_of_failure=spofs,
            bottlenecks=bottlenecks,
            overall_risk_score=base_score,
            risk_level=risk_level,
            spof_count=len(spofs),
            total_nodes=metrics["total_nodes"],
            total_edges=metrics["total_edges"]
        )
