"""
Test Full Ingestion Pipeline on Physical Demo Files
Reads binary and text files from data/demo/ through Orion, Mapper, and GraphForge.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.pipeline import NexusPipeline


def test_file_ingestion():
    print("-> Ingesting physical demo files from data/demo/...")
    pipeline = NexusPipeline()
    
    demo_dir = os.path.join(os.path.dirname(__file__), "..", "data", "demo")
    files_to_load = [
        "Suppliers.xlsx",
        "Inventory.xlsx",
        "Production_Process.pdf",
        "Machine_Requirements.pdf",
        "Supply_Contracts.pdf",
        "Operations_SOP.docx"
    ]
    
    file_payloads = []
    for fn in files_to_load:
        path = os.path.join(demo_dir, fn)
        assert os.path.exists(path), f"Missing demo file: {path}"
        with open(path, "rb") as f:
            file_payloads.append({
                "name": fn,
                "content": f.read()
            })
            
    # Run ingestion without live LLM (testing deterministic parser and heuristics)
    res = pipeline.ingest_files(file_payloads, use_llm=False)
    
    print(f"   Entities extracted: {len(res['entities'])}")
    print(f"   Dependencies discovered: {len(res['dependencies'])}")
    print(f"   Graph nodes: {res['graph'].number_of_nodes()}")
    print(f"   Graph edges: {res['graph'].number_of_edges()}")
    
    assert len(res["entities"]) >= 8, f"Expected >= 8 entities, got {len(res['entities'])}"
    assert len(res["dependencies"]) >= 5, f"Expected >= 5 dependencies, got {len(res['dependencies'])}"
    assert res["graph"].number_of_nodes() >= 8
    
    # Run a test scenario
    sim = pipeline.run_scenario("Supplier A fails for 7 days", use_llm=False)
    print(f"   Failed node simulated: {sim['failed_node']}")
    print(f"   Blast radius: {len(sim['impact_result'].all_affected_nodes)} nodes")
    print(f"   Inventory coverage: {sim['impact_result'].inventory_coverage_days}d")
    print(f"   Outage gap: {sim['impact_result'].inventory_gap_days}d")
    
    assert sim["impact_result"].inventory_coverage_days == 5.0
    assert sim["impact_result"].inventory_gap_days == 2.0
    print("   [PASS] Physical file ingestion and scenario simulation verified successfully!")


if __name__ == "__main__":
    test_file_ingestion()
