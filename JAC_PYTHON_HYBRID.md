# Jac + Python Hybrid Architecture

## Overview

**Codebase Genius** uses a **pragmatic hybrid approach** to integrate Jac and Python:

- **Python**: Primary orchestrator for all multi-agent coordination, code analysis, and documentation generation
- **Jac**: Reference architecture and future-ready design (v0.9+); currently available as design docs for long-term Jac integration

## Why Hybrid?

### The Problem
- **jac v0.8.10** has strict syntax limitations that prevent implementing complex walkers with:
  - Parameter type annotations on abilities
  - Inter-module imports and delegation
  - Python-like control flow within walker bodies
  - Subprocess or external function calls

### The Solution
Rather than invest time in Jac dialect compatibility (which may change in v0.9+), we:

1. **Prioritize Python** for immediate delivery and stability
2. **Keep Jac as reference design** for future integration (v0.9+)
3. **Create a Python bridge** (`Py/jac_bridge.py`) that is callable from Jac via subprocess

This ensures:
- ✅ Fast, stable delivery (Python works now)
- ✅ Jac-ready design (reference docs in `Jac/entry.jac`)
- ✅ Easy upgrade path (when jac v0.9 relaxes syntax, drop-in Jac replacement)

## Current Implementation

### Python Orchestrator
```
GitHub URL
  ↓
Py/jac_bridge.py (entry point, callable from Jac)
  ↓
Py/orchestrator.py (Supervisor)
  ├─→ Py/repo_clone.py (RepoMapper)
  ├─→ Py/parser_ccg.py (CodeAnalyzer)
  └─→ Py/diagram_export.py (DocGenie)
  ↓
./outputs/<repo>/docs.md
```

### Files

| File | Role | Status |
|------|------|--------|
| `Py/orchestrator.py` | Supervisor: coordinates agents, saves docs | ✅ Working |
| `Py/jac_bridge.py` | Entry point: accepts URL, calls orchestrator | ✅ Working |
| `Py/repo_clone.py` | RepoMapper: clone, tree, README | ✅ Working |
| `Py/parser_ccg.py` | CodeAnalyzer: parse, build CCG, mermaid | ✅ Working |
| `Jac/entry.jac` | Reference design (pseudo-code for v0.9+) | ✅ Design |
| `Jac/agents.jac` | Multi-agent design docs | ✅ Design |
| `Jac/repo_mapper.jac` | Jac-style repo mapper (reference) | ✅ Design |

## Usage

### Python CLI (Direct)
```bash
# Use Py/jac_bridge.py as entry point
python Py/jac_bridge.py https://github.com/openai/gym
```

### FastAPI HTTP API
```bash
# Start server
python run_api_server.py

# Submit job
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/openai/gym"}'
```

### Python Direct (Library)
```python
from Py.orchestrator import Orchestrator
orchestrator = Orchestrator()
result = orchestrator.run("https://github.com/openai/gym")
print(result['docs_path'])
```

### Jac (Future, v0.9+)
```bash
# When jac syntax relaxes, this becomes possible:
jac enter -e generate_docs Jac/entry.jac https://github.com/openai/gym
```

Currently, Jac entry delegates to Python bridge via subprocess or direct import.

## Future Roadmap (v0.9+)

When **jac v0.9** relaxes syntax, replace `Py/jac_bridge.py` with native Jac walker:

```jac
walker generate_docs {
    can orchestrate(url: str) {
        # Import Python orchestrator
        orch = py_module("Py.orchestrator")
        
        # Call orchestrator
        result = orch.Orchestrator().run(url, verbose=true)
        
        # Return result
        return result
    }
}
```

**Entry command:**
```bash
jac enter -e orchestrate Jac/entry.jac https://github.com/owner/repo
```

## Multi-Language Support (Post-MVP)

Once Python+Jac are stable, extend RepoMapper + CodeAnalyzer to support:
- **Jac codebases**: Parse Jac walkers, build Jac-specific CCG
- **TypeScript**: Parse TS/JS, build TS type graph
- **Go**: Parse Go, build Go call graph
- etc.

Each language gets:
1. `Py/parser_<lang>.py` — language-specific parser
2. `Py/analyzer_<lang>.py` — language-specific CCG builder
3. Plugged into orchestrator's CodeAnalyzer

## Architecture Evolution

```
v0.1 (Current)       v0.2 (Near)         v0.9+ (Future)
─────────────       ──────────────      ─────────────
Python              Python +             Pure Jac
Orchestrator        Multi-lang           + Multi-lang
                    Analyzers
                    
                    Jac
                    Optional
                    Wrapper
```

## Troubleshooting

### "jac enter" fails with parse error
**Expected.** jac v0.8.10 doesn't support the syntax in Jac/entry.jac.
**Solution:** Use Python CLI: `python Py/jac_bridge.py <url>`

### "No bytecode found for entry.jac"
**Expected.** The design-level Jac code is reference docs, not runnable.
**Solution:** Run Python bridge instead.

### I want to use pure Jac now
**Not supported in v0.1.** Use Python CLI/API instead. Jac support arrives when v0.9+ relaxes syntax.

## Contributing

To extend the system:

1. **Add a new agent (Python)**: Create `Py/my_agent.py`, integrate into `Py/orchestrator.py`
2. **Add a language analyzer**: Create `Py/parser_newlang.py`, extend `Py/orchestrator.py`
3. **Update Jac design**: Modify `Jac/entry.jac` reference (awaits v0.9+)

---

**Questions?** See `README.md` for API reference, `QUICKSTART.py` for usage examples.
