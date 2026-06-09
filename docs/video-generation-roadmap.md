# ViviDoc Video Generation Roadmap

> **Status**: Planning / Pre-implementation  
> **Related work**: Code2Video (ICML 2026), LASEV, ManimBench  
> **Proposed next milestone**: ViviDoc-Video v0.1

---

## Motivation

ViviDoc currently produces **self-contained interactive HTML documents** — explorable explanations
that readers manipulate in a browser. The natural next medium is **educational video**: a narrated,
animated walkthrough of the same concept, suitable for YouTube, lecture slides, or asynchronous
courses. Video trades interactivity for accessibility — no browser required, shareable anywhere,
consumable passively.

The two formats are complementary. An interactive document lets a learner explore at their own pace;
a video provides a curated narrative arc. ViviDoc is uniquely positioned to generate both from a
single DocSpec, since the SRTC spec already describes the concept's structure, visual elements,
and key transitions — the same information a video storyboard needs.

---

## Landscape Survey (June 2026)

### Code2Video · ICML 2026
**Paper**: [arXiv:2510.01174](https://arxiv.org/abs/2510.01174)  
**Venue**: DL4C @ NeurIPS 2025 → ICML 2026  
**Approach**: Code-centric tri-agent pipeline — Planner (storyboard), Coder (Manim synthesis), Critic (layout refinement with spatial anchors). Generates Manim Python code instead of pixels; videos are rendered deterministically.  
**Benchmark**: MMMC — 117 topics inspired by 3Blue1Brown (calculus, geometry, probability, neural nets).  
**Results**: 40% improvement over direct code generation; quality comparable to human-crafted tutorials.  
**Key limitation**: Manim-only output; no audio narration; no interactivity; long-form videos (>3 min) remain hard; common syntax errors in generated Manim code.

### LASEV (LLM-based Multi-Agent System for Educational Video)
**Paper**: [arXiv:2602.11790](https://arxiv.org/html/2602.11790v1)  
**Approach**: End-to-end system for high-fidelity instructional video. Uses a multi-agent pipeline for storyboarding, scene generation, narration synthesis, and video assembly.  
**Limitation**: Less focused on mathematical rigor; aimed at broader educational content.

### Manim + LLM (general direction)
Multiple groups (including [KrishKrosh/manim-video-gen](https://github.com/KrishKrosh/manim-video-gen),
[Bleu AI](https://docs.buildbleu.com/blog/using-llms-to-generate-educational-videos-with-manim/))
have prototyped 3Blue1Brown-style video generation from text prompts using LLMs to write Manim code.  
**Common issues**: Syntax errors, layout conflicts, poor spatial reasoning in generated code. ManimBench (417 paired samples) was created to benchmark this.

### What's missing across all existing work

| Gap | Notes |
|-----|-------|
| **No interactive ↔ video duality** | No system generates both interactive HTML and video from the same spec |
| **No SRTC-aware storyboarding** | Existing storyboards ignore interaction taxonomy; transitions are flat |
| **No narration synthesis tied to visual state** | Audio is generated independently from the animation |
| **No benchmark with paired HTML + video** | Evaluation is video-only; no cross-modal quality assessment |

---

## ViviDoc-Video: Proposed Approach

### Core Idea

Reuse the existing **DocSpec / SRTC spec** as the storyboard skeleton. Each `KnowledgeUnit` maps
to one video scene. The SRTC fields translate naturally:

| SRTC field | Video storyboard mapping |
|-----------|--------------------------|
| `S` (State) | Scene parameters / variable values to demonstrate |
| `R` (Render) | Visual elements to animate |
| `T` (Transition) | Keyframe sequence — what changes, when, in what order |
| `C` (Constraint) | Pedagogical highlight — what the narrator calls out |

This gives ViviDoc-Video a structural advantage over Code2Video's flat storyboard: the SRTC
constraint forces every scene to have a **pedagogical invariant**, not just a visual description.

### Proposed Pipeline

```
DocSpec (SRTC)
    │
    ▼
┌──────────────────┐
│  Scene Planner   │  Expands each KnowledgeUnit into a scene timeline:
│                  │  t=0s: show state variables, t=3s: animate transition,
│  (LLM)          │  t=6s: highlight constraint, t=8s: summary
└────────┬─────────┘
         │ Scene timeline (JSON)
         ▼
┌──────────────────┐
│  Manim Coder     │  Generates Manim Python for each scene.
│                  │  Grounded in SRTC R-field (render elements already
│  (LLM + tools)  │  specified as Canvas drawing operations in HTML).
└────────┬─────────┘
         │ Manim .py files
         ▼
┌──────────────────┐
│  Narration Sync  │  Generates voiceover script synchronized to keyframes.
│                  │  Uses TTS (e.g., ElevenLabs, Coqui) or LLM-synthesized
│  (LLM + TTS)    │  narration cues.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Video Renderer  │  Renders Manim to MP4, adds narration track,
│  + Assembler     │  optionally overlays KaTeX equations.
└────────┬─────────┘
         │
         ▼
    document.mp4  (alongside document.html)
```

### Direction 1: Manim-Based (Code2Video-style)

Generate Manim Python code from SRTC. Advantages:
- Deterministic, reproducible
- Vector-quality output, arbitrarily zoomable
- Mathematical typesetting via LaTeX (native in Manim)
- Code is debuggable and editable

Challenges:
- Manim API is large and error-prone for LLMs
- Spatial layout is hard to specify in natural language
- Slow render times (minutes per scene)

**Mitigation**: Use ViviDoc's existing Canvas JS logic as a "rendered spec" — translate Canvas
drawing calls to Manim equivalents via LLM. The HTML document already provides a working
visual specification.

### Direction 2: HTML-to-Video (Record-Then-Narrate)

Record the interactive HTML document using a headless browser (Playwright), scripting the
interactions via the SRTC Transition spec. Add narration in post.

Advantages:
- Zero new rendering stack — uses the existing HTML/Canvas output
- Pixel-perfect match between interactive and video versions
- Fast iteration

Challenges:
- Resolution limited by browser viewport
- No vector output
- Canvas animations may have timing jitter

**Implementation**: Playwright headless Chrome → `page.evaluate()` to drive state changes
per SRTC T-field events → `ffmpeg` to assemble frame sequence → TTS narration overlay.

### Direction 3: Hybrid (Recommended for v0.1)

Start with Direction 2 (HTML recording) for fast prototyping and a working demo.
Layer on Direction 1 (Manim) for sections with complex mathematical animations.

---

## Benchmark Proposal: ViviBench-Video

Extend ViviBench (101 topics) with paired video targets:
- **Source**: The 8 gold HTML examples in `benchmark/datasets/interaction_examples/`
- **Ground truth**: Human-curated narrated walkthroughs for each
- **Metrics**:
  - Concept accuracy (LLM-as-judge against gold explanation)
  - Visual coherence (do animations match the narration?)
  - Pedagogical completeness (are all SRTC constraints covered?)
  - Synchronization quality (narration timing vs visual events)

---

## Implementation Plan

### Phase 0 (now): Foundations
- [x] DocSpec includes SRTC T-field (transition keyframe structure)
- [x] 16 gold HTML documents in `frontend/public/cases/`
- [ ] Add `timeline` field to KnowledgeUnit: ordered list of `{t: seconds, event: string, state_delta: dict}`

### Phase 1 (v0.1): HTML Recording Pipeline
- [ ] `vividoc record <doc.html> --out video.mp4` CLI command
- [ ] Playwright script that drives SRTC T-field events on schedule
- [ ] Basic TTS narration from text_description field
- [ ] ffmpeg assembly

### Phase 2 (v0.2): Manim Code Generation
- [ ] `SceneCodegen` agent: SRTC → Manim Python
- [ ] Use existing Canvas JS as visual spec (translate draw calls)
- [ ] ManimBench-style evaluation
- [ ] Scene-level critic for layout validation

### Phase 3 (v1.0): Unified Pipeline
- [ ] Single `vividoc run <topic> --output html,video` command
- [ ] Narration synchronized to SRTC T-field keyframes
- [ ] ViviBench-Video evaluation
- [ ] Comparison against Code2Video on MMMC topics

---

---

## Design Notes: Quality, Tools, and the Creator Problem

### The 3B1B Quality Gap

The gap between a generated Manim video and a 3Blue1Brown video is not about the framework — 3B1B uses Manim too. It operates at three distinct layers:

**Layer 1 — Script / Pedagogy (hardest to fix)**
3B1B's scripts are built around a single "aha moment" per video. Every sentence exists to build one specific geometric intuition before the abstract formula appears. Generated scripts tend to follow a textbook path: state the formula, show a graph, list properties. This is the inverse of how understanding actually forms. A better prompt frame: "Design the moment at second N when the learner will understand X. What do they need to have seen in the N−1 seconds before that?" This is a planning problem, not a rendering problem.

**Layer 2 — Audio (easiest quick win)**
Silent math animations feel cold and hard to follow. 3B1B's warmly-paced narration does half the pedagogical work. Integrating TTS (OpenAI TTS, ElevenLabs) synchronized to Manim keyframes is the highest-ROI improvement available today. Even mediocre narration beats silence.

**Layer 3 — Timing and choreography**
3B1B controls exactly when each element appears, how long pauses are, and what gets highlighted. The rhythm creates suspense and resolution. Generated animations tend to play sequentially without dramatic timing — they feel like slideshow transitions rather than a narrative unfolding. This is fixable with a "scene critic" pass that adjusts durations and stagger timings based on pedagogical role.

**Summary**: quality is 60% script, 30% audio, 10% visual polish. Most existing work optimizes the 10%.

---

### Manim vs Remotion: Tool Choice Framework

Both are "video from code" tools, but they have fundamentally different mental models.

**Manim** thinks in *mathematical objects and transformations*. Every element is an MObject with a coordinate-space position. LaTeX is native. Elements can morphically transform into each other (e.g., an equation becomes a geometric shape). Rendering is offline, frame-by-frame via Cairo. Designed for precision — if you need to show that two angles are equal, Manim lets you state that mathematically.

**Remotion** thinks in *React components over time*. A Remotion video is a component tree rendered at each timestamp; frame N is just the React DOM at `currentFrame === N`. This means anything the browser can render — CSS, WebGL, Three.js, D3, any npm package — is available. Remotion Cloud is specifically designed for personalized batch rendering (each viewer gets a different video).

| Dimension | Manim | Remotion |
|---|---|---|
| Paradigm | Math objects + transforms | React components + time |
| Best for | Equations, geometric proofs, scientific simulations | Data viz, product demos, personalized videos |
| Audio sync | Manual and painful | Native (useCurrentFrame = frame-accurate) |
| Batch/personalized rendering | Not designed for it | First-class (Remotion Cloud) |
| Math typesetting | LaTeX native | KaTeX possible but not native |
| Object morphing | Excellent | Hard |
| Web ecosystem | No | Full access |
| LLM code generation quality | Poor (Manim API is large and error-prone) | Better (React patterns are LLM-familiar) |

**For ViviDoc specifically:**
- Manim → deep mathematical education content (the 3B1B direction)
- Remotion → ViviDoc Learn email videos (personalized per learner, batch rendered)

---

### The Talking Head + Product Demo Problem

A recurring need for independent creators: combining a product screen recording (or Manim animation) with a talking-head webcam feed to build audience trust. This is a genuinely hard composition problem. The state of the art as of mid-2026:

**What exists:**
- **Descript** / **CapCut** — timeline editors with AI-assist (auto-cut silence, filler words, basic green screen). Good for manual editing; poor for programmatic generation.
- **HeyGen / Synthesia** — AI avatars that lip-sync to a script. Removes the need to record at all, but avatars still feel uncanny and lose the authenticity benefit of showing your real face.
- **Runway / Pika** — generative video for B-roll and transitions, not for compositing a real person with a product demo.
- **Loom / Mmhmm** — webcam overlay on screen recording, good UX but purely manual.

**What's missing:**
No tool does all of: (1) programmatically compose talking head + product demo, (2) auto-align the speaker's gestures/gaze to the on-screen content, (3) produce broadcast-quality output without manual timeline editing. The closest workflow today is: record talking head separately → record screen separately → stitch manually in DaVinci Resolve or Descript → narration timing done by hand.

**The AI opportunity**: An agent that takes (a) a product demo script, (b) a screen recording or Remotion-generated animation, (c) a webcam recording, and outputs a composed video where gaze direction, pointing gestures, and cut timing are auto-aligned to the script. This doesn't exist as a coherent product yet (June 2026). The nearest research is in talking-head video generation and gaze redirection, but they operate on generated avatars, not real footage.

**Interim recommendation for independent creators**: Record webcam + screen simultaneously with OBS (Picture-in-Picture), keep it rough and honest — audiences trust rough-around-the-edges real footage more than polished AI avatars. Spend time on the script, not the production.

---

### AI-Assisted Video Quality Iteration

The core loop for improving generated video quality with AI:

1. **Generate** a rough Manim or Remotion video from the SRTC spec
2. **Evaluate** it with an LLM-as-judge against the pedagogical criteria (does the aha moment land? is the constraint visible? is the pacing right?)
3. **Critique** specific keyframes: "At second 12, the viewer doesn't yet understand why the boundary condition matters — add a visual cue"
4. **Revise** the animation code based on the critique
5. **Repeat** until the critic is satisfied

The missing piece is a **visual understanding loop**: the critic needs to *watch* the video, not just read the code. This is now feasible with multimodal LLMs (pass video frames to the model). A tight human-AI collaboration loop — human watches and gives one-sentence feedback, AI revises code — is already achievable and is likely the right model before fully automated critique works reliably.

**Taste as infrastructure**: The real bottleneck is taste — the ability to recognize that a 0.3s pause before revealing the key equation is the difference between "oh I see it" and "wait, what just happened." This is hard to encode in a rubric. The practical path is: build a growing library of examples that the creator marks as "good" or "not quite," and use those as few-shot examples in the critic prompt.

---

## References

- **Code2Video** — Chen et al., ICML 2026. [arXiv:2510.01174](https://arxiv.org/abs/2510.01174) · [GitHub](https://github.com/showlab/Code2Video)
- **LASEV** — "Beyond End-to-End Video Models: An LLM-Based Multi-Agent System for Educational Video Generation." [arXiv:2602.11790](https://arxiv.org/html/2602.11790v1)
- **ManimBench** — First benchmarking dataset for Manim code generation, 417 paired samples.
- **LLM Approaches to Educational Video Generation Using Manim** — Springer 2025. [link](https://link.springer.com/chapter/10.1007/978-3-032-07938-1_26)
- **manim-video-gen** — Open-source prototype: [GitHub](https://github.com/KrishKrosh/manim-video-gen)
