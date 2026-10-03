"""
NEXUS 2026 AI Product Experience — Visual Identity & Design System
Palette:
  Background:       #070A13
  Main Surface:     #0D1220
  Glass Surface:    #111827 / rgba(17, 24, 39, 0.8)
  Primary Accent:   #6366F1 (Indigo)
  Secondary Accent: #22D3EE (Cyan)
  Success:          #22C55E
  Warning:          #F59E0B
  Critical:         #EF4444
  Main Text:        #F8FAFC
  Secondary Text:   #94A3B8
  Borders:          #1E293B
"""

NEXUS_CUSTOM_CSS = """
<style>
/* Global Reset and Background */
[data-testid="stAppViewContainer"] {
    background-color: #070A13;
    color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}

[data-testid="stSidebar"] {
    background-color: #0D1220 !important;
    border-right: 1px solid #1E293B !important;
}

/* Glass Surface Cards */
.nexus-card {
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nexus-card:hover {
    border-color: #6366F1;
    box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
}

.nexus-metric-box {
    background: #0D1220;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.nexus-metric-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #6366F1, #22D3EE);
}

.nexus-metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #F8FAFC;
    margin-top: 4px;
}

.nexus-metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94A3B8;
}

/* Header & Hero Glow */
.hero-glow-container {
    text-align: center;
    padding: 30px 10px 20px 10px;
    position: relative;
}

.hero-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 320px;
    height: 120px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(34, 211, 238, 0.15) 50%, rgba(0, 0, 0, 0) 80%);
    filter: blur(40px);
    z-index: 0;
    pointer-events: none;
    animation: breathingGlow 8s ease-in-out infinite alternate;
}

@keyframes breathingGlow {
    0% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.6; }
    100% { transform: translate(-50%, -50%) scale(1.15); opacity: 0.95; }
}

.hero-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.4);
    color: #22D3EE;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    padding: 4px 14px;
    border-radius: 9999px;
    margin-bottom: 14px;
    position: relative;
    z-index: 1;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, #FFFFFF 40%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.1;
    position: relative;
    z-index: 1;
}

.hero-tagline {
    font-size: 1.15rem;
    color: #94A3B8;
    margin-top: 10px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    position: relative;
    z-index: 1;
}

/* Agent Activity Stream */
.agent-pill {
    display: flex;
    align-items: center;
    background: #0D1220;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.9rem;
}

.agent-status-done {
    color: #22C55E;
    font-weight: 700;
    margin-right: 10px;
}

.agent-status-running {
    color: #22D3EE;
    font-weight: 700;
    margin-right: 10px;
    animation: pulse 1.5s infinite;
}

.agent-status-waiting {
    color: #64748B;
    margin-right: 10px;
}

@keyframes pulse {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}

/* Tag styles */
.badge-fact {
    background: rgba(34, 211, 238, 0.12);
    border: 1px solid #22D3EE;
    color: #22D3EE;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-ai {
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid #6366F1;
    color: #818CF8;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-critical {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #EF4444;
    color: #EF4444;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    display: inline-block;
}

/* Buttons */
.stButton>button {
    background-color: #0D1220 !important;
    color: #F8FAFC !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    border-color: #6366F1 !important;
    color: #22D3EE !important;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.3) !important;
}

/* Primary Action Buttons */
.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    color: #FFFFFF !important;
    border: 1px solid #818CF8 !important;
}

.stButton>button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5, #4338CA) !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.5) !important;
}

/* Form Inputs */
.stTextInput>div>div>input {
    background-color: #0D1220 !important;
    color: #F8FAFC !important;
    border: 1px solid #1E293B !important;
    border-radius: 8px !important;
}

.stTextInput>div>div>input:focus {
    border-color: #6366F1 !important;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.25) !important;
}
</style>
"""


def get_css() -> str:
    """Returns the CSS block for embedding into Streamlit."""
    return NEXUS_CUSTOM_CSS
