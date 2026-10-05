"""
NEXUS Interactive Dependency Graph Visualizer
Renders an interactive, physics-enabled Vis.js / PyVis network directly in Streamlit.
Dark futuristic theme matching NEXUS palette, node inspection modal,
failure path highlighting, and zero temporary file dependencies.
"""

import json
from typing import Dict, List, Any, Optional


def generate_interactive_graph_html(graph_export: Dict[str, Any], height: int = 580) -> str:
    """
    Produces standalone Vis.js network HTML with interactive node inspector.
    """
    nodes_json = json.dumps(graph_export["nodes"])
    edges_json = json.dumps(graph_export["edges"])

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #070A13;
      color: #F8FAFC;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
      overflow: hidden;
    }}
    #mynetwork {{
      width: 100%;
      height: {height}px;
      border: 1px solid #1E293B;
      border-radius: 12px;
      background: radial-gradient(circle at center, #0D1220 0%, #070A13 100%);
    }}
    #node-inspector {{
      position: absolute;
      top: 15px;
      right: 15px;
      width: 290px;
      background: rgba(17, 24, 39, 0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid #6366F1;
      border-radius: 10px;
      padding: 16px;
      font-size: 0.85rem;
      display: none;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      z-index: 100;
    }}
    .inspector-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #22D3EE;
      margin-bottom: 8px;
    }}
    .inspector-field {{
      margin-bottom: 6px;
      color: #94A3B8;
    }}
    .inspector-val {{
      color: #F8FAFC;
      font-weight: 500;
    }}
    .legend-container {{
      position: absolute;
      bottom: 15px;
      left: 15px;
      background: rgba(13, 18, 32, 0.85);
      border: 1px solid #1E293B;
      border-radius: 8px;
      padding: 8px 14px;
      font-size: 0.75rem;
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      z-index: 99;
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-dot {{
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }}
  </style>
</head>
<body>

  <div id="mynetwork"></div>

  <div id="node-inspector">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
      <div id="insp-title" class="inspector-title">Node Details</div>
      <span style="cursor: pointer; color: #94A3B8; font-size: 1rem;" onclick="document.getElementById('node-inspector').style.display='none'">✕</span>
    </div>
    <div class="inspector-field">Type: <span id="insp-type" class="inspector-val"></span></div>
    <div class="inspector-field">Inventory Coverage: <span id="insp-inv" class="inspector-val"></span></div>
    <div class="inspector-field">Documented Backup: <span id="insp-backup" class="inspector-val"></span></div>
    <div class="inspector-field">Source Document: <span id="insp-source" class="inspector-val"></span></div>
    <div style="margin-top: 10px; border-top: 1px solid #1E293B; padding-top: 8px;">
      <div class="inspector-field" style="color: #6366F1; font-weight: 600;">Status:</div>
      <div id="insp-status" style="font-weight: 600;"></div>
    </div>
  </div>

  <div class="legend-container">
    <div class="legend-item"><div class="legend-dot" style="background: #22D3EE;"></div>Supplier</div>
    <div class="legend-item"><div class="legend-dot" style="background: #6366F1;"></div>Component</div>
    <div class="legend-item"><div class="legend-dot" style="background: #F59E0B;"></div>Machine</div>
    <div class="legend-item"><div class="legend-dot" style="background: #A855F7;"></div>Process</div>
    <div class="legend-item"><div class="legend-dot" style="background: #22C55E;"></div>Product</div>
    <div class="legend-item"><div class="legend-dot" style="background: #EF4444;"></div>Failed Node</div>
    <div class="legend-item"><div class="legend-dot" style="background: #F43F5E;"></div>Affected Node</div>
  </div>

  <script type="text/javascript">
    const rawNodes = {nodes_json};
    const rawEdges = {edges_json};

    const nodeDict = {{}};
    const visNodes = rawNodes.map(n => {{
      nodeDict[n.id] = n;
      let borderWidth = n.is_failed ? 4 : (n.is_affected ? 2 : 1);
      let borderColor = n.is_failed ? '#FFFFFF' : '#1E293B';
      return {{
        id: n.id,
        label: n.label,
        title: (n.title || '')
          .replace(/<br\s*\/?>/gi, ' | ')
          .replace(/<[^>]*>/g, ''),
        shape: 'box',
        margin: 10,
        color: {{
          background: n.color,
          border: borderColor,
          highlight: {{
            background: '#818CF8',
            border: '#22D3EE'
          }}
        }},
        font: {{
          color: '#FFFFFF',
          face: 'sans-serif',
          size: 13,
          bold: true
        }},
        borderWidth: borderWidth,
        shadow: {{
          enabled: true,
          color: n.is_failed ? 'rgba(239, 68, 68, 0.6)' : 'rgba(0, 0, 0, 0.5)',
          size: n.is_failed ? 15 : 6
        }}
      }};
    }});

    const visEdges = rawEdges.map(e => ({{
      from: e.from,
      to: e.to,
      label: e.label,
      title: e.title,
      arrows: 'to',
      color: {{
        color: e.color,
        highlight: '#22D3EE'
      }},
      font: {{
        color: '#94A3B8',
        size: 10,
        align: 'middle'
      }},
      smooth: {{
        type: 'cubicBezier',
        roundness: 0.2
      }}
    }}));

    const container = document.getElementById('mynetwork');
    const data = {{
      nodes: new vis.DataSet(visNodes),
      edges: new vis.DataSet(visEdges)
    }};

    const options = {{
      layout: {{
        hierarchical: {{
          enabled: true,
          direction: 'LR',
          sortMethod: 'directed',
          levelSeparation: 190,
          nodeSpacing: 100
        }}
      }},
      physics: {{
        hierarchicalRepulsion: {{
          nodeDistance: 130
        }}
      }},
      interaction: {{
        hover: true,
        tooltipDelay: 100,
        zoomView: false,
        dragView: true
      }}
    }};

    const network = new vis.Network(container, data, options);

    // Keep graph panning enabled after zooming.
    // Left mouse drag moves the graph without changing zoom.
    network.setOptions({
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: false,
        dragView: true,
        dragNodes: false
      }
    });

    // Normal mouse wheel = page scrolling.
    // Touchpad two-finger pinch = graph zoom.
    // Mouse drag = move the graph.

    let lastTouchDistance = null;

    // Chrome/Edge normally report a touchpad pinch as ctrlKey + wheel.
    // This does NOT require the user to physically press Ctrl.
    container.addEventListener("wheel", function(event) {{
      if (event.ctrlKey || event.metaKey) {{
        event.preventDefault();

        const currentScale = network.getScale();
        const minScale = 0.35;
        const maxScale = 2.5;

        const newScale = event.deltaY < 0
          ? Math.min(currentScale * 1.06, maxScale)
          : Math.max(currentScale * 0.94, minScale);

        network.moveTo({{
          scale: newScale,
          animation: {{
            duration: 80,
            easingFunction: "easeInOutQuad"
          }}
        }});
      }}
    }}, {{ passive: false }});

    // Extra support for devices that send real touch events.
    container.addEventListener("touchstart", function(event) {{
      if (event.touches.length === 2) {{
        const dx = event.touches[0].clientX - event.touches[1].clientX;
        const dy = event.touches[0].clientY - event.touches[1].clientY;
        lastTouchDistance = Math.sqrt(dx * dx + dy * dy);
      }}
    }}, {{ passive: true }});

    container.addEventListener("touchmove", function(event) {{
      if (event.touches.length !== 2 || lastTouchDistance === null) {{
        return;
      }}

      event.preventDefault();

      const dx = event.touches[0].clientX - event.touches[1].clientX;
      const dy = event.touches[0].clientY - event.touches[1].clientY;
      const currentDistance = Math.sqrt(dx * dx + dy * dy);
      const difference = currentDistance - lastTouchDistance;

      if (Math.abs(difference) > 1) {{
        const currentScale = network.getScale();
        const minScale = 0.35;
        const maxScale = 2.5;

        const newScale = difference > 0
          ? Math.min(currentScale * 1.03, maxScale)
          : Math.max(currentScale * 0.97, minScale);

        network.moveTo({{
          scale: newScale,
          animation: {{
            duration: 50,
            easingFunction: "linear"
          }}
        }});

        lastTouchDistance = currentDistance;
      }}
    }}, {{ passive: false }});

    container.addEventListener("touchend", function(event) {{
      if (event.touches.length < 2) {{
        lastTouchDistance = null;
      }}
    }}, {{ passive: true }});

    // Inspector Click Handler
    network.on("click", function(params) {{
      if (params.nodes.length > 0) {{
        const nodeId = params.nodes[0];
        const info = nodeDict[nodeId];
        if (info) {{
          document.getElementById('insp-title').textContent = info.label;
          document.getElementById('insp-type').textContent = (info.type || 'System').toUpperCase();
          document.getElementById('insp-inv').textContent = info.inventory_days !== null && info.inventory_days !== undefined ? (info.inventory_days + ' days') : 'N/A';
          document.getElementById('insp-backup').textContent = info.backup_supplier || 'None Certified (SPOF Risk)';
          document.getElementById('insp-source').textContent = info.source_doc || 'Extracted Corpus';

          const statusEl = document.getElementById('insp-status');
          if (info.is_failed) {{
            statusEl.textContent = '🚨 ROOT FAILURE SIMULATION TARGET';
            statusEl.style.color = '#EF4444';
          }} else if (info.is_affected) {{
            statusEl.textContent = '⚠️ IMPACTED BY CASCADING FAILURE';
            statusEl.style.color = '#F43F5E';
          }} else {{
            statusEl.textContent = '✓ Operational';
            statusEl.style.color = '#22C55E';
          }}

          document.getElementById('node-inspector').style.display = 'block';
        }}
      }}
    }});
  </script>
</body>
</html>
"""
    return html
