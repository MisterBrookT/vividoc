# Style: Airy Glass

## Color palette
- Background: `#f1f5f9` (light slate-gray, like overcast sky)
- Card: `rgba(255,255,255,0.7)` + `backdrop-filter: blur(10px)` — glassmorphism
- Inner widget: `rgba(255,255,255,0.8)`
- Canvas background: `radial-gradient(circle, #f8fafc 0%, #e2e8f0 100%)` — soft vignette
- Primary: `#0284c7` (sky blue)
- Secondary: `#0369a1` (deeper blue for math)
- Text: `#334155` (dark slate), `#475569` (body)
- Border: `#cbd5e1` (light), `#e2e8f0`
- Math box: `rgba(56,189,248,0.1)` tint, `border-left: 4px solid #0284c7`

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, letter-spacing: 2px
- Body: Merriweather, 300 weight
- Values: Space Mono

## Layout
- Single centered column, max-width 850px
- Glassmorphism card: white semi-transparent + backdrop-filter blur
- Soft box shadows: `0 20px 40px rgba(14,165,233,0.1)` — light, airy
- Canvas `cursor: grab` / `cursor: grabbing` — signals rotation

## Controls signature
No explicit controls — all interaction is click-drag on the canvas.
A `drag-prompt` hint card (white pill, left blue border, Space Mono text) at canvas bottom-left.
Numeric overlays on canvas show `rotX` and `rotY` current values.

## Animation aesthetic
3D mesh rendered with Painter's Algorithm (sort faces by z-depth, draw back-to-front).
Face colors: teal-to-sky-blue gradient by `u` parameter. Diffuse shading simulates light source.
Smooth response to drag input; no easing — rotation follows mouse directly.

## Key CSS patterns
```css
body { background: #f1f5f9; color: #334155; }
.card { background: rgba(255,255,255,0.7); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,1); border-top: 4px solid #0284c7;
  box-shadow: 0 20px 40px rgba(14,165,233,0.1); }
.main-title { color: #0284c7; border-bottom: 4px double #0284c7; }
.math-box { color: #0369a1; background: rgba(56,189,248,0.1); border-left: 4px solid #0284c7; }
.canvas-wrapper { background: radial-gradient(circle at 50% 50%, #f8fafc 0%, #e2e8f0 100%);
  cursor: grab; border: 1px solid #cbd5e1;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.05); }
.drag-prompt { background: rgba(255,255,255,0.9); border-left: 3px solid #0284c7;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
```

## When to use
Geometry, topology, or any subject where the concept is physically "in space."
The light/glassmorphic aesthetic feels clean and modern without distracting from the 3D object.
Avoids the "dark lab" cliché when the topic is more about elegance than precision instruments.
Best for Spatial Navigation interactions.
