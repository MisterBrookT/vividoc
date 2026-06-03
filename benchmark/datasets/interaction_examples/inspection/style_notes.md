# Style: Mystic Observatory

## Color palette
- Background: `#170a24` (deep purple-black)
- Card/surface: `#28143d`
- Inner widget: `#13081e` (darkest layer)
- Canvas: `#0c0512`
- Primary accent: `#facc15` (gold/yellow) — titles, highlights, hovering elements
- Secondary: `#d8b4fe`, `#e9d5ff` (lavender body text tones)
- Border: `#7e22ce` (bright purple), `#9333ea`
- Text: `#dac6e3` (dusty lavender)
- Strong text: `#facc15` + Space Mono

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, letter-spacing: 2px
- Body: Merriweather, 300 weight (matches scientific series)
- Values/code: Space Mono monospace
- Math box: left border `4px solid #facc15`, gold text, dark purple tint background

## Layout
- Single centered column, max-width 850px
- Three-layer depth: body → card → widget → canvas (each darker than the previous)
- `box-shadow: inset 0 0 50px rgba(0,0,0,0.8)` creates depth in widget

## Controls signature
No explicit controls — interaction is pure hover/mouse-move.
`cursor: crosshair` on canvas. A bottom-left `drag-prompt` tag with dashed lavender border
signals hover interaction. Canvas responds to `mousemove` events in real-time.

## Animation aesthetic
Drifting particles with slow random velocities. On hover: radial gradient flood-fill
reveals the Voronoi cell. Connecting line from cursor to nearest seed. Everything animates
at 60fps via requestAnimationFrame; canvas clears each frame (`clearRect`).

## Key CSS patterns
```css
body { background: #170a24; color: #dac6e3; }
.card { background: #28143d; border: 1px solid #7e22ce; border-top: 4px solid #facc15; }
.main-title { color: #facc15; border-bottom: 4px double #facc15; }
.section-title { color: #fdf4ff; }
.text-box { color: #e9d5ff; }
.math-box { color: #facc15; background: rgba(250,204,21,0.05); border-left: 4px solid #facc15; }
.strong-text { color: #facc15; font-family: 'Space Mono'; }
.widget { background: #13081e; border: 1px solid #7e22ce; box-shadow: inset 0 0 50px rgba(0,0,0,0.8); }
.canvas-wrapper { background: #0c0512; border: 1px solid #9333ea; cursor: crosshair; }
.drag-prompt { color: #facc15; border: 1px dashed #d8b4fe; background: rgba(60,20,90,0.8); }
```

## When to use
Math/CS topics with a sense of wonder or mystery: topology, spatial algorithms, set theory,
probability. The deep purple + gold palette evokes "seeing the hidden structure of space."
Best for Inspection interactions where hovering reveals something that was already there.
