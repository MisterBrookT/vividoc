# Style: Academic Antiquarian

## Color palette
- Background: `#fdfbf7` (warm ivory)
- Card/surface: `#f5f0e6` (cream)
- Primary: `#1e3a8a` (navy blue) — structure, math, borders
- Accent: `#991b1b` (deep red) — titles, emphasis, active state
- Text: `#475569` (slate body), `#1e293b` (headings)
- Math background: `rgba(30,58,138,0.05)` with left `4px solid #1e3a8a`

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, letter-spacing: 2px
- Body: Merriweather, 300 weight, serif, 1.1rem / 1.7 line-height
- Code/values: Space Mono, monospace
- Buttons/controls: Space Mono, uppercase

## Layout
- Single centered column, max-width 850px
- Card with cream background, navy blue border, deep red top accent bar
- `border-bottom: 4px double` on title — double-rule editorial feel

## Controls signature
Segmented buttons with `Space Mono` font, navy border, transparent background when inactive,
solid navy fill when active. Minimal, no border-radius (2px).

## Animation aesthetic
Progressive particle accumulation (Monte Carlo sampling) — dots appear one by one, building up
the density cloud. No CSS animations; all canvas-driven.

## Key CSS patterns
```css
body { background: #fdfbf7; color: #1e293b; font-family: 'Merriweather', serif; }
.card { background: #f5f0e6; border: 1px solid #1e3a8a; border-top: 4px solid #991b1b; }
.main-title { color: #1e3a8a; border-bottom: 4px double #1e3a8a; text-transform: uppercase; letter-spacing: 2px; }
.section-title { color: #991b1b; text-transform: uppercase; letter-spacing: 1px; }
.math-box { color: #1e3a8a; background: rgba(30,58,138,0.05); border-left: 4px solid #1e3a8a; }
.segment { border: 1px solid #1e3a8a; border-radius: 2px; color: #1e3a8a; background: transparent; }
.segment.active { background: #1e3a8a; color: #fdfbf7; }
.canvas-wrapper { border: 1px dashed #1e3a8a; background: radial-gradient(circle at center, rgba(30,58,138,0.05) 0%, transparent 70%); }
```

## When to use
Topics in physics, quantum mechanics, formal mathematics, or any subject that benefits from an
"old textbook" authority feel. The cream-and-navy palette conveys scholarship and precision.
Works well for State Switching interactions where discrete configurations need clear visual distinction.

## Design rationale
Quantum mechanics is an *academic subject* — the learner is reading about something with centuries
of scientific history. Ivory/cream background + navy blue + serif fonts → old physics textbook,
academic journal. The double-rule title border is an editorial convention from classic print.

The deep red accent for section titles adds warmth and distinction from pure navy. The warm paper
background signals "this is a formal document worth reading carefully, not a game."
