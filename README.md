# ViviDoc

A multi-agent system that generates interactive documents (explorarable explanations) from any topic. 

**[Live Demo](https://vividoc.vercel.app/)**

![screenshot](assets/demo-screenshot.png)

## Setup

```bash
# Install dependencies
uv sync --dev

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-key"
```

## Usage

### CLI

```bash
vividoc run "Fourier Transform" openrouter/google/gemini-3-flash-preview

### Web UI

```bash
# Start backend (http://localhost:8000)
vividoc serve

# Start frontend (http://localhost:5173)
cd frontend && npm install && npm run dev
```

## License

MIT
