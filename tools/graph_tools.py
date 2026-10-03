"""
NEXUS Graph Intelligence Tools
Constructs and analyzes the directed dependency graph using NetworkX.
Provides deterministic graph operations: topological sorting, path analysis,
single points of failure (SPOF) detection, and bottleneck identification.
"""

from typing import Dict, List, Any, Set, Tuple, Optional
import networkx as nx
from core.models import Entity, Dependency, EntityType, RelationType, ImportanceLevel


def build_dependency_graph(
    entities: List[Entity],
    dependencies: List[Dependency]
) -> nx.DiGraph:
    """
    Constructs a deterministic NetworkX directed graph from validated entities and dependencies.
    """
    G = nx.DiGraph()
    
    # Add nodes with complete metadata
    for ent in entities:
        node_id = ent.name.strip()
        G.add_node(
            node_id,
            label=ent.name,
            type=ent.entity_type.value if hasattr(ent.entity_type, "value") else str(ent.entity_type),
            importance=ent.importance.value if hasattr(ent.importance, "value") else str(ent.importance),
            fact=ent.fact,
            source_doc=ent.source_doc,
            section=ent.section or "General",
            inventory_days=ent.inventory_days,
            daily_burn_rate=ent.daily_burn_rate,
            backup_supplier=ent.backup_supplier,
            metadata=ent.metadata or {}
        )
        
    # Add edges with relationship and evidence
    for dep in dependencies:
        src = dep.source.strip()
        tgt = dep.target.strip()
        
        # Ensure nodes exist in graph even if not explicitly in entities list
        if not G.has_node(src):
            G.add_node(src, label=src, type="system", importance="medium", source_doc=dep.source_doc)
        if not G.has_node(tgt):
            G.add_node(tgt, label=tgt, type="system", importance="medium", source_doc=dep.source_doc)
            
        rel_str = dep.relation.value if hasattr(dep.relation, "value") else str(dep.relation)
        G.add_edge(
            src,
            tgt,
            relation=rel_str,
            evidence=dep.evidence,
            source_doc=dep.source_doc,
            confidence=dep.confidence
        )
        
    return G


def find_terminal_products(graph: nx.DiGraph) -> List[str]:
    """
    Identifies end-products or terminal services in the graph (out-degree == 0 or type == 'product').
    """
    terminal = []
    for node, data in graph.nodes(data=True):
        node_type = str(data.get("type", "")).lower()
        if node_type == "product" or (graph.out_degree(node) == 0 and graph.in_degree(node) > 0):
            terminal.append(node)
    return sorted(list(set(terminal)))


def find_root_suppliers(graph: nx.DiGraph) -> List[str]:
    """
    Identifies root nodes (in-degree == 0 or type == 'supplier').
    """
    roots = []
    for node, data in graph.nodes(data=True):
        node_type = str(data.get("type", "")).lower()
        if node_type == "supplier" or (graph.in_degree(node) == 0 and graph.out_degree(node) > 0):
            roots.append(node)
    return sorted(list(set(roots)))


def find_single_points_of_failure(graph: nx.DiGraph) -> List[str]:
    """
    Deterministically identifies Single Points of Failure (SPOFs).
    A node is a SPOF if:
    1. It has no documented backup supplier/alternative, AND
    2. Its removal disconnects any root supplier or intermediate critical component
       from reaching one or more terminal products.
    """
    spofs = set()
    terminals = find_terminal_products(graph)
    if not terminals:
        # Fallback to general articulation points in undirected representation
        undirected = graph.to_undirected()
        return sorted(list(nx.articulation_points(undirected)))
        
    # Test each non-terminal node
    for node in graph.nodes():
        if node in terminals:
            continue
            
        data = graph.nodes[node]
        backup = data.get("backup_supplier")
        
        # If node has a certified backup, it is not an unmitigated SPOF
        if backup and str(backup).strip().lower() not in ["none", "n/a", "no", "false", ""]:
            continue
            
        # Check if removing this node breaks reachability to any terminal product
        # that was previously reachable
        G_sub = graph.copy()
        G_sub.remove_node(node)
        
        # Check upstream nodes that reached terminals through this node
        upstream_ancestors = nx.ancestors(graph, node)
        check_sources = list(upstream_ancestors) if upstream_ancestors else [n for n in graph.nodes() if graph.in_degree(n) == 0]
        
        for src in check_sources:
            if not G_sub.has_node(src):
                continue
            for term in terminals:
                if not G_sub.has_node(term):
                    continue
                # If path existed before removal, check if path still exists
                if nx.has_path(graph, src, term) and not nx.has_path(G_sub, src, term):
                    spofs.add(node)
                    break
            if node in spofs:
                break
                
        # Also, any supplier with no backup that supplies a component used in products
        if data.get("type") == "supplier" and not backup:
            desc = nx.descendants(graph, node)
            if any(t in desc for t in terminals):
                spofs.add(node)
                
    return sorted(list(spofs))


def find_bottlenecks(graph: nx.DiGraph) -> List[str]:
    """
    Identifies bottleneck nodes based on high betweenness centrality and connection degree.
    """
    if len(graph) < 3:
        return list(graph.nodes())
        
    try:
        centrality = nx.betweenness_centrality(graph)
        # Sort nodes by betweenness centrality
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        # Return top 20% or top 3 nodes with centrality > 0.05
        top_candidates = [n for n, c in sorted_nodes if c > 0.05]
        if not top_candidates:
            top_candidates = [n for n, c in sorted_nodes[:3]]
        return top_candidates
    except Exception:
        return []


def get_all_paths_to_products(graph: nx.DiGraph, start_node: str) -> List[List[str]]:
    """
    Deterministically computes all directed paths from start_node to terminal products.
    """
    if not graph.has_node(start_node):
        return []
        
    terminals = find_terminal_products(graph)
    all_paths = []
    
    for term in terminals:
        if term == start_node:
            continue
        if nx.has_path(graph, start_node, term):
            for path in nx.all_simple_paths(graph, source=start_node, target=term):
                all_paths.append(path)
                
    return all_paths


def get_graph_summary_metrics(graph: nx.DiGraph) -> Dict[str, Any]:
    """
    Calculates operational health and topology metrics of the dependency graph.
    """
    total_nodes = graph.number_of_nodes()
    total_edges = graph.number_of_edges()
    
    spofs = find_single_points_of_failure(graph)
    bottlenecks = find_bottlenecks(graph)
    terminals = find_terminal_products(graph)
    roots = find_root_suppliers(graph)
    
    # Calculate Risk Score (0 - 100)
    # Weighted by: SPOF ratio, connectivity, absence of backups
    spof_penalty = min(50, len(spofs) * 15)
    density_penalty = 10 if total_nodes > 0 and (total_edges / max(1, total_nodes)) < 1.0 else 0
    risk_score = min(100, 20 + spof_penalty + density_penalty)
    
    risk_level = "LOW"
    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 45:
        risk_level = "HIGH"
    elif risk_score >= 25:
        risk_level = "MODERATE"
        
    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "spof_count": len(spofs),
        "spofs": spofs,
        "bottlenecks": bottlenecks,
        "terminal_products": terminals,
        "root_suppliers": roots,
        "risk_score": risk_score,
        "risk_level": risk_level
    }
