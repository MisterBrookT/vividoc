# ViviDoc Web UI

This is the React demo interface used in the paper's user study and deployed at **[vividoc.vercel.app](https://vividoc.vercel.app/)**.

## What it is

A three-panel React app (topic input → spec editor → style selector → document viewer) that calls the Python FastAPI backend (`vividoc/entrypoint/`) to run the Planner → Executor → Evaluator pipeline with an external LLM.

## Status

**Demo / legacy.** The primary workflow for ViviDoc is now the Claude Code skill (`/vividoc`), which requires no backend, no API key, and no build step. The web UI is maintained for the live demo and paper reproducibility.

## Running locally

```bash
# Start the backend
export OPENROUTER_API_KEY="sk-or-..."
uv run python -m vividoc.entrypoint.web_server

# Start the frontend
npm install
npm run dev   # http://localhost:5173
```

The backend runs on `:8000`; the frontend proxies API calls to it.
