"""NEXUS Deterministic Tools Module"""
from tools.document_tools import parse_document, extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
from tools.spreadsheet_tools import parse_spreadsheet, extract_inventory_metrics, extract_supplier_catalog
from tools.graph_tools import (
    build_dependency_graph,
    find_single_points_of_failure,
    find_bottlenecks,
    find_terminal_products,
    find_root_suppliers,
    get_all_paths_to_products,
    get_graph_summary_metrics
)
from tools.simulation_tools import run_deterministic_simulation, parse_scenario_query
from tools.evidence_tools import EvidenceStore, format_fact_tag, get_alternative_status_message
