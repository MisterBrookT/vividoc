# Style: Neo-Brutalist

## Color palette
- Background: `#fdf07e` (loud yellow — the defining feature)
- Card: white (`#fff`) with `4px solid #000` border + `12px 12px 0 #000` offset shadow
- Text: pure `#000`
- Success/active: `#4ade80` (lime green) — used for highlights, active buttons, fill bars
- Danger/clear: `#f87171` (coral red) — used for clear/reset actions
- Math/code background: `#000` with `#fff` text (inverted block)
- Canvas dot grid: `background-image: radial-gradient(#000 1.5px, transparent 1.5px)` on `#f5f5f0`

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, 2px letter-spacing
- Body: Merriweather, 300 weight
- Controls/buttons: Space Mono, bold, uppercase — this is critical to the aesthetic

## Layout
- Single centered column, max-width 880px
- No border-radius (or 0px) on cards — hard corners reinforce brutalism
- Widget has same black border + offset shadow as card: `box-shadow: 6px 6px 0 #000`
- Buttons: `box-shadow: 4px 4px 0 #666`, shift on `:active` with `transform: translate(3px,3px)`
- Output bar is a hand-drawn-style progress indicator

## Controls signature
Large black buttons with colored fill (lime/red), `Space Mono` font, bold uppercase text.
Button press has a tactile translate + shadow collapse animation. Canvas is `cursor: crosshair`.

## Animation aesthetic
Nodes placed on click. Animated forward pass with colored connection pulses (green then orange).
Snappy, no easing — everything feels mechanical and direct.

## Key CSS patterns
```css
body { background: #fdf07e; color: #000; }
.card { background: #fff; border: 4px solid #000; box-shadow: 12px 12px 0 #000; }
.main-title { border-bottom: 6px solid #000; }
.math-box { background: #000; color: #fff; font-family: 'Space Mono'; }
.canvas-wrapper { border: 4px solid #000; cursor: crosshair;
  background-image: radial-gradient(#000 1.5px, transparent 1.5px);
  background-size: 20px 20px; }
button { font-family: 'Space Mono'; background: #000; color: #fdf07e;
  border: 3px solid #000; box-shadow: 4px 4px 0 #666; text-transform: uppercase; }
button:active { transform: translate(3px, 3px); box-shadow: 1px 1px 0 #666; }
#btn-pulse { background: #4ade80; color: #000; }
.strong-text { background: #4ade80; padding: 0 5px; }
```

## When to use
CS / engineering / technology topics where bold, assertive design signals agency and construction.
The yellow + black palette is energetic and confident. Works especially well for
Freeform Construction interactions where the user is building something. Polarizing but memorable.

## Design rationale
Neural networks are about *construction* — you build something and watch it come alive.
The loud yellow background is energetic and assertive, like a warning sign or a sticky note.
This is not a passive observation exercise; the user is actively creating.

Neo-brutalism's thick black borders and offset shadows signal "this is made of parts,"
which metaphorically fits a network of nodes. The lime green "pulse" button vs. red "clear"
button uses traffic light logic — go vs. reset. The polka-dot canvas grid evokes graph paper,
which is where engineers sketch circuits and networks. The aesthetic is confident, even aggressive.
