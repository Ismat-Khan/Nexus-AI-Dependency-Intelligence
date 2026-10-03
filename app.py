"""
NEXUS — AI Dependency Intelligence & Failure Simulation
Main Streamlit Application Entrypoint
Target Deployment: Streamlit Cloud / GitHub
"""

import os
import streamlit as st
import streamlit.components.v1 as components

# Configure Streamlit Page
st.set_page_config(
    page_title="NEXUS // AI Dependency Intelligence",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import NEXUS Engine and UI components
from ui.styles import get_css
from ui.background import render_background_canvas
from ui.components import (
    render_hero_header,
    render_pipeline_badge,
    render_metrics_dashboard,
    render_agent_activity_feed,
    render_impact_report
)
from ui.graph_viz import generate_interactive_graph_html
from ui.voice import render_voice_interface
from core.pipeline import NexusPipeline
from core.llm import is_groq_available, get_groq_api_key, PREFERRED_MODEL
from agents.graphforge import GraphForgeAgent


# Inject 2026 AI Product Experience Styling & Background
st.markdown(get_css(), unsafe_allow_html=True)
st.components.v1.html(render_background_canvas(), height=0, width=0)

# Session State Initialization
if "pipeline" not in st.session_state:
    st.session_state.pipeline = NexusPipeline()
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = "What happens if Supplier A is unavailable for 7 days?"
if "scenario_result" not in st.session_state:
    st.session_state.scenario_result = None
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {}
if "selected_failed_node" not in st.session_state:
    st.session_state.selected_failed_node = None
if "affected_nodes" not in st.session_state:
    st.session_state.affected_nodes = []

# Status update callback for agent monitoring
def agent_callback(agent_name: str, status: str, detail: str):
    st.session_state.agent_statuses[agent_name] = {
        "status": status,
        "detail": detail
    }

st.session_state.pipeline.engine.status_callback = agent_callback

# Load initial Voltra Mobility demo if empty
if not st.session_state.pipeline.current_state:
    st.session_state.pipeline.load_demo()


# ---------------------------------------------------------
# SIDEBAR: Control Center & Environment Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
      <span style="font-size: 1.6rem;">🕸️</span>
      <div>
        <div style="font-size: 1.1rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">NEXUS</div>
        <div style="font-size: 0.75rem; color: #22D3EE; font-weight: 600;">CONTROL CENTER</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Configuration
    groq_active = is_groq_available()
    if groq_active:
        st.markdown("""
        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22C55E; border-radius: 8px; padding: 10px; margin-bottom: 15px; font-size: 0.8rem; color: #22C55E;">
          <b>✓ Groq API Key Connected</b><br/>
          Live reasoning model: <code>openai/gpt-oss-120b</code>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; border-radius: 8px; padding: 10px; margin-bottom: 15px; font-size: 0.8rem; color: #F59E0B;">
          <b>⚠️ No GROQ_API_KEY Detected</b><br/>
          Running in <b>Deterministic Offline Mode</b>. Add key below or in Streamlit Secrets for live LLM reasoning.
        </div>
        """, unsafe_allow_html=True)
        user_key = st.text_input("Enter Groq API Key:", type="password", key="sidebar_groq_key")
        if user_key:
            os.environ["GROQ_API_KEY"] = user_key.strip()
            st.rerun()
            
    st.markdown("---")
    
    # Ingestion Actions
    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;'>Data Ingestion</div>", unsafe_allow_html=True)
    
    if st.button("🚀 Load Voltra Mobility Demo", use_container_width=True, type="primary"):
        with st.spinner("Loading synthetic Voltra Mobility dataset..."):
            st.session_state.pipeline.load_demo()
            st.session_state.scenario_result = None
            st.session_state.selected_failed_node = None
            st.session_state.affected_nodes = []
            st.rerun()
            
    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload Organization Files",
        type=["pdf", "xlsx", "xls", "csv", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Upload contracts, inventory logs, machine specs, or SOPs."
    )
    
    if uploaded_files:
        if st.button("⚡ Ingest & Analyze Uploaded Files", use_container_width=True):
            file_payloads = []
            for up in uploaded_files:
                file_payloads.append({
                    "name": up.name,
                    "content": up.getvalue()
                })
            with st.spinner("ORION & MAPPER parsing documents and generating graph..."):
                st.session_state.pipeline.ingest_files(file_payloads, use_llm=groq_active)
                st.session_state.scenario_result = None
                st.session_state.selected_failed_node = None
                st.session_state.affected_nodes = []
                st.rerun()
                
    st.markdown("---")
    
    # Active Organization / File List
    curr = st.session_state.pipeline.current_state
    if curr:
        st.markdown(f"**Dataset**: `{curr.get('organization', 'Workspace')}`")
        with st.expander("📁 Loaded Documents", expanded=False):
            for fn in curr.get("file_names", []):
                st.caption(f"• {fn}")
                
    st.markdown("---")
    st.caption("NEXUS v2.6 // Hackathon Edition")
    st.caption("Built for Streamlit Cloud deployment.")


# ---------------------------------------------------------
# MAIN INTERFACE
# ---------------------------------------------------------

# 1. Hero Title & Tagline
render_hero_header()

curr_state = st.session_state.pipeline.current_state
is_demo = curr_state.get("is_demo", True)
render_pipeline_badge(is_live=not is_demo, model_name=PREFERRED_MODEL)

# 2. Executive Metrics Dashboard
metrics = curr_state.get("metrics", {})
docs_count = len(curr_state.get("file_names", []))
entities_count = len(curr_state.get("entities", []))
deps_count = len(curr_state.get("dependencies", []))
critical_links = len(metrics.get("spofs", [])) + 2
spof_count = metrics.get("spof_count", 0)

render_metrics_dashboard(
    docs_count=docs_count,
    entities_count=entities_count,
    deps_count=deps_count,
    critical_deps_count=critical_links,
    spof_count=spof_count
)

st.markdown("<br/>", unsafe_allow_html=True)

# 3. Interactive Dependency Graph Section
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 10px;">
  <div>
    <span style="font-size: 0.8rem; font-weight: 700; color: #22D3EE; letter-spacing: 0.08em; text-transform: uppercase;">Topological Model</span>
    <h3 style="margin: 0; font-size: 1.4rem; color: #F8FAFC;">GRAPHFORGE Interactive Dependency Graph</h3>
  </div>
  <div style="font-size: 0.8rem; color: #94A3B8;">Click any node to inspect metadata and evidence</div>
</div>
""", unsafe_allow_html=True)

graph = curr_state.get("graph")
forge_agent = GraphForgeAgent()

# Export graph for Vis.js visualization
graph_export = forge_agent.export_graph_for_visualization(
    graph,
    failed_node=st.session_state.selected_failed_node,
    affected_nodes=st.session_state.affected_nodes
)
graph_html = generate_interactive_graph_html(graph_export, height=520)
components.html(graph_html, height=530)

st.markdown("<br/>", unsafe_allow_html=True)

# 4. Scenario Lab Section
st.markdown("""
<div class="nexus-card">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <div>
      <span class="badge-ai">CASCADE SCENARIO LAB</span>
      <h3 style="margin: 4px 0 0 0; font-size: 1.4rem; color: #F8FAFC;">Simulate Failure & Supply Chain Shocks</h3>
    </div>
  </div>
""", unsafe_allow_html=True)

# Voice Interface Component (Web Speech API)
components.html(render_voice_interface(), height=130)

# Quick Preset Buttons
st.markdown("<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px; font-weight: 600;'>DEMO PRESETS:</div>", unsafe_allow_html=True)
p1, p2, p3 = st.columns(3)

with p1:
    if st.button("🚨 Case 1: Supplier A fails for 7 days (SPOF)", use_container_width=True):
        st.session_state.current_scenario = "What happens if Supplier A is unavailable for 7 days?"
        st.session_state.trigger_sim = True
with p2:
    if st.button("🛡️ Case 2: VoltCell fails for 14 days (Backup)", use_container_width=True):
        st.session_state.current_scenario = "What happens if VoltCell Energy is unavailable for 14 days?"
        st.session_state.trigger_sim = True
with p3:
    if st.button("⚙️ Case 3: SMT Robot #4 fails for 2 days", use_container_width=True):
        st.session_state.current_scenario = "What happens if SMT Robot #4 fails for 2 days?"
        st.session_state.trigger_sim = True

# Scenario Query Input
scenario_query = st.text_input(
    "Enter failure query or hypothesis:",
    value=st.session_state.current_scenario,
    placeholder="e.g., What happens if Supplier A is unavailable for 7 days?"
)

run_button = st.button("⚡ Run Deterministic Failure Simulation", type="primary", use_container_width=True)

if run_button or st.session_state.get("trigger_sim", False):
    st.session_state.trigger_sim = False
    with st.spinner("Executing CASCADE -> SENTINEL -> AEGIS multi-agent pipeline..."):
        res = st.session_state.pipeline.run_scenario(scenario_query, use_llm=groq_active)
        st.session_state.scenario_result = res
        st.session_state.selected_failed_node = res["failed_node"]
        st.session_state.affected_nodes = res["impact_result"].all_affected_nodes
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 5. Live Agent Swarm Execution Monitor
render_agent_activity_feed(st.session_state.agent_statuses)

st.markdown("<br/>", unsafe_allow_html=True)

# 6. Executive Impact Report
if st.session_state.scenario_result:
    res = st.session_state.scenario_result
    render_impact_report(
        scenario_query=st.session_state.current_scenario,
        impact=res["impact_result"],
        risk=res["risk_analysis"],
        recovery=res["recovery_plan"],
        narrative=res["narrative"]
    )
