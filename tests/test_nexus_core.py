"""
NEXUS Core Verification & Unit Tests
Tests deterministic graph construction, SPOF detection, inventory gap math,
and multi-agent pipeline consistency without requiring external network calls.
"""

import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.models import Entity, Dependency, EntityType, RelationType, ImportanceLevel, ImpactResult
from core.cache import get_default_demo_dataset
from tools.graph_tools import (
    build_dependency_graph,
    find_single_points_of_failure,
    find_bottlenecks,
    find_terminal_products,
    get_graph_summary_metrics
)
from tools.simulation_tools import run_deterministic_simulation, parse_scenario_query
from agents.cascade import CascadeAgent
from agents.sentinel import SentinelAgent
from agents.aegis import AegisAgent


def test_models_and_demo_state():
    print("-> Testing Voltra Mobility Demo State...")
    demo = get_default_demo_dataset()
    assert len(demo["entities"]) >= 10, f"Expected >= 10 entities, got {len(demo['entities'])}"
    assert len(demo["dependencies"]) >= 10, f"Expected >= 10 dependencies, got {len(demo['dependencies'])}"
    assert demo["graph"].number_of_nodes() >= 10
    print("   [PASS] Demo dataset loaded successfully.")


def test_graph_topology_and_spofs():
    print("-> Testing Deterministic Graph Topology & SPOF Detection...")
    demo = get_default_demo_dataset()
    G = demo["graph"]
    
    terminals = find_terminal_products(G)
    print(f"   Terminal Products detected: {terminals}")
    assert "Voltra Model V-1" in terminals, "Voltra Model V-1 must be a terminal product"
    
    spofs = find_single_points_of_failure(G)
    print(f"   Single Points of Failure detected: {spofs}")
    # Apex Microelectronics or Microcontroller MCU-900 must be detected as SPOF
    assert any("Apex" in s or "MCU-900" in s for s in spofs), "Apex or MCU-900 must be flagged as a Single Point of Failure"
    
    # VoltCell has certified backup Amperex Dynamics, so it should not be an unmitigated SPOF
    assert "VoltCell Energy" not in spofs, "VoltCell Energy has documented backup and should not be an unmitigated SPOF"
    print("   [PASS] SPOF and terminal node detection verified.")


def test_case1_and_case3_simulation():
    print("-> Testing Planted Case 1 & Case 3 (Supplier A 7-Day Outage & 2-Day Gap)...")
    demo = get_default_demo_dataset()
    G = demo["graph"]
    
    target, days = parse_scenario_query("What happens if Supplier A is unavailable for 7 days?", list(G.nodes()))
    assert "Apex" in target, f"Expected target to resolve to Apex Microelectronics, got {target}"
    assert days == 7.0, f"Expected 7 days, got {days}"
    
    sim_result: ImpactResult = run_deterministic_simulation(G, target, days)
    print(f"   Failed Node: {sim_result.failed_node}")
    print(f"   Direct Impact: {sim_result.direct_impact}")
    print(f"   All Affected: {sim_result.all_affected_nodes}")
    print(f"   Inventory Coverage: {sim_result.inventory_coverage_days} days")
    print(f"   Outage Gap: {sim_result.inventory_gap_days} days")
    
    assert "Microcontroller MCU-900" in sim_result.direct_impact
    assert any("Voltra Model V-1" in p for p in sim_result.terminal_products)
    assert sim_result.inventory_coverage_days == 5.0, f"Expected 5.0 days coverage, got {sim_result.inventory_coverage_days}"
    assert sim_result.inventory_gap_days == 2.0, f"Expected 2.0 days gap, got {sim_result.inventory_gap_days}"
    assert sim_result.is_single_point_of_failure is True
    assert sim_result.has_documented_backup is False
    print("   [PASS] Deterministic Case 1 (SPOF) and Case 3 (5d coverage vs 7d outage = 2d gap) verified.")


def test_case2_documented_backup():
    print("-> Testing Planted Case 2 (VoltCell Energy Documented Backup)...")
    demo = get_default_demo_dataset()
    G = demo["graph"]
    
    sim_result: ImpactResult = run_deterministic_simulation(G, "VoltCell Energy", 14.0)
    assert sim_result.has_documented_backup is True
    assert sim_result.documented_backup_name == "Amperex Dynamics"
    
    aegis = AegisAgent()
    recovery = aegis.plan_recovery(G, sim_result, use_llm=False)
    assert len(recovery.documented_options) > 0
    assert "Amperex Dynamics" in recovery.documented_options[0]["title"]
    assert recovery.no_documented_alternative_found is False
    print("   [PASS] Case 2 documented backup verification passed.")


def test_no_alternative_rule():
    print("-> Testing Strict Factual Rule: 'No documented alternative was found'...")
    demo = get_default_demo_dataset()
    G = demo["graph"]
    
    sim_result = run_deterministic_simulation(G, "Apex Microelectronics", 7.0)
    aegis = AegisAgent()
    recovery = aegis.plan_recovery(G, sim_result, use_llm=False)
    
    assert recovery.no_documented_alternative_found is True
    assert "No documented alternative was found in the provided data." in recovery.raw_summary
    print("   [PASS] Strict factual audit message verified.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING NEXUS CORE LOGIC & MATHEMATICAL TESTS")
    print("==================================================")
    test_models_and_demo_state()
    test_graph_topology_and_spofs()
    test_case1_and_case3_simulation()
    test_case2_documented_backup()
    test_no_alternative_rule()
    print("==================================================")
    print("ALL CORE NEXUS DETERMINISTIC TESTS PASSED (5/5)!")
    print("==================================================")
