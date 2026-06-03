# Style: Synthwave / Retro Arcade

## Color palette
- Background: `#2a1b38` (deep purple)
- Card/surface: `#3b284d`
- Inner widget: `#231630`
- Canvas: `#1a1024` with grid overlay `rgba(192,132,252,0.1)`
- Primary accent: `#f472b6` (hot pink / magenta) — title, play button, thumb glow
- Secondary: `#c084fc` (soft purple) — math, slider labels
- Text: `#fdf2f8` (near white with pink tint), `#e2e8f0` (body), `#cbd5e1`
- Border: `#5b3e75`, `#704b90`
- Button glow: `box-shadow: 0 0 10px rgba(219,39,119,0.5)`
- Slider thumb glow: `box-shadow: 0 0 10px #f472b6`

## Typography
- Headings: Roboto Slab, 800 weight, uppercase, `text-shadow: 2px 2px 10px rgba(244,114,182,0.3)` — neon glow
- Body: Merriweather, 300 weight
- Buttons/controls: **VT323** (retro/arcade bitmap font), 1.3rem, uppercase
- Values: VT323 for playback display

## Layout
- Single centered column, max-width 850px
- Canvas has a `background-image` grid pattern — 20px grid with purple tint, like graph paper
- Controls bar: flex row, `rgba(112,75,144,0.1)` tinted background
- Play button is tall and centered with neon border glow

## Controls signature
Play/Pause button: VT323 font, hot pink fill, glowing border.
Slider with custom thumb: `background: #f472b6; box-shadow: 0 0 10px #f472b6` — neon indicator.
Slider track: dark purple with purple border.

## Animation aesthetic
requestAnimationFrame loop for epicycle animation. Each circle drawn with strokeStyle colors
cycling through spectrum. Wave output recorded to array, drawn as polyline on right side.
Dashed connecting line from epicycle tip to wave. All motion is continuous and smooth.

## Key CSS patterns
```css
body { background: #2a1b38; color: #fdf2f8; }
.card { background: #3b284d; border: 1px solid #5b3e75; border-top: 4px solid #f472b6; }
.main-title { color: #f472b6; border-bottom: 4px double #f472b6;
  text-shadow: 2px 2px 10px rgba(244,114,182,0.3); }
.canvas-wrapper {
  background: #1a1024;
  background-image: linear-gradient(rgba(192,132,252,0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(192,132,252,0.1) 1px, transparent 1px);
  background-size: 20px 20px; }
button { font-family: 'VT323', monospace; font-size: 1.3rem;
  background: #db2777; border: 2px solid #f472b6;
  box-shadow: 0 0 10px rgba(219,39,119,0.5); }
input[type="range"]::-webkit-slider-thumb { background: #f472b6; box-shadow: 0 0 10px #f472b6; }
```

## When to use
Topics in signal processing, wave physics, time-series analysis, music theory, or anything
where the "flow of time" is core to understanding. The synthwave aesthetic makes mathematics
feel exciting and aesthetic rather than dry. Best for Temporal Control interactions with
real-time animation.
