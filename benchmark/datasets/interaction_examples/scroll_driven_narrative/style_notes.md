# Style: Stark Monochrome

## Color palette
- Background: `#09090b` (near-pure black, zinc-950)
- Card/surface: `#18181b` (zinc-900)
- Text: `#f4f4f5` (zinc-100, headings), `#a1a1aa` (body), `#d4d4d8` (section body)
- Borders: `#3f3f46` (zinc-700), `#27272a` (zinc-800)
- **Only color accent**: `#ef4444` (red) — entropy value, math box border, scroll fill bar
- Card left-border accent: `border-left: 6px solid #f4f4f5` (white, not color)
- Math background: `#000` (pure black) — maximum contrast

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, letter-spacing: 2px (no color accent)
- Body: Merriweather, 300 weight
- Entropy readout: Space Mono, 1.4rem, `#ef4444` — the only colored text in the whole piece

## Layout
- Single centered column, max-width 850px
- Widget is a flex row: scroll-track sidebar (50px) + canvas area
- `scroll-track`: full-height red fill bar that rises as user scrolls — like a progress indicator
- Card uses `border-left: 6px solid #f4f4f5` (vertical accent rule) instead of top border

## Controls signature
No traditional controls. Interaction is `wheel` event on canvas.
A bottom-right `drag-prompt` ("SCROLL TO REMOVE WALL") with plain monospace styling.
Red fill bar on left edge of widget as the only visual feedback of scroll progress.

## Animation aesthetic
60fps particle simulation. Particles are colored red/blue and bounce off walls.
The partition wall shortens from the top as scroll_progress increases.
Entropy counter updates live. No easing — particles are purely physics-driven.
Color contrast between red/blue particles against black background is stark and clear.

## Key CSS patterns
```css
body { background: #09090b; color: #a1a1aa; }
.card { background: #18181b; border: 1px solid #3f3f46; border-left: 6px solid #f4f4f5; }
.main-title { color: #f4f4f5; border-bottom: 4px solid #3f3f46; }  /* no color accent */
.math-box { background: #000; color: #f4f4f5; border-left: 4px solid #ef4444; }
.widget { display: flex; padding: 0; }  /* no padding — content fills edge-to-edge */
.scroll-track { width: 50px; background: #000; border-right: 1px solid #27272a; }
.scroll-fill { background: #ef4444; }  /* rises with scroll progress */
.entropy-disp { color: #ef4444; font-family: 'Space Mono'; font-size: 1.4rem; font-weight: bold; }
.drag-prompt { color: #f4f4f5; border: 1px solid #3f3f46; background: rgba(0,0,0,0.8); }
```

## When to use
Topics in thermodynamics, statistical mechanics, information theory, or any concept where
**irreversibility** and **time's arrow** are the point. The minimal color use means
the red accent on the entropy counter carries maximum visual weight — it IS the concept.
Best for Scroll-driven Narrative interactions where scroll = time.

## Design rationale
Entropy and the Second Law of Thermodynamics is about *irreversibility* — the arrow of time.
The visual design must feel like the concept: stark, inevitable, no-nonsense.

Near-pure black zinc palette with a single red accent → the red entropy counter is the ONLY
thing with color in the entire piece. When something is the only colored element, it has
maximum visual weight. The learner's eye goes directly to it. The scroll interaction maps
exactly to time's arrow (you can scroll forward but the concept is about irreversibility).
The minimal design says: "this is serious; pay attention to what's happening."
