# Style: Dark Laboratory

## Color palette
- Background: `#020617` (near-black, deeper than pure black)
- Card/surface: `#0f172a`
- Primary accent: `#10b981` (emerald green) — all interactive elements, titles
- Text: `#94a3b8` (slate body), `#cbd5e1` (section body), `#f8fafc` (headings)
- Border: `#1e293b`
- Dashboard values: `#10b981` on `#020617` — instrument readout style
- Grid overlay: `rgba(16,185,129,0.05)` — subtle green grid on canvas

## Typography
- Headings: Roboto Slab, 800 weight, uppercase
- Body: Merriweather, 300 weight
- Readouts/values: Space Mono (critical for instrument aesthetic)
- Labels: Inter, uppercase, letter-spacing

## Layout
- Single centered column, max-width 900px
- Dashboard strip above canvas: flex row, each metric in its own cell with label + large value
- Canvas has `cursor: crosshair` — signals it's a draggable space
- `drag-prompt` tag (dashed border) at bottom-left corner of canvas as affordance hint

## Controls signature
No traditional sliders. Interaction is entirely through direct canvas manipulation.
A `tag-item` component shows real/virtual image type with colored badge.
Dashboard readout uses `dash-item` with uppercase label and large `Space Mono` value.

## Animation aesthetic
Canvas redraws on every `mousemove` event during drag. Physics-based optical calculations
update all derived values in real-time. Lines and arrows drawn with strokeStyle colors:
orange for object, green for real image, blue for virtual, gray for rays.

## Key CSS patterns
```css
body { background: #020617; color: #94a3b8; }
.card { background: #0f172a; border-top: 4px solid #10b981; }
.main-title { color: #10b981; border-bottom: 4px double #10b981; }
.canvas-wrapper { background: #020617;
  background-image: linear-gradient(rgba(16,185,129,0.05) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(16,185,129,0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  border: 1px solid #10b981; cursor: crosshair; }
.dashboard { background: #020617; border: 1px solid #1e293b; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }
.dash-item .val { color: #10b981; font-family: 'Space Mono', monospace; font-size: 1.5rem; }
.tag-item { background: #10b981; color: #020617; font-weight: 900; }
.drag-prompt { color: #10b981; border: 1px dashed #10b981; font-family: 'Space Mono'; text-transform: uppercase; }
```

## When to use
Science topics where the "precision instrument / lab bench" aesthetic fits: optics, physics,
engineering. The emerald-on-black palette evokes oscilloscope screens and scientific equipment.
Best for Direct Manipulation interactions where readouts update in real-time.
