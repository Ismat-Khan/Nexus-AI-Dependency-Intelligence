"""
CASCADE — Failure Simulation Agent

Responsibilities:
- Ingest failure scenario query
- Parse the requested failure entity and outage duration
- Trigger deterministic NetworkX graph traversal
- Compute deterministic inventory coverage and outage gap
- Synthesize an evidence-backed narrative
- Adapt response length to the user's request
- NEVER invent affected nodes or alter calculated metrics
"""

from typing import Dict, List, Any, Optional
import re
import networkx as nx

from core.models import ImpactResult
from tools.simulation_tools import (
    run_deterministic_simulation,
    parse_scenario_query,
)
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
        Executes deterministic simulation and produces an
        evidence-backed narrative.

        The deterministic simulation is always the source of truth.
        The LLM is only used to explain those deterministic results.
        """

        all_nodes = list(graph.nodes())

        # ---------------------------------------------------------
        # 1. Parse target entity + requested outage duration
        # ---------------------------------------------------------
        target_node, outage_days = parse_scenario_query(
            scenario_query,
            all_nodes
        )

        # ---------------------------------------------------------
        # 2. Validate target entity before running simulation
        # ---------------------------------------------------------
        if target_node is None:
            return {
                "impact_result": None,
                "explanation": (
                    "I could not find the entity mentioned in your "
                    "failure scenario in the loaded dependency graph. "
                    "Please use an entity name that exists in the data."
                ),
                "failed_node": None,
                "outage_days": outage_days,
                "status": "entity_not_found"
            }

        # ---------------------------------------------------------
        # 3. Deterministic Calculation
        # ---------------------------------------------------------
        impact_result: ImpactResult = run_deterministic_simulation(
            graph,
            target_node,
            outage_days
        )

        # ---------------------------------------------------------
        # 4. Determine requested response length
        # ---------------------------------------------------------
        response_style = self._detect_response_style(
            scenario_query
        )

        # ---------------------------------------------------------
        # 5. Generate explanation
        # ---------------------------------------------------------
        explanation = ""

        if use_llm and is_groq_available():
            explanation = self._generate_llm_explanation(
                impact_result,
                scenario_query,
                response_style
            )
        else:
            explanation = self._generate_deterministic_explanation(
                impact_result,
                response_style
            )

        return {
            "impact_result": impact_result,
            "explanation": explanation,
            "failed_node": target_node,
            "outage_days": outage_days,
            "response_style": response_style,
            "status": "success"
        }

    # =============================================================
    # RESPONSE LENGTH DETECTION
    # =============================================================

    def _detect_response_style(self, query: str) -> str:
        """
        Detect how much information the user is asking for.

        short:
            "give short information"
            "briefly"
            "in short"
            "quick summary"

        detailed:
            "give detailed information"
            "explain in detail"
            "full details"
            "complete analysis"

        normal:
            Default response length.
        """

        text = query.lower().strip()

        short_patterns = [
            r"\bshort\b",
            r"\bbrief\b",
            r"\bbriefly\b",
            r"\bin short\b",
            r"\bshort information\b",
            r"\bshort answer\b",
            r"\bquick summary\b",
            r"\bbrief summary\b",
            r"\bsummarize briefly\b",
            r"\bjust tell me\b",
            r"\bjust give me\b",
        ]

        detailed_patterns = [
            r"\bdetailed\b",
            r"\bin detail\b",
            r"\bdetails\b",
            r"\bfull detail\b",
            r"\bfull details\b",
            r"\bcomplete analysis\b",
            r"\bdeep analysis\b",
            r"\bexplain fully\b",
            r"\bthorough\b",
            r"\bcomprehensive\b",
            r"\bcomplete explanation\b",
        ]

        if any(
            re.search(pattern, text)
            for pattern in short_patterns
        ):
            return "short"

        if any(
            re.search(pattern, text)
            for pattern in detailed_patterns
        ):
            return "detailed"

        return "normal"

    # =============================================================
    # LLM EXPLANATION
    # =============================================================

    def _generate_llm_explanation(
        self,
        result: ImpactResult,
        query: str,
        response_style: str = "normal"
    ) -> str:
        """
        Ask Groq to explain deterministic results.

        IMPORTANT:
        The LLM cannot change the calculated figures or invent
        dependency nodes.
        """

        if response_style == "short":
            length_instruction = """
The user asked for a SHORT response.

Give only a concise summary in 2-4 sentences.
Mention only the most important impact and inventory information.
Do not provide a long executive report.
Do not add recommendations unless they are directly supported
by the deterministic data.
"""

        elif response_style == "detailed":
            length_instruction = """
The user asked for DETAILED information.

Provide a thorough but focused explanation.
Cover:
- failed entity
- outage duration
- direct impact
- cascading impact
- affected products
- inventory coverage
- inventory gap
- single point of failure
- documented backup
- impact chain where useful

Do not invent any additional facts.
"""

        else:
            length_instruction = """
The user did not explicitly request short or detailed information.

Give a NORMAL concise operational explanation.
Use approximately 1-3 short paragraphs.
Focus on the actual failure impact and the most important
inventory/risk information.
"""

        prompt = f"""
You are CASCADE, the Failure Simulation Agent in NEXUS.

The user asked:

"{query}"

Your job is to explain the DETERMINISTIC simulation results below.

{length_instruction}

CRITICAL GROUNDING RULES:

1. NEVER invent suppliers, machines, components, processes,
   products, systems, or other entities.

2. ONLY mention entities explicitly present in the deterministic
   simulation data below.

3. NEVER change any numerical value.

4. The outage duration is:
   {result.outage_duration_days} days

5. Inventory coverage is:
   {result.inventory_coverage_days} days

6. Inventory gap is:
   {result.inventory_gap_days} days

7. If the outage is shorter than the inventory coverage, clearly
   state that the inventory can absorb the outage.

8. If the outage is longer than the inventory coverage, clearly
   state that inventory is exhausted after the coverage period
   and calculate the remaining gap using the provided value.

9. Do not assume that a backup exists unless the deterministic
   result says that a documented backup exists.

10. Do not turn general AI knowledge into company-specific facts.

DETERMINISTIC SIMULATION DATA:

Failed Node:
{result.failed_node}

Outage Duration:
{result.outage_duration_days} days

Direct Downstream Impact:
{', '.join(result.direct_impact) if result.direct_impact else 'None'}

Indirect / Cascading Impact:
{', '.join(result.indirect_impact) if result.indirect_impact else 'None'}

Finished Products Stalled:
{', '.join(result.terminal_products) if result.terminal_products else 'None'}

Primary Impact Chains:
{[' -> '.join(p) for p in result.impact_chains[:3]]}

Inventory Coverage:
{result.inventory_coverage_days} days

Inventory Gap:
{result.inventory_gap_days} days

Buffer Status:
{result.buffer_status}

Single Point of Failure:
{'YES' if result.is_single_point_of_failure else 'NO'}

Documented Backup:
{result.documented_backup_name if result.has_documented_backup else 'No documented backup certified'}

Now answer the user's question according to the requested response length.
"""

        res = call_groq_llm(
            [{"role": "user", "content": prompt}],
            temperature=0.2
        )

        if res.get("success"):
            content = res.get("content", "").strip()

            if content:
                return content

        return self._generate_deterministic_explanation(
            result,
            response_style
        )

    # =============================================================
    # DETERMINISTIC FALLBACK EXPLANATION
    # =============================================================

    def _generate_deterministic_explanation(
        self,
        result: ImpactResult,
        response_style: str = "normal"
    ) -> str:
        """
        Deterministic narrative generation for offline/fallback mode.

        Response length follows the user's request.
        """

        # ---------------------------------------------------------
        # SHORT RESPONSE
        # ---------------------------------------------------------
        if response_style == "short":

            lines = [
                (
                    f"**{result.failed_node}** is unavailable for "
                    f"**{result.outage_duration_days:g} days**."
                )
            ]

            if result.direct_impact:
                lines.append(
                    f"It directly affects: "
                    f"**{', '.join(result.direct_impact)}**."
                )

            if result.inventory_gap_days > 0:
                lines.append(
                    f"Inventory covers **{result.inventory_coverage_days:g} days**, "
                    f"leaving a **{result.inventory_gap_days:g}-day gap**."
                )
            else:
                lines.append(
                    f"Inventory covers the full "
                    f"**{result.outage_duration_days:g}-day outage**."
                )

            return " ".join(lines)

        # ---------------------------------------------------------
        # DETAILED RESPONSE
        # ---------------------------------------------------------
        if response_style == "detailed":

            lines = []

            lines.append(
                f"### Failure Simulation — {result.failed_node}"
            )

            lines.append(
                f"**Failure duration:** "
                f"{result.outage_duration_days:g} days."
            )

            if result.direct_impact:
                lines.append(
                    f"**Direct impact:** "
                    f"{', '.join(result.direct_impact)}."
                )
            else:
                lines.append(
                    "**Direct impact:** None identified."
                )

            if result.indirect_impact:
                lines.append(
                    f"**Cascading impact:** "
                    f"{', '.join(result.indirect_impact)}."
                )
            else:
                lines.append(
                    "**Cascading impact:** None identified."
                )

            if result.terminal_products:
                lines.append(
                    f"**Affected finished products:** "
                    f"{', '.join(result.terminal_products)}."
                )

            lines.append(
                f"**Inventory coverage:** "
                f"{result.inventory_coverage_days:g} days."
            )

            lines.append(
                f"**Inventory gap:** "
                f"{result.inventory_gap_days:g} days."
            )

            if result.inventory_gap_days > 0:
                lines.append(
                    f"Inventory is exhausted after approximately "
                    f"Day {result.inventory_coverage_days:g}, leaving "
                    f"{result.inventory_gap_days:g} days of uncovered outage."
                )
            else:
                lines.append(
                    "Current inventory is sufficient to absorb "
                    "the requested outage duration."
                )

            lines.append(
                f"**Single point of failure:** "
                f"{'Yes' if result.is_single_point_of_failure else 'No'}."
            )

            if result.has_documented_backup:
                lines.append(
                    f"**Documented backup:** "
                    f"{result.documented_backup_name}."
                )
            else:
                lines.append(
                    "**Documented backup:** "
                    "No documented backup certified."
                )

            return "\n\n".join(lines)

        # ---------------------------------------------------------
        # NORMAL RESPONSE
        # ---------------------------------------------------------

        lines = []

        lines.append(
            f"**{result.failed_node}** has an outage of "
            f"**{result.outage_duration_days:g} days**."
        )

        if result.direct_impact:
            lines.append(
                f"The failure directly affects "
                f"**{', '.join(result.direct_impact)}**."
            )

        if result.indirect_impact:
            lines.append(
                f"It can also cascade to "
                f"**{', '.join(result.indirect_impact)}**."
            )

        if result.inventory_gap_days > 0:
            lines.append(
                f"Inventory provides **{result.inventory_coverage_days:g} days** "
                f"of coverage, leaving a **{result.inventory_gap_days:g}-day gap**."
            )
        else:
            lines.append(
                f"Inventory provides **{result.inventory_coverage_days:g} days** "
                f"of coverage, which is enough for this outage."
            )

        return " ".join(lines)
