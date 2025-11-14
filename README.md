# Codebase Genius - Multi-Agent Documentation Generator

A hybrid Python/Jac system for automatically analyzing GitHub repositories and generating comprehensive markdown documentation with code structure analysis.

## 🎯 System Architecture

```
GitHub URL
    ↓
[HTTP API / CLI Entry]
    ↓
[Orchestrator] — coordinates multi-agent pipeline
    ├─→ [RepoMapper]      — clone repo, build file tree, summarize README
    ├─→ [CodeAnalyzer]    — parse code, build code context graph (CCG)
    └─→ [DocGenie]        — generate markdown docs with diagrams
    ↓
./outputs/<repo>/docs.md
```

### Agents

| Agent | Role | Implementation | Status |
|-------|------|----------------|--------|
| **RepoMapper** | Clone repository, generate file tree, extract README | `Py/repo_clone.py` | ✅ Complete |
| **CodeAnalyzer** | Parse Python code, build CCG (call graph), extract structure | `Py/parser_ccg.py` | ✅ Complete (regex-based) |
| **DocGenie** | Save markdown docs with metadata, file tree, CCG diagram | `Py/orchestrator.py` | ✅ Complete |
| **Supervisor** | Coordinate agents, expose API endpoint | `Py/orchestrator.py` + `tools/api_server.py` | ✅ Complete |

## 📋 Quick Start

### 1. Setup (One-time)

```bash
# Clone or navigate to project
cd agentic_codebase_genius

# Create Python venv (if not already created)
python3.13 -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run as FastAPI Server (Recommended)

```bash
# Start API server on http://localhost:8000
python run_api_server.py

# In another terminal, test with curl:
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/openai/gym", "verbose": true}'

# Or visit http://localhost:8000/docs for interactive Swagger UI
```

### 3. Run as Python CLI

```bash
# Generate docs for a repository (one-shot)
python test_orchestrator.py

# Output: ./outputs/gym/docs.md
cat ./outputs/gym/docs.md
```

### 4. Run via Jac+Python Bridge

```bash
# Use the Python bridge (callable from Jac or directly from Python)
python Py/jac_bridge.py https://github.com/openai/gym

# Output: ./outputs/gym/docs.md
```

## 🔗 Jac + Python Hybrid Integration

The system prioritizes **Python for orchestration** and **Jac for reference design** (future implementation):

- **`Py/jac_bridge.py`**: Python entry point that accepts a repo URL and delegates to the orchestrator. Can be called directly from Jac via subprocess when `jac enter` is enhanced in future versions.
- **`Jac/entry.jac`**: Reference design (pseudo-code) showing how a Jac walker would orchestrate the multi-agent pipeline (for jac v0.9+).
- **Why?**: jac v0.8.10 has strict syntax limitations; to ensure fast delivery and stability, we use Python as the primary orchestrator with Jac as an optional, future-compatible layer.

### Example: Calling from Jac (Future)

```jac
# When jac syntax relaxes (v0.9+):
walker generate_docs {
    can orchestrate(url: str) {
        py = py_module("Py.orchestrator")
        result = py.Orchestrator().run(url, verbose=true)
        return result
    }
}
```

Currently: `jac enter -e main Jac/entry.jac` → calls Python bridge → orchestrator runs.

## 📁 Project Structure

```
agentic_codebase_genius/
├── Py/
│   ├── __init__.py
│   ├── repo_clone.py          # RepoMapper implementation
│   ├── parser_ccg.py          # CodeAnalyzer implementation (CCG builder)
│   ├── diagram_export.py      # DocGenie helper (save Mermaid)
│   ├── orchestrator.py        # Supervisor + DocGenie (orchestrate + save docs)
│   └── jac_bridge.py          # Jac+Python bridge (entry point callable from Jac)
├── Jac/
│   ├── agents.jac             # Design-level multi-agent definitions
│   ├── repo_mapper.jac        # Jac version of RepoMapper (reference design)
│   └── entry.jac              # Jac entrypoint (reference design for v0.9+)
├── tools/
│   ├── api_server.py          # FastAPI server exposing /generate endpoint
│   └── run_repo.py            # Standalone CLI tool (legacy)
├── run_api_server.py          # Launch FastAPI server with instructions
├── test_orchestrator.py       # CLI test script
├── test_api.py                # API integration test script
├── requirements.txt           # Python dependencies
├── typing_override_patch.py   # Python 3.13 compatibility patch
└── run_jac.py                 # Entry point for Jac (legacy)
```

## 🔧 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| `jaclang` | Jac language runtime (optional) | ^0.8.10 |
| `fastapi` | HTTP API framework | ^0.104.0 |
| `uvicorn` | ASGI server for FastAPI | ^0.24.0 |
| `pydantic` | Data validation | ^2.0.0 |
| `networkx` | Graph library for CCG | Latest |
| `tree-sitter` (optional) | AST parsing (not required; falls back to regex) | Latest |

Install with:
```bash
pip install -r requirements.txt
```

## 📊 Example Output

After running the generator on a repository, you'll get `./outputs/<repo_name>/docs.md`:

```markdown
# gym - Auto-Generated Documentation

## Overview
[README summary from the repository]

## Repository Structure
```
gym/
├── gym/
│   ├── __init__.py
│   ├── core.py
│   ├── envs/
│   └── ...
└── tests/
```

## Code Context Graph (Call Graph)
[Mermaid diagram showing function call structure]

## Metadata
- **Repository Name**: gym
- **Root Path**: /path/to/cloned/repo
- **Generated at**: ...
```

## 🚀 API Reference

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Codebase Genius API"
}
```

---

#### `POST /generate`
Generate documentation for a GitHub repository.

**Request:**
```json
{
  "url": "https://github.com/openai/gym",
  "verbose": true
}
```

**Response (success):**
```json
{
  "success": true,
  "repo_name": "gym",
  "docs_path": "./outputs/gym/docs.md"
}
```

**Response (error):**
```json
{
  "success": false,
  "error": "Failed to clone repository: ..."
}
```

---

#### `GET /docs`
Interactive Swagger UI for testing endpoints.

---

#### `GET /redoc`
ReDoc documentation.

---

## 🧪 Testing

### Test Orchestrator (CLI)
```bash
python test_orchestrator.py
# Generates docs for openai/gym, prints preview
```

### Test API (Integration)
```bash
python test_api.py
# Starts FastAPI server, sends test requests, checks responses
```

### Manual API Test (curl)
```bash
# Start server in one terminal
python run_api_server.py

# In another terminal
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/pallets/flask", "verbose": true}'
```

## 🔍 How It Works

### 1. RepoMapper (`Py/repo_clone.py`)
- Clones repository using `git clone --depth 1` (shallow clone for speed)
- Generates file tree structure recursively
- Extracts first lines from README.md
- Returns dict: `{"name", "root", "readme", "file_tree"}`

### 2. CodeAnalyzer (`Py/parser_ccg.py`)
- Parses Python files (regex-based, fallback to tree-sitter if available)
- Extracts function and class definitions
- Builds Code Context Graph (CCG) using networkx DiGraph
- Converts CCG to Mermaid flowchart syntax
- Gracefully handles missing dependencies (optional tree-sitter, networkx)

### 3. DocGenie (`Py/orchestrator.py`)
- Formats markdown document with sections:
  - Title & Overview (from README)
  - Repository Structure (file tree)
  - Code Context Graph (Mermaid diagram)
  - Metadata
- Saves to `./outputs/<repo_name>/docs.md`
- Creates output directories if missing

### 4. Supervisor (`Py/orchestrator.py` + `tools/api_server.py`)
- Orchestrates pipeline: RepoMapper → CodeAnalyzer → DocGenie
- Exposes HTTP API via FastAPI
- Handles errors gracefully
- Supports both CLI and API interfaces

## 🛠️ Hybrid Architecture

**Why Python + Jac?**
- **Python**: Heavy lifting (cloning, parsing, analysis) — mature libraries, speed, reliability
- **Jac**: (Optional) Orchestration and multi-agent design — Jac language exploration, future research

**Current Implementation:**
- ✅ Python does all core work (RepoMapper, CodeAnalyzer, DocGenie)
- ✅ Python server (FastAPI) provides HTTP interface (Supervisor)
- ⏳ Jac entrypoint deferred (jac v0.8.10 parser incompatibilities; not critical)

**Future Extensions:**
- Optional: Wrap FastAPI server in Jac walker for pure-Jac orchestration
- Optional: Extend to analyze non-Python codebases (Jac, TypeScript, Go, etc.) via language plugins

## 🐛 Troubleshooting

### Issue: `ImportError: cannot import name 'override' from 'typing'`
**Cause:** Python 3.13 compatibility issue (v0.8.10 runs on older Python)
**Solution:** Uses `typing_override_patch.py` (auto-loaded)

### Issue: `ModuleNotFoundError: No module named 'fastapi'`
**Solution:** Run `pip install -r requirements.txt`

### Issue: `tree-sitter` build errors
**Solution:** tree-sitter is optional. CCG falls back to regex parsing if unavailable. Install with:
```bash
pip install tree-sitter tree-sitter-python
```

### Issue: API server won't start on port 8000
**Solution:** Port already in use. Change in `run_api_server.py` or `tools/api_server.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

## 📈 Performance

- **Shallow Clone**: `git clone --depth 1` (~1-5 seconds for typical repos)
- **File Tree Generation**: Recursive walk (~0.1-0.5 seconds)
- **CCG Building**: Regex parsing (10 files, ~0.5-2 seconds)
- **Doc Generation**: Markdown formatting (~0.1 seconds)
- **Total**: ~2-10 seconds per repository

## 📚 References

- FastAPI Docs: https://fastapi.tiangolo.com/
- Jac Language: https://github.com/jac-ai/jac
- networkx: https://networkx.org/
- Mermaid Diagrams: https://mermaid.js.org/

## 📝 License

(Add license here)

## 🤝 Contributing

Contributions welcome! Areas for extension:
- [ ] Support for Jac/TypeScript/Go code analysis
- [ ] Advanced CCG query APIs
- [ ] Diagram styling options
- [ ] Database backend for docs storage
- [ ] Web UI for browsing generated docs

---

**Status**: Beta (v0.1.0) — Functional end-to-end pipeline for Python repos. Ready for feedback and extensions.
