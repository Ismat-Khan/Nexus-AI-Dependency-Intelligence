"""
GRAPHFORGE — Dependency Graph Agent
Responsibilities:
- Convert validated entities and relationships into an interactive NetworkX directed graph
- Enrich nodes and edges with technical metadata (burn rates, inventory days, backup options)
- Prepare data payloads for the 2026 UI Graph Visualizer
"""

from typing import List, Dict, Any, Optional
import networkx as nx
from core.models import Entity, Dependency
from tools.graph_tools import build_dependency_graph, get_graph_summary_metrics


class GraphForgeAgent:
    """GRAPHFORGE Dependency Graph Agent."""
    
    def __init__(self):
        self.name = "GRAPHFORGE"
        self.role = "Dependency Graph Construction & Topological Modeling"
        
    def build_graph(
        self,
        entities: List[Entity],
        dependencies: List[Dependency]
    ) -> Dict[str, Any]:
        """
        Builds the NetworkX DiGraph and extracts topology metrics.
        """
        G = build_dependency_graph(entities, dependencies)
        metrics = get_graph_summary_metrics(G)
        
        return {
            "graph": G,
            "metrics": metrics,
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "status": "success"
        }
        
    def export_graph_for_visualization(
        self,
        graph: nx.DiGraph,
        failed_node: Optional[str] = None,
        affected_nodes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Exports graph nodes and edges into JSON format tailored for PyVis and custom D3/Canvas renderers.
        Colors nodes according to EntityType and failure impact status.
        """
        affected_set = set(affected_nodes or [])
        failed_lower = failed_node.lower() if failed_node else None
        
        # Color mapping (2026 NEXUS Palette)
        type_colors = {
            "supplier": "#22D3EE",    # Cyan
            "component": "#6366F1",   # Indigo
            "machine": "#F59E0B",     # Amber
            "process": "#A855F7",     # Purple
            "product": "#22C55E",     # Emerald
            "system": "#38BDF8",      # Sky
            "service": "#06B6D4"      # Teal
        }
        
        nodes_data = []
        for n, d in graph.nodes(data=True):
            ntype = str(d.get("type", "system")).lower()
            base_color = type_colors.get(ntype, "#6366F1")
            
            # Check failure status
            is_failed = False
            is_affected = False
            if failed_lower and n.lower() == failed_lower:
                base_color = "#EF4444"  # Red
                is_failed = True
            elif n in affected_set or (affected_nodes and any(n.lower() == a.lower() for a in affected_nodes)):
                base_color = "#F43F5E"  # Rose / Affected
                is_affected = True
                
            inv_days = d.get("inventory_days")
            backup = d.get("backup_supplier")
            
            tooltip = f"<b>{n}</b><br/>Type: {ntype.title()}<br/>Importance: {d.get('importance', 'medium').title()}"
            if inv_days is not None:
                tooltip += f"<br/>Inventory Coverage: {inv_days} days"
            if backup:
                tooltip += f"<br/>Documented Backup: {backup}"
            elif ntype in ["supplier", "component"]:
                tooltip += "<br/>Documented Backup: None"
            if d.get("source_doc"):
                tooltip += f"<br/>Source: {d.get('source_doc')}"
                
            nodes_data.append({
                "id": n,
                "label": n,
                "title": tooltip,
                "color": base_color,
                "type": ntype,
                "is_failed": is_failed,
                "is_affected": is_affected,
                "inventory_days": inv_days,
                "backup_supplier": backup,
                "source_doc": d.get("source_doc", "")
            })
            
        edges_data = []
        for u, v, d in graph.edges(data=True):
            is_active_edge = False
            edge_color = "rgba(100, 116, 139, 0.4)"  # Slate
            
            if failed_lower and u.lower() == failed_lower:
                edge_color = "#EF4444"
                is_active_edge = True
            elif u in affected_set and v in affected_set:
                edge_color = "rgba(244, 63, 94, 0.7)"
                is_active_edge = True
                
            edges_data.append({
                "from": u,
                "to": v,
                "label": d.get("relation", "depends_on"),
                "title": f"Relation: {d.get('relation')}<br/>Evidence: {d.get('evidence', '')}<br/>Source: {d.get('source_doc', '')}",
                "color": edge_color,
                "arrows": "to"
            })
            
        return {
            "nodes": nodes_data,
            "edges": edges_data
        }
