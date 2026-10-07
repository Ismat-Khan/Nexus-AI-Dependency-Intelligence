"""
NEXUS Deterministic Failure Simulation Tools

Executes deterministic graph traversal, blast radius calculations,
inventory coverage analysis, outage gap math, and duration parsing.

Zero LLM hallucination:
all impacted nodes and mathematical figures are Python-calculated.
"""

from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

from core.models import ImpactResult, TimeBufferComparison, EvidenceCitation
from tools.graph_tools import (
    find_terminal_products,
    get_all_paths_to_products,
    find_single_points_of_failure,
)


def parse_scenario_query(
    query: str,
    available_nodes: List[str]
) -> Tuple[Optional[str], float]:
    """
    Parse a natural-language failure scenario into:

        (target_node, outage_duration_days)

    Supported duration formats:

        3 minutes
        1 minute
        an hour
        1 hour
        2 hours
        a day
        1 day
        7 days
        2 weeks
        a week
        1 month
        a month
        6 months
        1 year
        a year
        2 years

    Examples:

        "What happens if Supplier A is unavailable for 7 days?"
            -> ("Supplier A", 7.0)

        "What happens if Sensoryx Corp is unavailable for an hour?"
            -> ("Sensoryx Corp", 0.041667)

        "What happens if Sensoryx Corp fails for 3 minutes?"
            -> ("Sensoryx Corp", 0.002083)

        "What happens if Sensoryx Corp fails for 2 hours?"
            -> ("Sensoryx Corp", 0.083333)

        "What happens if Sensoryx Corp fails for a day?"
            -> ("Sensoryx Corp", 1.0)

        "What happens if Sensoryx Corp fails for a month?"
            -> ("Sensoryx Corp", 30.0)

        "What happens if Sensoryx Corp fails for a year?"
            -> ("Sensoryx Corp", 365.0)

    IMPORTANT:
    The duration supplied by the user is preserved.

    The old implementation defaulted to 7 days when it could not
    recognize the duration. This version only uses 7 days when the
    user provides no recognizable duration at all.

    IMPORTANT:
    If the requested entity cannot be found, this function returns
    None instead of silently selecting the first graph node.
    """

    import re

    clean_q = query.strip()

    if not clean_q:
        return None, 7.0

    # ============================================================
    # 1. DEFAULT DURATION
    # ============================================================

    # Backward-compatible default ONLY when no duration is supplied.
    outage_duration_days = 7.0

    duration_found = False

    # ============================================================
    # 2. NUMERIC DURATIONS
    # ============================================================

    numeric_duration_patterns = [
        # Minutes
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|min)\b",
            lambda value: value / (24.0 * 60.0),
        ),

        # Hours
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|hr)\b",
            lambda value: value / 24.0,
        ),

        # Days
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:days?|d)\b",
            lambda value: value,
        ),

        # Weeks
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:weeks?|wks?|wk)\b",
            lambda value: value * 7.0,
        ),

        # Months
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:months?|mos?|mo)\b",
            lambda value: value * 30.0,
        ),

        # Years
        (
            r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?|yr)\b",
            lambda value: value * 365.0,
        ),
    ]

    for pattern, converter in numeric_duration_patterns:
        match = re.search(pattern, clean_q, re.IGNORECASE)

        if match:
            value = float(match.group(1))

            outage_duration_days = round(
                converter(value),
                6
            )

            duration_found = True
            break

    # ============================================================
    # 3. NATURAL-LANGUAGE DURATIONS
    # ============================================================

    if not duration_found:

        natural_duration_patterns = [
            # an minute / a minute
            (
                r"\b(?:an|a)\s+(?:minute|min)\b",
                1.0 / (24.0 * 60.0),
            ),

            # an hour / a hour
            (
                r"\b(?:an|a)\s+(?:hour|hr)\b",
                1.0 / 24.0,
            ),

            # a day
            (
                r"\ba\s+(?:day|d)\b",
                1.0,
            ),

            # a week
            (
                r"\ba\s+(?:week|wk)\b",
                7.0,
            ),

            # a month
            (
                r"\ba\s+(?:month|mo)\b",
                30.0,
            ),

            # a year / one year
            (
                r"\b(?:a|one)\s+(?:year|yr)\b",
                365.0,
            ),

            # one day
            (
                r"\bone\s+(?:day|d)\b",
                1.0,
            ),

            # one week
            (
                r"\bone\s+(?:week|wk)\b",
                7.0,
            ),

            # one month
            (
                r"\bone\s+(?:month|mo)\b",
                30.0,
            ),
        ]

        for pattern, converted_days in natural_duration_patterns:

            if re.search(pattern, clean_q, re.IGNORECASE):

                outage_duration_days = round(
                    converted_days,
                    6
                )

                duration_found = True
                break

    # ============================================================
    # 4. EXTRACT TARGET ENTITY FROM ACTUAL GRAPH NODES
    # ============================================================

    target_node = None
    lower_query = clean_q.lower()

    # Longest entity names are checked first.
    # This prevents a shorter entity name from being selected
    # when a more specific entity is present.
    sorted_nodes = sorted(
        available_nodes,
        key=lambda node: len(str(node)),
        reverse=True,
    )

    for node in sorted_nodes:

        node_text = str(node).strip()

        if not node_text:
            continue

        if node_text.lower() in lower_query:
            target_node = node
            break

    # ============================================================
    # 5. DEMO / COMMON ALIASES
    # ============================================================

    if target_node is None:

        alias_map = {
            # Supplier A
            "supplier a": "Apex Microelectronics",
            "apex": "Apex Microelectronics",

            # Component X
            "component x": "Microcontroller MCU-900",
            "mcu-900": "Microcontroller MCU-900",

            # Machine B
            "machine b": "SMT Robot #4",
            "smt robot": "SMT Robot #4",

            # Process C
            "process c": "ECU Sub-assembly",

            # Product D
            "product d": "Voltra Model V-1",
            "voltra": "Voltra Model V-1",

            # Supplier B
            "supplier b": "VoltCell Energy",
            "voltcell": "VoltCell Energy",

            # Supplier C
            "supplier c": "StatorTech Precision",
            "statortech": "StatorTech Precision",

            # Supplier D
            "supplier d": "Sensoryx Corp",
            "sensoryx": "Sensoryx Corp",

            # Battery
            "battery": "Lithium-Ion Battery Cells",
        }

        for alias, real_name in alias_map.items():

            alias_pattern = (
                r"\b"
                + re.escape(alias)
                + r"\b"
            )

            if not re.search(
                alias_pattern,
                lower_query,
                re.IGNORECASE,
            ):
                continue

            for node in available_nodes:

                if (
                    str(node).strip().lower()
                    == real_name.lower()
                ):
                    target_node = node
                    break

            if target_node is not None:
                break

    # ============================================================
    # 6. NEVER FALL BACK TO THE FIRST GRAPH NODE
    # ============================================================

    # This is very important.
    #
    # Previously, if NEXUS could not identify the requested entity,
    # it used:
    #
    #     available_nodes[0]
    #
    # That could cause a question about Sensoryx Corp to accidentally
    # simulate Apex Microelectronics or another unrelated entity.
    #
    # We now return None so the calling layer can show a friendly
    # "entity not found" message.

    if target_node is None:
        return None, outage_duration_days

    return target_node, outage_duration_days


def run_deterministic_simulation(
    graph: nx.DiGraph,
    failed_node: str,
    outage_duration_days: float = 7.0
) -> ImpactResult:
    """
    Deterministically computes failure cascade, inventory buffers,
    and impact paths.

    No LLM is allowed to modify the nodes or mathematical figures
    in this result.
    """

    if not graph.has_node(failed_node):

        # Look for case-insensitive match.
        match = None

        for node in graph.nodes():

            if str(node).lower() == str(failed_node).lower():
                match = node
                break

        if match:
            failed_node = match

        else:
            return ImpactResult(
                failed_node=failed_node,
                outage_duration_days=outage_duration_days,
                buffer_status="Node not found in graph",
            )

    node_data = graph.nodes[failed_node]

    # ============================================================
    # 1. DIRECT IMPACT
    # ============================================================

    direct_successors = sorted(
        list(graph.successors(failed_node))
    )

    # ============================================================
    # 2. TOTAL DOWNSTREAM REACH
    # ============================================================

    descendants = nx.descendants(
        graph,
        failed_node,
    )

    all_affected = sorted(
        list(descendants)
    )

    # Indirect impact =
    # all affected nodes minus immediate successors.
    indirect_impact = [
        node
        for node in all_affected
        if node not in direct_successors
    ]

    # ============================================================
    # 3. TERMINAL PRODUCTS
    # ============================================================

    terminals = find_terminal_products(graph)

    terminal_impacted = [
        product
        for product in terminals
        if product in all_affected
    ]

    # ============================================================
    # 4. IMPACT CHAINS
    # ============================================================

    impact_chains = get_all_paths_to_products(
        graph,
        failed_node,
    )

    # ============================================================
    # 5. INVENTORY / BUFFER CALCULATION
    # ============================================================

    inventory_days = node_data.get(
        "inventory_days"
    )

    daily_burn = (
        node_data.get("daily_burn_rate")
        or 0.0
    )

    # If the failed entity itself does not contain inventory,
    # inspect its directly supplied successor.
    if inventory_days is None:

        for successor in direct_successors:

            successor_data = graph.nodes[successor]

            successor_inventory = successor_data.get(
                "inventory_days"
            )

            if successor_inventory is not None:

                inventory_days = successor_inventory

                daily_burn = (
                    successor_data.get(
                        "daily_burn_rate"
                    )
                    or 0.0
                )

                break

    coverage_days = (
        float(inventory_days)
        if inventory_days is not None
        else 0.0
    )

    # IMPORTANT:
    # outage_duration_days comes directly from the user's
    # scenario parser.
    gap_days = max(
        0.0,
        round(
            outage_duration_days - coverage_days,
            6,
        ),
    )

    # ============================================================
    # 6. BUFFER STATUS
    # ============================================================

    if coverage_days >= outage_duration_days:

        buffer_status = (
            "Fully Buffered "
            "(Outage absorbed by current inventory)"
        )

    elif coverage_days > 0:

        buffer_status = (
            f"Partially Buffered "
            f"(Stock exhausts after "
            f"{coverage_days:.2f} days; "
            f"{gap_days:.2f} days downtime)"
        )

    else:

        buffer_status = (
            "Zero Buffer "
            "(Immediate production halt upon failure)"
        )

    # ============================================================
    # 7. STANDARD COMPARISON INTERVALS
    # ============================================================

    comparison_intervals = [
        1.0,
        7.0,
        14.0,
        30.0,
    ]

    multi_day_comparison = []

    for interval in comparison_intervals:

        interval_gap = max(
            0.0,
            round(
                interval - coverage_days,
                6,
            ),
        )

        if coverage_days >= interval:

            status = "Buffered"

            production_impact = (
                "None (Supplied from inventory)"
            )

        elif coverage_days > 0:

            status = "Critical Gap"

            production_impact = (
                f"{interval_gap:.2f} days "
                f"unbuffered production shutdown"
            )

        else:

            status = "Immediate Failure"

            production_impact = (
                f"Full {interval:.0f} days "
                f"total shutdown"
            )

        multi_day_comparison.append(
            TimeBufferComparison(
                duration_days=interval,
                coverage_days=coverage_days,
                gap_days=interval_gap,
                status=status,
                production_impact=production_impact,
            )
        )

    # ============================================================
    # 8. SINGLE POINT OF FAILURE
    # ============================================================

    spof_list = find_single_points_of_failure(
        graph
    )

    is_spof = failed_node in spof_list

    # ============================================================
    # 9. DOCUMENTED BACKUP
    # ============================================================

    backup_supplier = node_data.get(
        "backup_supplier"
    )

    if not backup_supplier:

        for successor in direct_successors:

            successor_backup = (
                graph.nodes[successor].get(
                    "backup_supplier"
                )
            )

            if successor_backup:

                backup_supplier = successor_backup
                break

    has_backup = False
    backup_name = None

    if (
        backup_supplier
        and str(backup_supplier).strip().lower()
        not in [
            "none",
            "n/a",
            "no",
            "false",
            "",
        ]
    ):

        has_backup = True
        backup_name = str(
            backup_supplier
        ).strip()

    # ============================================================
    # 10. EVIDENCE CITATIONS
    # ============================================================

    evidence_list = []

    # Node evidence
    if node_data.get("source_doc"):

        evidence_list.append(
            EvidenceCitation(
                source_file=node_data["source_doc"],
                section=node_data.get(
                    "section",
                    "General",
                ),
                exact_fact=node_data.get(
                    "fact",
                    f"Entity registered: {failed_node}",
                ),
                confidence=1.0,
            )
        )

    # Edge evidence
    for successor in direct_successors:

        edge_data = (
            graph.get_edge_data(
                failed_node,
                successor,
            )
            or {}
        )

        if edge_data.get("evidence"):

            evidence_list.append(
                EvidenceCitation(
                    source_file=edge_data.get(
                        "source_doc",
                        "Extracted Graph",
                    ),
                    section="Relationship Definition",
                    exact_fact=(
                        f"{failed_node} -> "
                        f"{edge_data.get('relation')} -> "
                        f"{successor}: "
                        f"{edge_data.get('evidence')}"
                    ),
                    confidence=edge_data.get(
                        "confidence",
                        1.0,
                    ),
                )
            )

    # ============================================================
    # 11. FINAL DETERMINISTIC RESULT
    # ============================================================

    return ImpactResult(
        failed_node=failed_node,

        # This is now the actual duration supplied by
        # the user's question.
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

        backup_sla_days=(
            3.0
            if has_backup
            else None
        ),

        evidence_citations=evidence_list,
    )
