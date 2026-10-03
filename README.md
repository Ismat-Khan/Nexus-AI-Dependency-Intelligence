# NEXUS — AI Dependency Intelligence & Failure Simulation

> **See what depends on what. Simulate what happens when something fails.**

![NEXUS Version](https://img.shields.io/badge/NEXUS-v2.6%20Hackathon%20Edition-6366F1?style=for-the-badge)
![Streamlit Cloud](https://img.shields.io/badge/Deployment-Streamlit%20Cloud-FF4B4B?style=for-the-badge)
![Groq](https://img.shields.io/badge/LLM-Groq%20API-F55036?style=for-the-badge)
![NetworkX](https://img.shields.io/badge/Graph%20Engine-NetworkX%203.x-22D3EE?style=for-the-badge)

NEXUS is an autonomous multi-agent AI system for organizational dependency intelligence. Organizations have critical manufacturing and operational facts scattered across unstructured documents (PDF, DOCX, TXT, MD) and datasets (XLSX, XLS, CSV). NEXUS analyzes these sources, extracts verified entities and verbatim evidence, discovers multi-tier dependencies, builds an interactive dependency graph, and simulates failure scenarios with deterministic mathematical precision.

---

## 🚀 The Core Innovation: Deterministic Traversal + Grounded Reasoning

NEXUS is **NOT** a simple document chatbot. In high-stakes manufacturing and operational systems, allowing an LLM to invent impact chains or hallucinate inventory math causes catastrophic errors.

NEXUS enforces strict separation:

```text
Uploaded Documents & Spreadsheets
               ↓
      ORION (Entity & Fact Extraction)
               ↓
      NEXUS-MAPPER (Dependency Discovery)
               ↓
      GRAPHFORGE (Directed Graph Construction)
               ↓
         Interactive Dependency Graph
               ↓
         Failure Scenario Query
               ↓
      CASCADE (Deterministic Graph Traversal & Blast Radius)
               ↓
      Python NetworkX / Inventory Math (Zero Hallucination)
               ↓
      SENTINEL (SPOF & Bottleneck Analysis)
               ↓
      AEGIS (Evidence-Backed Recovery Options)
               ↓
         Executive Impact Report
```

**The golden rule:**
- **NetworkX & Python calculate and verify.**
- **The LLM reasons and explains.**

---

## 🤖 The Six Core Agents

| Agent | Codename | Role & Responsibility |
|---|---|---|
| **ORION** | *Document Intelligence* | Reads PDF, DOCX, XLSX, CSV, and text files. Extracts verified entities (Suppliers, Components, Machines, Processes, Products) and preserves verbatim source citations. |
| **NEXUS-MAPPER** | *Dependency Discovery* | Discovers grounded causal links (`Supplier A` &rarr; `Component X` &rarr; `Machine B` &rarr; `Process C` &rarr; `Product D`). Rejects unsupported relationships. |
| **GRAPHFORGE** | *Graph Engine* | Converts relationships into a directed NetworkX graph, enriches nodes with burn rates and buffer levels, and exports interactive Vis.js visualization. |
| **CASCADE** | *Failure Simulation* | Executes deterministic downstream BFS/DFS traversal to calculate blast radius, affected finished products, and inventory outage gaps. Synthesizes an executive debrief without altering numbers. |
| **SENTINEL** | *Risk Analysis* | Detects cut-vertices, bottlenecks, and Single Points of Failure (SPOFs). Evaluates topological vulnerability and calculates 0–100 Risk Scores. |
| **AEGIS** | *Recovery Planning* | Audits company records for certified backup suppliers and SOP workarounds. Strictly enforces: *"No documented alternative was found in the provided data"* when no backup exists. |

---

## ⚡ Planted Hackathon Demo: Voltra Mobility

NEXUS includes an instant 1-click synthetic demo company: **Voltra Mobility** (an electric urban vehicle manufacturer).

### The Three Planted Benchmark Cases:

1. **Case 1 — Single Point of Failure (SPOF)**:
   - **Apex Microelectronics** supplies **Microcontroller MCU-900**.
   - No documented backup exists in company contracts (`Supply_Contracts.pdf`).
   - The graph and risk engine deterministically identify Apex and MCU-900 as Single Points of Failure halting final assembly of the **Voltra Model V-1**.

2. **Case 2 — Documented Backup**:
   - **VoltCell Energy** supplies **Lithium-Ion Battery Cells**.
   - Company records explicitly document **Amperex Dynamics** as an approved secondary supplier with a 3-day activation SLA.
   - AEGIS recognizes this critical link is protected by a certified alternative.

3. **Case 3 — Inventory Buffer Runway & Outage Gap Math**:
   - MCU-900 inventory on hand: **2,500 units**
   - Daily burn rate: **500 units/day**
   - Inventory coverage: **5 days**
   - User simulates: *"What happens if Supplier A is unavailable for 7 days?"*
   - **Deterministic result**:
     - Inventory Coverage = `5 days`
     - Outage Duration = `7 days`
     - **Production Gap = `2 days`** of unbuffered total plant shutdown!
   - Multi-day comparison matrix calculates impact across 1 day, 7 days, 14 days, and 30 days.

---

## 🎤 Voice Interaction (Web Speech API)

NEXUS includes client-side voice interaction:
- **Speech-to-Text**: Click **"🎙️ Speak Scenario"** and state your failure query into your microphone. Transcribed instantly in your browser.
- **Text-to-Speech**: Click **"🔊 Listen to Executive Briefing"** to hear an audio readout of the cascading failure impact.
- **Zero-Cost & Zero-Config**: Runs 100% in modern browsers (Chrome, Edge, Safari) without requiring paid voice API keys!

---

## 🎨 2026 AI Product Experience (UI Design)

- **Palette**: Dark, intelligent, precise, and premium (`#070A13` background, `#0D1220` surface, `#6366F1` indigo accent, `#22D3EE` cyan accent, `#EF4444` critical alert).
- **Living Dependency Network Background**: Lightweight HTML5 ambient canvas rendering subtle particles, glowing light sweeps, and faint dependency lines (non-blocking, CPU < 1%, respects `prefers-reduced-motion`).
- **Interactive Graph Visualizer**: Pan, zoom, and click nodes to open an inspection drawer showing inventory days, backup status, and source documents.
- **Live Swarm Monitor**: Displays real status badges for each agent during execution (`✓ Completed`, `⟳ Running`, `○ Waiting`).

---

## 📦 Project Structure

```text
nexus/
├── app.py                     # Main Streamlit application entrypoint
├── requirements.txt           # Deployment dependencies
├── runtime.txt                # Python 3.11 target
├── README.md                  # Complete documentation
├── .gitignore                 # GitHub ignore rules
│
├── .streamlit/
│   └── config.toml            # Dark theme and server parameters
│
├── agents/                    # Conceptual CrewAI agents
│   ├── __init__.py
│   ├── orion.py               # ORION (Document Intelligence)
│   ├── mapper.py              # NEXUS-MAPPER (Dependency Discovery)
│   ├── graphforge.py          # GRAPHFORGE (Graph Engine)
│   ├── cascade.py             # CASCADE (Failure Simulation)
│   ├── sentinel.py            # SENTINEL (Risk Analysis)
│   └── aegis.py               # AEGIS (Recovery Planning)
│
├── tools/                     # Deterministic Python tools
│   ├── __init__.py
│   ├── document_tools.py      # PDF, DOCX, TXT, MD, CSV parsers
│   ├── spreadsheet_tools.py   # Excel & CSV tabular extractors
│   ├── graph_tools.py         # NetworkX topology & SPOF detector
│   ├── simulation_tools.py    # Outage gap & blast radius calculator
│   └── evidence_tools.py      # Verbatim citation tracker & fact labeler
│
├── core/                      # Architecture & models
│   ├── __init__.py
│   ├── models.py              # Pydantic schemas
│   ├── llm.py                 # Groq client & fallback negotiator
│   ├── crew.py                # Multi-agent orchestrator & status callbacks
│   ├── pipeline.py            # Central pipeline controller
│   └── cache.py               # Session state & Voltra Mobility demo loader
│
├── ui/                        # Presentation layer
│   ├── __init__.py
│   ├── styles.py              # Custom CSS & 2026 design system
│   ├── background.py          # Living dependency network canvas
│   ├── components.py          # Metrics, feeds, reports, and tables
│   ├── graph_viz.py           # Interactive Vis.js network visualizer
│   └── voice.py               # Web Speech STT & TTS interface
│
├── data/
│   └── demo/                  # Synthetic Voltra Mobility datasets
│       ├── Suppliers.xlsx
│       ├── Inventory.xlsx
│       ├── Production_Process.pdf
│       ├── Machine_Requirements.pdf
│       ├── Supply_Contracts.pdf
│       └── Operations_SOP.docx
│
└── scripts/
    └── generate_demo_data.py  # Standalone synthetic data generator
```

---

## ☁️ Deployment Guide: Streamlit Cloud (1-Click)

NEXUS was designed specifically for frictionless deployment to **Streamlit Cloud**:

```text
Extract ZIP
     ↓
Push to GitHub Repository
     ↓
Connect to Streamlit Cloud (https://share.streamlit.io)
     ↓
Select Main file path: app.py
     ↓
Add Secret: GROQ_API_KEY = "gsk_..."
     ↓
Deploy!
```

### Adding Your Groq API Key:
In Streamlit Cloud:
1. Go to your app dashboard.
2. Click **Settings** &rarr; **Secrets**.
3. Add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
4. Click **Save**.

*Note: If no API key is provided, NEXUS runs gracefully in **Deterministic Offline Mode** with full graph simulation, inventory calculations, and rule-based debriefs!*

---

## 🧪 Hackathon 2-Minute Presentation Walkthrough

1. **Load Voltra Mobility Demo**:
   Click **"🚀 Load Voltra Mobility Demo"** in the sidebar. Loads instantly.
2. **Review Metrics**:
   Observe real calculated figures: 6 Documents, 16 Entities, 14 Dependencies, 1 Single Point of Failure.
3. **Inspect Interactive Graph**:
   Explore the visual flow: `Supplier` &rarr; `Component` &rarr; `Machine` &rarr; `Process` &rarr; `Product`. Click on `Apex Microelectronics` or `Microcontroller MCU-900` to inspect inventory and backup status.
4. **Run Scenario**:
   In the **Scenario Lab**, click the quick preset:
   > **🚨 Case 1: Supplier A fails for 7 days (SPOF)**
   Click **"⚡ Run Deterministic Failure Simulation"**.
5. **Observe Agent Execution**:
   Watch the live agent execution stream: `CASCADE` &rarr; `SENTINEL` &rarr; `AEGIS`.
6. **Verify Deterministic Results in Impact Report**:
   - **Direct Impact**: `Microcontroller MCU-900`
   - **Indirect Impact**: `SMT Robot #4`, `ECU Sub-assembly`, `Final Vehicle Synthesis`
   - **Products Stalled**: `Voltra Model V-1`, `Voltra Commercial Fleet Van`
   - **Inventory Runway**: `5.0 Days`
   - **Outage Gap**: `2.0 Days` of total production stoppage!
   - **Multi-Day Table**: Compare 1 day (0 gap), 7 days (2 days gap), 14 days (9 days gap).
   - **Recovery Verification**: Explicitly states: *"No documented alternative was found in the provided data."*
7. **Test Voice**:
   Click **"🔊 Listen to Executive Briefing"** to hear the audio summary read aloud!

---

## 🔒 Security & Factual Integrity

- **Zero Hard-coded Secrets**: Keys are accessed strictly through environment variables or `st.secrets`.
- **Factual Integrity Tagging**:
  - `📘 DOCUMENTED FACT`: Grounded directly in uploaded documents.
  - `🤖 AI-GENERATED EXPLANATION`: Natural language reasoning over verified math.
  - `💡 AI-GENERATED SUGGESTION`: Clearly labeled advisory suggestions.
