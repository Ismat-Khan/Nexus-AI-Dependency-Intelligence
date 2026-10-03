"""
NEXUS Deterministic Failure Simulation Tools
Executes deterministic graph traversal, blast radius calculations,
inventory coverage analysis, and outage gap math.
Zero LLM hallucination: all impacted nodes and mathematical figures are Python-calculated.
"""

from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
from core.models import ImpactResult, TimeBufferComparison, EvidenceCitation
from tools.graph_tools import find_terminal_products, get_all_paths_to_products, find_single_points_of_failure


def parse_scenario_query(query: str, available_nodes: List[str]) -> Tuple[str, float]:
    """
    Parses a natural-language or structured scenario string into (target_node, outage_days).
    Examples:
    - "What happens if Supplier A is unavailable for 7 days?" -> ("Supplier A", 7.0)
    - "Machine B fails for 2 days" -> ("Machine B", 2.0)
    - "Payment system unavailable for 12 hours" -> ("Payment system", 0.5)
    """
    import re
    
    clean_q = query.strip()
    
    # 1. Extract days or hours duration
    days = 7.0  # default
    
    # Look for hours
    hours_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours|hour|hrs|hr)", clean_q, re.IGNORECASE)
    if hours_match:
        days = round(float(hours_match.group(1)) / 24.0, 2)
    else:
        # Look for days
        days_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:days|day|d)", clean_q, re.IGNORECASE)
        if days_match:
            days = float(days_match.group(1))
            
    # 2. Extract target node by matching against available nodes (case-insensitive)
    target_node = None
    lower_query = clean_q.lower()
    
    # Exact match or longest substring match first
    sorted_nodes = sorted(available_nodes, key=lambda n: len(n), reverse=True)
    for node in sorted_nodes:
        if node.lower() in lower_query:
            target_node = node
            break
            
    # If no exact match, try matching known aliases
    if not target_node:
        alias_map = {
            "supplier a": "Apex Microelectronics",
            "apex": "Apex Microelectronics",
            "component x": "Microcontroller MCU-900",
            "mcu-900": "Microcontroller MCU-900",
            "machine b": "SMT Robot #4",
            "smt robot": "SMT Robot #4",
            "process c": "ECU Sub-assembly",
            "product d": "Voltra Model V-1",
            "voltra": "Voltra Model V-1",
            "supplier b": "VoltCell Energy",
            "voltcell": "VoltCell Energy",
            "supplier c": "StatorTech Precision",
            "supplier d": "Sensoryx Corp",
            "battery": "Lithium-Ion Battery Cells"
        }
        for alias, real_name in alias_map.items():
            if alias in lower_query:
                # verify real_name exists
                for n in available_nodes:
                    if n.lower() == real_name.lower():
                        target_node = n
                        break
                if target_node:
                    break
                    
    # If still not found, fallback to first available node or raw first word
    if not target_node and available_nodes:
        target_node = available_nodes[0]
        
    return target_node, days


def run_deterministic_simulation(
    graph: nx.DiGraph,
    failed_node: str,
    outage_duration_days: float = 7.0
) -> ImpactResult:
    """
    Deterministically computes failure cascade, inventory buffers, and impact paths.
    No LLM is allowed to modify the nodes or numbers in this result.
    """
    if not graph.has_node(failed_node):
        # Look for case-insensitive match
        match = None
        for n in graph.nodes():
            if n.lower() == failed_node.lower():
                match = n
                break
        if match:
            failed_node = match
        else:
            # Fallback placeholder if node not in graph
            return ImpactResult(
                failed_node=failed_node,
                outage_duration_days=outage_duration_days,
                buffer_status="Node not found in graph"
            )
            
    node_data = graph.nodes[failed_node]
    
    # 1. Direct Impact = immediate successors
    direct_successors = sorted(list(graph.successors(failed_node)))
    
    # 2. Total Downstream Reachable Nodes (Cascading Blast Radius)
    descendants = nx.descendants(graph, failed_node)
    all_affected = sorted(list(descendants))
    
    # Indirect = all affected minus direct successors
    indirect_impact = [n for n in all_affected if n not in direct_successors]
    
    # 3. Terminal Products impacted
    terminals = find_terminal_products(graph)
    terminal_impacted = [t for t in terminals if t in all_affected]
    
    # 4. Dependency Chains / Impact Paths from failed node to finished products
    impact_chains = get_all_paths_to_products(graph, failed_node)
    
    # 5. Inventory and Buffer Calculations
    # Check if failed node has inventory days or check directly supplied component
    inventory_days = node_data.get("inventory_days")
    daily_burn = node_data.get("daily_burn_rate") or 0.0
    
    if inventory_days is None:
        # Check direct successors (e.g. if Supplier A failed, check Component X's inventory)
        for succ in direct_successors:
            succ_data = graph.nodes[succ]
            succ_inv = succ_data.get("inventory_days")
            if succ_inv is not None:
                inventory_days = succ_inv
                daily_burn = succ_data.get("daily_burn_rate") or 0.0
                break
                
    coverage_days = float(inventory_days) if inventory_days is not None else 0.0
    gap_days = max(0.0, round(outage_duration_days - coverage_days, 2))
    
    if coverage_days >= outage_duration_days:
        buffer_status = "Fully Buffered (Outage absorbed by current inventory)"
    elif coverage_days > 0:
        buffer_status = f"Partially Buffered (Stock exhausts after {coverage_days:.1f} days; {gap_days:.1f} days downtime)"
    else:
        buffer_status = "Zero Buffer (Immediate production halt upon failure)"
        
    # Multi-day comparison (1 day, 7 days, 14 days, 30 days)
    comparison_intervals = [1.0, 7.0, 14.0, 30.0]
    multi_day_comparison = []
    
    for interval in comparison_intervals:
        interval_gap = max(0.0, round(interval - coverage_days, 2))
        if coverage_days >= interval:
            status = "Buffered"
            prod_impact = "None (Supplied from inventory)"
        elif coverage_days > 0:
            status = "Critical Gap"
            prod_impact = f"{interval_gap} days unbuffered production shutdown"
        else:
            status = "Immediate Failure"
            prod_impact = f"Full {interval} days total shutdown"
            
        multi_day_comparison.append(TimeBufferComparison(
            duration_days=interval,
            coverage_days=coverage_days,
            gap_days=interval_gap,
            status=status,
            production_impact=prod_impact
        ))
        
    # 6. Single Point of Failure (SPOF) Analysis
    spof_list = find_single_points_of_failure(graph)
    is_spof = failed_node in spof_list
    
    # 7. Documented Backup Check
    backup_supplier = node_data.get("backup_supplier")
    # If not on node, check supplied component or edges
    if not backup_supplier:
        for succ in direct_successors:
            succ_backup = graph.nodes[succ].get("backup_supplier")
            if succ_backup:
                backup_supplier = succ_backup
                break
                
    has_backup = False
    backup_name = None
    if backup_supplier and str(backup_supplier).strip().lower() not in ["none", "n/a", "no", "false", ""]:
        has_backup = True
        backup_name = str(backup_supplier).strip()
        
    # 8. Evidence Citations
    evidence_list = []
    # Node source
    if node_data.get("source_doc"):
        evidence_list.append(EvidenceCitation(
            source_file=node_data["source_doc"],
            section=node_data.get("section", "General"),
            exact_fact=node_data.get("fact", f"Entity registered: {failed_node}"),
            confidence=1.0
        ))
        
    # Edge evidence
    for succ in direct_successors:
        edge_data = graph.get_edge_data(failed_node, succ) or {}
        if edge_data.get("evidence"):
            evidence_list.append(EvidenceCitation(
                source_file=edge_data.get("source_doc", "Extracted Graph"),
                section="Relationship Definition",
                exact_fact=f"{failed_node} -> {edge_data.get('relation')} -> {succ}: {edge_data.get('evidence')}",
                confidence=edge_data.get("confidence", 1.0)
            ))
            
    return ImpactResult(
        failed_node=failed_node,
        outage_duration_days=outage_duration_days,
        direct_impact=direct_successors,
        indirect_impact=indirect_impact,
        all_affected_nodes=all_affected,
        terminal_products=terminal_impacted,
        impact_chains=impact_chains,
        inventory_coverage_days=coverage_days,
        inventory_gap_days=gap_days,
        daily_burn_rate=daily_burn,
        buffer_status=buffer_status,
        multi_day_comparison=multi_day_comparison,
        is_single_point_of_failure=is_spof,
        has_documented_backup=has_backup,
        documented_backup_name=backup_name,
        backup_sla_days=3.0 if has_backup else None,
        evidence_citations=evidence_list
    )
