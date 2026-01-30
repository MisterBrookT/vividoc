# ViviDoc

ViviDoc is an interactive educational document generation system with a web-based UI.

## Features

- **Spec Generation**: Generate document specifications from topics using AI
- **Interactive Editing**: Edit, reorder, and manage knowledge units
- **Document Generation**: Create interactive HTML documents with visualizations
- **Progress Monitoring**: Real-time progress tracking during generation
- **Local Storage**: Specs automatically saved to local filesystem

## Architecture

- **Backend**: FastAPI + Python (Planner, Executor, Evaluator agents)
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS v4
- **Storage**: Local filesystem (`outputs/` directory)

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone repository
git clone <repository-url>
cd viviDoc

# Install Python dependencies
uv sync --dev

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## Running the Application

### Start Backend

```bash
# From project root
vividoc serve
```

Backend will run on `http://localhost:8000`

Optional flags:
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development

### Start Frontend

```bash
# From project root
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Enter a topic in the input field
3. Click "Generate Spec" to create a document specification
4. Edit knowledge units as needed (drag to reorder, click Edit/Delete)
5. Click "Generate Document" to create the interactive HTML
6. View progress in the right panel
7. Preview and download the generated document

## Project Structure

```
viviDoc/
├── vividoc/          # Core package
│   ├── entrypoint/   # Web server & API
│   │   ├── api/      # API routes
│   │   ├── models/   # API data models
│   │   ├── services/ # Business logic (JobManager, SpecService, DocumentService)
│   │   └── web_server.py  # FastAPI app factory
│   ├── planner.py    # Spec generation agent
│   ├── executor.py   # Document generation agent
│   ├── evaluator.py  # Quality evaluation agent
│   ├── runner.py     # CLI pipeline runner
│   └── cli.py        # CLI commands
├── frontend/         # React frontend
│   └── src/
│       ├── components/  # UI components
│       ├── api/        # API client
│       └── types/      # TypeScript types
├── outputs/          # Generated specs & documents (UUID-based folders)
├── tests/            # Test suite
└── datasets/         # Training data
```

## CLI Usage

```bash
# View all commands
vividoc --help

# Start web server
vividoc serve

# Run complete pipeline (plan → execute → evaluate)
vividoc run "Your topic here"

# Individual phases
vividoc plan "Your topic" --output spec.json
vividoc exec spec.json --output doc.json
vividoc eval doc.json --output eval.json
```

All generated files are saved to `outputs/{uuid}/` where UUID is deterministically generated from the topic.

## License

MIT
