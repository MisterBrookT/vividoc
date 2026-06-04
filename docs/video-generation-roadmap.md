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

## References

- **Code2Video** — Chen et al., ICML 2026. [arXiv:2510.01174](https://arxiv.org/abs/2510.01174) · [GitHub](https://github.com/showlab/Code2Video)
- **LASEV** — "Beyond End-to-End Video Models: An LLM-Based Multi-Agent System for Educational Video Generation." [arXiv:2602.11790](https://arxiv.org/html/2602.11790v1)
- **ManimBench** — First benchmarking dataset for Manim code generation, 417 paired samples.
- **LLM Approaches to Educational Video Generation Using Manim** — Springer 2025. [link](https://link.springer.com/chapter/10.1007/978-3-032-07938-1_26)
- **manim-video-gen** — Open-source prototype: [GitHub](https://github.com/KrishKrosh/manim-video-gen)
