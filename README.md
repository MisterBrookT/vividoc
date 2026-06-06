<div align="center">

<h1>ViviDoc</h1>
<p><strong>Turn any topic into an explorable explanation.</strong></p>

[![arXiv](https://img.shields.io/badge/arXiv-2603.27991-b31b1b.svg?style=flat-square)](https://arxiv.org/abs/2603.27991)
[![ACL 2026](https://img.shields.io/badge/ACL_2026-System_Demo-4b8bff?style=flat-square&logo=semantic-scholar)](https://arxiv.org/abs/2603.01912)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Demo](https://img.shields.io/badge/Demo-vividoc.vercel.app-000000?style=flat-square&logo=vercel)](https://vividoc.vercel.app)

**[Live Demo](https://vividoc.vercel.app)** · **[Paper](https://arxiv.org/abs/2603.27991)** · **[Demo Paper](https://arxiv.org/abs/2603.01912)** · **[PDF](assets/paper.pdf)**

<br/>

<img src="assets/demo-screenshot.png" alt="ViviDoc showcase — 8 interactive documents across 4 domains" width="100%"/>

</div>

---

ViviDoc generates **self-contained interactive HTML documents** from a single topic input. It designs a purpose-built visual style, structures the document using the **SRTC Interaction Spec** (State · Render · Transition · Constraint), and writes a single `.html` file with KaTeX math and Canvas visualizations — no build step, no server. Your AI coding agent (Claude Code, Codex, etc.) is the harness — no external API key required.

> **Accepted at ACL 2026 System Demonstrations** — [arXiv:2603.01912](https://arxiv.org/abs/2603.01912)

---

## 🚀 Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/MisterBrookT/vividoc/main/install.sh | bash
```

Installs `/vividoc`, `/vividoc-learn`, and `/vividoc-slides` into `~/.claude/commands/`. Your harness is the model — no separate API key needed.

```
/vividoc Fourier Transform
```

```
/vividoc-learn https://ncase.me/trust/
```

```
/vividoc-slides https://example.edu/lecture.pdf
```

---

## 📚 Showcase

**[→ vividoc.vercel.app](https://vividoc.vercel.app)**

| Document | Domain | Interaction |
|---|---|---|
| [Fourier Transform](https://vividoc.vercel.app) | Physics & Math | Temporal Control |
| [Lorenz Attractor](https://vividoc.vercel.app) | Physics & Math | Parameter Exploration |
| [Action Potential](https://vividoc.vercel.app) | Biology | Temporal Control |
| [DNA Replication](https://vividoc.vercel.app) | Biology | Temporal Control |
| [Gradient Descent](https://vividoc.vercel.app) | Machine Learning | Direct Manipulation |
| [Bias–Variance Tradeoff](https://vividoc.vercel.app) | Machine Learning | Parameter Exploration |
| [Shannon Entropy](https://vividoc.vercel.app) | Information Theory | Parameter Exploration |
| [Huffman Coding](https://vividoc.vercel.app) | Information Theory | Freeform Construction |

---

## 🔬 Development

```bash
uv sync --dev
uv run pytest
cd frontend && npm install && npm run dev
```

Baselines (AutoGen, CAMEL, MetaGPT, naive): `uv run python benchmark/run.py --baseline autogen`

---

## 📄 Citation

```bibtex
@article{tang2026vividoc,
  title   = {{ViviDoc}: Generating Interactive Documents through Human-Agent Collaboration},
  author  = {Tang, Yinghao and Xie, Yupeng and Feng, Yingchaojie and
             Lan, Tingfeng and Lao, Jiale and Cheng, Yue and Chen, Wei},
  journal = {arXiv preprint arXiv:2603.27991},
  year    = {2026},
  url     = {https://arxiv.org/abs/2603.27991}
}

@inproceedings{tang2026demonstrating,
  title     = {Demonstrating {ViviDoc}: Generating Interactive Documents through Human-Agent Collaboration},
  author    = {Tang, Yinghao and Xie, Yupeng and Feng, Yingchaojie and Lan, Tingfeng and Chen, Wei},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics: System Demonstrations},
  year      = {2026},
  url       = {https://arxiv.org/abs/2603.01912}
}
```

---

<div align="center">

MIT License · [ACL 2026 System Demonstrations](https://arxiv.org/abs/2603.01912) · [arXiv:2603.27991](https://arxiv.org/abs/2603.27991)

</div>
