# Style: Dark Scientific

## Color palette
- Background: `#0b0f19` (deep navy-black)
- Card/surface: `#161e2e`
- Border/divider: `#334155`
- Primary accent: `#22d3ee` (cyan)
- Secondary accent: `#7dd3fc` (sky blue)
- Text: `#cbd5e1` (slate-200)
- Math/code highlight: `#38bdf8`

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, letter-spacing: 2px
- Body: Merriweather, 300 weight, serif, 1.1rem / 1.7 line-height
- Code/values: Space Mono, monospace

## Layout
- Single centered column, max-width 850px
- Content inside a card with `border-top: 4px solid accent`
- Section title uses uppercase + letter-spacing for editorial feel

## Animation aesthetic
- Canvas drawing: trail fades with alpha compositing (`rgba(bg, 0.05)` each frame)
- No CSS transitions — all animation is canvas-driven

## Key CSS patterns
```css
body { background: #0b0f19; color: #cbd5e1; }
.card { background: #161e2e; border-top: 4px solid #22d3ee; border-radius: 8px; }
.section-title { text-transform: uppercase; letter-spacing: 1px; color: #f8fafc; }
input[type="range"] { background: #0f172a; border: 1px solid #38bdf8; }
input[type="range"]::-webkit-slider-thumb { background: #22d3ee; box-shadow: 0 0 10px #22d3ee; }
.math-box { color: #38bdf8; background: rgba(56,189,248,0.05); font-family: 'Space Mono'; }
```

## When to use
Scientific / mathematical topics where precision and "lab instrument" aesthetic fits.
Works especially well for physics, signal processing, dynamical systems.

## Design rationale
The Lorenz Attractor is a *physics simulation* — the mental model is "watching a system evolve
on an instrument." Dark backgrounds + monochrome + cyan single accent → oscilloscope / physics
terminal. Space Mono everywhere signals "this is numerical output." The trail-fading animation
technique is borrowed from real particle physics visualization software.

Chaos theory has no "warm" emotional tone — it's precise, cold, and slightly unsettling.
The darkness is appropriate.
