"""
NEXUS UI Components
Reusable Streamlit UI modules for Hero Header, Metric Cards, Live Agent Status Feed,
Impact Reports, and Evidence Tables adhering to the 2026 AI Product Experience.
"""

from typing import Dict, List, Any, Optional
import streamlit as st
from core.models import ImpactResult, RiskAnalysis, RecoveryPlan, EvidenceCitation
from tools.evidence_tools import format_fact_tag


def render_hero_header():
    """Renders the futuristic hero header with breathing ambient glow."""
    st.markdown("""
    <div class="hero-glow-container">
      <div class="hero-glow"></div>
      <div class="hero-badge">AI DEPENDENCY INTELLIGENCE PLATFORM // NEXUS v2.6</div>
      <h1 class="hero-title">NEXUS</h1>
      <p class="hero-tagline">
        See what depends on what. Simulate what happens when something fails.
        <br/><span style="font-size: 0.9rem; color: #64748B;">Multi-Agent Factual Extraction &bull; Deterministic Graph Traversal &bull; Zero Hallucination Impact Analysis</span>
      </p>
    </div>
    """, unsafe_allow_html=True)


def render_pipeline_badge(is_live: bool, model_name: str = "Groq LLaMA / GPT-OSS"):
    """Displays unambiguous badge distinguishing Live AI Analysis vs Demo / Cached Mode."""
    if is_live:
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 15px;">
          <div style="background: rgba(34, 197, 94, 0.12); border: 1px solid #22C55E; color: #22C55E; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 8px #22C55E;"></span>
            LIVE AI PIPELINE &bull; {model_name}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: flex-end; margin-bottom: 15px;">
          <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid #6366F1; color: #818CF8; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #818CF8; box-shadow: 0 0 8px #818CF8;"></span>
            DEMO / CACHED ANALYSIS &bull; VOLTRA MOBILITY SYNTHETIC DATASET
          </div>
        </div>
        """, unsafe_allow_html=True)


def render_metrics_dashboard(
    docs_count: int,
    entities_count: int,
    deps_count: int,
    critical_deps_count: int,
    spof_count: int
):
    """Renders the top executive metrics row with real calculated numbers."""
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.markdown(f"""
        <div class="nexus-metric-box">
          <div class="nexus-metric-label">Documents Analyzed</div>
          <div class="nexus-metric-value">{docs_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="nexus-metric-box">
          <div class="nexus-metric-label">Entities Discovered</div>
          <div class="nexus-metric-value" style="color: #22D3EE;">{entities_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="nexus-metric-box">
          <div class="nexus-metric-label">Dependencies</div>
          <div class="nexus-metric-value" style="color: #818CF8;">{deps_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="nexus-metric-box">
          <div class="nexus-metric-label">Critical Links</div>
          <div class="nexus-metric-value" style="color: #F59E0B;">{critical_deps_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c5:
        spof_color = "#EF4444" if spof_count > 0 else "#22C55E"
        st.markdown(f"""
        <div class="nexus-metric-box">
          <div class="nexus-metric-label">Single Points of Failure</div>
          <div class="nexus-metric-value" style="color: {spof_color};">{spof_count}</div>
        </div>
        """, unsafe_allow_html=True)


def render_agent_activity_feed(agent_statuses: Dict[str, Dict[str, Any]]):
    """
    Renders real agent execution activity.
    Example:
      ✓ ORION: Documents analyzed
      ✓ NEXUS-MAPPER: Dependencies discovered
      ✓ GRAPHFORGE: Dependency graph generated
      ✓ CASCADE: Simulating failure...
      ○ SENTINEL: Waiting
      ○ AEGIS: Waiting
    """
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px;">
      LIVE AGENT SWARM EXECUTION MONITOR
    </div>
    """, unsafe_allow_html=True)
    
    agents = [
        ("ORION", "Document Intelligence & Entity Extraction"),
        ("NEXUS-MAPPER", "Dependency Discovery & Verification"),
        ("GRAPHFORGE", "Dependency Graph & Topology"),
        ("CASCADE", "Failure Simulation & Blast Radius"),
        ("SENTINEL", "Risk Analysis & SPOF Detection"),
        ("AEGIS", "Recovery Planning & Evidence Verification")
    ]
    
    cols = st.columns(6)
    for idx, (name, role) in enumerate(agents):
        info = agent_statuses.get(name, {"status": "waiting", "detail": "Standing by"})
        status = info.get("status", "waiting")
        detail = info.get("detail", "")
        
        status_icon = "○"
        status_class = "agent-status-waiting"
        badge_border = "#1E293B"
        
        if status == "completed":
            status_icon = "✓"
            status_class = "agent-status-done"
            badge_border = "#22C55E"
        elif status == "running":
            status_icon = "⟳"
            status_class = "agent-status-running"
            badge_border = "#22D3EE"
        elif status == "error":
            status_icon = "✕"
            status_class = "agent-status-waiting"
            badge_border = "#EF4444"
            
        with cols[idx]:
            st.markdown(f"""
            <div style="background: #0D1220; border: 1px solid {badge_border}; border-radius: 8px; padding: 10px; min-height: 85px;">
              <div style="display: flex; align-items: center; font-size: 0.85rem; font-weight: 700;">
                <span class="{status_class}">{status_icon}</span>
                <span style="color: #F8FAFC;">{name}</span>
              </div>
              <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 4px; line-height: 1.2;">
                {detail if detail else role}
              </div>
            </div>
            """, unsafe_allow_html=True)


def render_impact_report(
    scenario_query: str,
    impact: ImpactResult,
    risk: RiskAnalysis,
    recovery: RecoveryPlan,
    narrative: str
):
    """
    Renders comprehensive executive impact report:
    - Failure Scenario
    - Impact Chain
    - Direct vs Indirect Impact
    - Inventory Buffer vs Outage Duration
    - Single Points of Failure
    - Documented Alternatives vs AI Suggestions
    - Supporting Evidence
    """
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    
    # 1. Header
    st.markdown(f"""
    <div style="border-bottom: 1px solid #1E293B; padding-bottom: 14px; margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="badge-critical">FAILURE SIMULATION REPORT</span>
        <span style="font-size: 0.8rem; color: #94A3B8;">Target Outage: <b>{impact.outage_duration_days:g} Days</b></span>
      </div>
      <h2 style="font-size: 1.7rem; font-weight: 700; color: #F8FAFC; margin-top: 8px; margin-bottom: 0;">
        Scenario: {scenario_query}
      </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Executive Briefing hidden/visible for TTS
    st.markdown(f'<div class="executive-briefing-text" style="display: none;">{narrative}</div>', unsafe_allow_html=True)
    
    # 2. Impact Chain Visual Flow
    if impact.impact_chains:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px;">
          DETERMINISTIC IMPACT CHAIN
        </div>
        """, unsafe_allow_html=True)
        
        for chain in impact.impact_chains[:2]:
            chain_html = []
            for i, step in enumerate(chain):
                if i == 0:
                    chain_html.append(f'<span style="background: rgba(239, 68, 68, 0.2); border: 1px solid #EF4444; color: #EF4444; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem;">🚨 {step}</span>')
                elif i == len(chain) - 1:
                    chain_html.append(f'<span style="background: rgba(34, 197, 94, 0.15); border: 1px solid #22C55E; color: #22C55E; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.85rem;">📦 {step}</span>')
                else:
                    chain_html.append(f'<span style="background: #0D1220; border: 1px solid #1E293B; color: #F8FAFC; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">{step}</span>')
            
            chain_str = ' <span style="color: #6366F1; font-weight: 700;">&rarr;</span> '.join(chain_html)
            st.markdown(f'<div style="background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 12px; overflow-x: auto; white-space: nowrap;">{chain_str}</div>', unsafe_allow_html=True)
            
    # 3. Direct vs Indirect Breakdown Columns
    col_dir, col_ind, col_prod = st.columns(3)
    
    with col_dir:
        st.markdown(f"""
        <div style="background: #0D1220; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #EF4444; font-weight: 700;">Direct Downstream Impact</div>
          <div style="font-size: 1.5rem; font-weight: 700; margin: 4px 0; color: #F8FAFC;">{len(impact.direct_impact)} Entity(s)</div>
          <div style="font-size: 0.82rem; color: #94A3B8;">{', '.join(impact.direct_impact) if impact.direct_impact else 'None'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_ind:
        st.markdown(f"""
        <div style="background: #0D1220; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #F59E0B; font-weight: 700;">Cascading / Indirect Impact</div>
          <div style="font-size: 1.5rem; font-weight: 700; margin: 4px 0; color: #F8FAFC;">{len(impact.indirect_impact)} Entity(s)</div>
          <div style="font-size: 0.82rem; color: #94A3B8;">{', '.join(impact.indirect_impact) if impact.indirect_impact else 'None'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_prod:
        st.markdown(f"""
        <div style="background: #0D1220; border: 1px solid #1E293B; border-radius: 8px; padding: 14px;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #22D3EE; font-weight: 700;">Finished Products Compromised</div>
          <div style="font-size: 1.5rem; font-weight: 700; margin: 4px 0; color: #F8FAFC;">{len(impact.terminal_products)} Product(s)</div>
          <div style="font-size: 0.82rem; color: #94A3B8;">{', '.join(impact.terminal_products) if impact.terminal_products else 'None'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 4. Inventory Runway & Gap Analysis Table
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px;">
      INVENTORY BUFFER RUNWAY & OUTAGE GAP MATH
    </div>
    """, unsafe_allow_html=True)
    
    # KPI row
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div style="background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #94A3B8;">On-Hand Inventory Coverage</div>
          <div style="font-size: 1.8rem; font-weight: 700; color: #22D3EE;">{impact.inventory_coverage_days:g} Days</div>
          <div style="font-size: 0.75rem; color: #64748B;">Calculated from Inventory.xlsx</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div style="background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #94A3B8;">Outage Duration Tested</div>
          <div style="font-size: 1.8rem; font-weight: 700; color: #F8FAFC;">{impact.outage_duration_days:g} Days</div>
          <div style="font-size: 0.75rem; color: #64748B;">Input Scenario</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        gap_col = "#EF4444" if impact.inventory_gap_days > 0 else "#22C55E"
        st.markdown(f"""
        <div style="background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; text-align: center;">
          <div style="font-size: 0.75rem; color: #94A3B8;">Production Stoppage Gap</div>
          <div style="font-size: 1.8rem; font-weight: 700; color: {gap_col};">{impact.inventory_gap_days:g} Days</div>
          <div style="font-size: 0.75rem; color: #64748B;">Unbuffered Downtime</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Multi-day comparison table
    if impact.multi_day_comparison:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        comp_rows = []
        for c in impact.multi_day_comparison:
            badge_color = "#22C55E" if c.gap_days == 0 else "#EF4444"
            comp_rows.append(f"""
            <tr style="border-bottom: 1px solid #1E293B;">
              <td style="padding: 8px 12px; font-weight: 600;">{c.duration_days:g} Days</td>
              <td style="padding: 8px 12px; color: #22D3EE;">{c.coverage_days:g} Days</td>
              <td style="padding: 8px 12px; color: {badge_color}; font-weight: 700;">{c.gap_days:g} Days</td>
              <td style="padding: 8px 12px;"><span style="color: {badge_color};">{c.status}</span></td>
              <td style="padding: 8px 12px; color: #94A3B8; font-size: 0.8rem;">{c.production_impact}</td>
            </tr>
            """)
            
        st.markdown(f"""
        <table style="width: 100%; border-collapse: collapse; background: #070A13; border: 1px solid #1E293B; border-radius: 8px; font-size: 0.85rem;">
          <thead>
            <tr style="border-bottom: 1px solid #1E293B; text-align: left; color: #94A3B8; font-size: 0.75rem; text-transform: uppercase;">
              <th style="padding: 10px 12px;">Outage Duration</th>
              <th style="padding: 10px 12px;">Inventory Coverage</th>
              <th style="padding: 10px 12px;">Buffer Gap</th>
              <th style="padding: 10px 12px;">Buffer Status</th>
              <th style="padding: 10px 12px;">Production Impact</th>
            </tr>
          </thead>
          <tbody>
            {''.join(comp_rows)}
          </tbody>
        </table>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 5. Narrative Explanation
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 6px;">
      CASCADE &bull; EXECUTIVE REASONING SUMMARY
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: #0D1220; border-left: 3px solid #6366F1; border-top: 1px solid #1E293B; border-right: 1px solid #1E293B; border-bottom: 1px solid #1E293B; border-radius: 0 8px 8px 0; padding: 16px; font-size: 0.95rem; line-height: 1.6; color: #F8FAFC;">
      {narrative}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 6. Recovery Options & Strict Factual Verification
    r_col1, r_col2 = st.columns(2)
    
    with r_col1:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #22D3EE; margin-bottom: 8px;">
          AEGIS &bull; DOCUMENTED RECOVERY OPTIONS
        </div>
        """, unsafe_allow_html=True)
        
        if recovery.documented_options:
            for opt in recovery.documented_options:
                st.markdown(f"""
                <div style="background: #070A13; border: 1px solid #22D3EE; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
                  <span class="badge-fact">📘 DOCUMENTED FACT</span>
                  <div style="font-weight: 700; color: #F8FAFC; margin-top: 6px; font-size: 0.95rem;">{opt['title']}</div>
                  <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">{opt['description']}</div>
                  <div style="color: #22D3EE; font-size: 0.75rem; margin-top: 6px; font-weight: 600;">Evidence: {opt['evidence']}</div>
                </div>
                """, unsafe_allow_html=True)
        elif recovery.no_documented_alternative_found:
            st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
              <span class="badge-critical">🚨 FACTUAL AUDIT RESULT</span>
              <div style="font-weight: 700; color: #EF4444; margin-top: 6px; font-size: 1rem;">
                No documented alternative was found in the provided data.
              </div>
              <div style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
                Neither the contracts nor the vendor database list an approved secondary supplier.
              </div>
            </div>
            """, unsafe_allow_html=True)
            
    with r_col2:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #818CF8; margin-bottom: 8px;">
          AEGIS &bull; CONTINGENCY ADVISORY
        </div>
        """, unsafe_allow_html=True)
        
        for sugg in recovery.ai_generated_suggestions:
            clean_sugg = sugg.replace("[AI-GENERATED SUGGESTION]", "").strip()
            st.markdown(f"""
            <div style="background: #070A13; border: 1px solid #1E293B; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
              <span class="badge-ai">💡 AI-GENERATED SUGGESTION</span>
              <div style="color: #F8FAFC; font-size: 0.85rem; margin-top: 6px; line-height: 1.4;">
                {clean_sugg}
              </div>
            </div>
            """, unsafe_allow_html=True)
            
    # 7. Supporting Evidence Citations
    if impact.evidence_citations:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94A3B8; margin-bottom: 8px;">
          SUPPORTING EVIDENCE & SOURCE COORDINATES
        </div>
        """, unsafe_allow_html=True)
        
        for cit in impact.evidence_citations:
            st.markdown(f"""
            <div style="background: #070A13; border: 1px solid #1E293B; border-radius: 6px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.82rem; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <span style="color: #22D3EE; font-weight: 600;">{cit.source_file}</span>
                <span style="color: #64748B;"> &bull; Section: {cit.section}</span>
                <div style="color: #F8FAFC; margin-top: 2px;">"{cit.exact_fact}"</div>
              </div>
              <span class="badge-fact">VERIFIED</span>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
