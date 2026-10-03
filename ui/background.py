"""
NEXUS Living Dependency Network Background
Lightweight, elegant, dark ambient canvas rendering subtle particles,
faint dependency lines, and slow glowing light fields.
Non-intrusive (pointer-events: none, z-index: -1, CPU < 1%).
Respects prefers-reduced-motion.
"""

BACKGROUND_CANVAS_HTML = """
<div id="nexus-bg-container" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; overflow: hidden; background: #070A13;">
  <canvas id="nexus-canvas" style="display: block; width: 100%; height: 100%; opacity: 0.45;"></canvas>
</div>

<script>
(function() {
  const canvas = document.getElementById('nexus-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  
  // Respect prefers-reduced-motion
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  
  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();
  
  // Sparse, elegant particles
  const particleCount = prefersReduced ? 10 : 28;
  const particles = [];
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      radius: Math.random() * 1.5 + 1.0,
      color: i % 2 === 0 ? 'rgba(99, 102, 241, ' : 'rgba(34, 211, 238, '
    });
  }
  
  let lastTime = 0;
  function animate(timestamp) {
    if (!lastTime) lastTime = timestamp;
    const dt = timestamp - lastTime;
    
    // Target ~30fps for minimal CPU usage
    if (dt > 32) {
      lastTime = timestamp;
      ctx.clearRect(0, 0, width, height);
      
      // Draw subtle ambient glow spots
      const grad = ctx.createRadialGradient(width * 0.2, height * 0.3, 50, width * 0.2, height * 0.3, 400);
      grad.addColorStop(0, 'rgba(99, 102, 241, 0.04)');
      grad.addColorStop(1, 'rgba(7, 10, 19, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);
      
      const grad2 = ctx.createRadialGradient(width * 0.8, height * 0.7, 50, width * 0.8, height * 0.7, 450);
      grad2.addColorStop(0, 'rgba(34, 211, 238, 0.03)');
      grad2.addColorStop(1, 'rgba(7, 10, 19, 0)');
      ctx.fillStyle = grad2;
      ctx.fillRect(0, 0, width, height);
      
      // Update and draw particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (!prefersReduced) {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0) p.x = width;
          if (p.x > width) p.x = 0;
          if (p.y < 0) p.y = height;
          if (p.y > height) p.y = 0;
        }
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color + '0.6)';
        ctx.fill();
        
        // Connect nearby particles with subtle dependency lines
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 130) {
            const alpha = (1 - dist / 130) * 0.18;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }
    }
    requestAnimationFrame(animate);
  }
  
  requestAnimationFrame(animate);
})();
</script>
"""


def render_background_canvas():
    """Returns HTML component string for embedding the animated background."""
    return BACKGROUND_CANVAS_HTML
