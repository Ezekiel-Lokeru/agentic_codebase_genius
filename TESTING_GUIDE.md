# Testing Guide - Codebase Genius

## Quick Answer: 5 Ways to Test with ANY Repository

### Method 1: One-Shot CLI Test
**Fastest for a quick test**

```bash
# Test with the gym repo (default)
python test_orchestrator.py
```

**To test with a different repo, edit `test_orchestrator.py` line 14:**
```python
REPO_URL = "https://github.com/owner/repo"  # Change this
```

Then run:
```bash
python test_orchestrator.py
```

---

### Method 2: Python Bridge (Jac-Compatible)
**Recommended for testing different repos without editing files**

```bash
# Test gym repo
python Py/jac_bridge.py https://github.com/openai/gym

# Test flask repo
python Py/jac_bridge.py https://github.com/pallets/flask

# Test any repo
python Py/jac_bridge.py https://github.com/owner/repo
```

**Output:** Success/failure message + path to generated docs (`./outputs/<repo>/docs.md`)

---

### Method 3: FastAPI Server (HTTP API)
**Best for testing multiple repos in a session**

**Terminal 1: Start server**
```bash
python run_api_server.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2: Test with different repos**
```bash
# Test gym
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/openai/gym"}'

# Test flask
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/pallets/flask"}'

# Test httpx
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/encode/httpx"}'

# Test ANY repo
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://github.com/owner/repo"}'
```

**Response:** JSON with success status and docs path

```json
{
  "success": true,
  "repo_name": "gym",
  "docs_path": "./outputs/gym/docs.md"
}
```

**Browser UI:** Visit `http://localhost:8000/docs` for interactive API explorer

---

### Method 4: Automated Integration Tests
**Tests multiple repos at once**

```bash
python test_jac_integration.py
```

**What it tests:**
- Python bridge with gym repo
- Orchestrator direct with httpx repo
- Reports pass/fail for each

**To add more repos to test, edit `test_jac_integration.py`:**
```python
def test_orchestrator_direct():
    test_repo = "https://github.com/encode/httpx"  # Change this
    orchestrator = Orchestrator(output_root="./outputs")
    result = orchestrator.run(test_repo, verbose=True)
```

---

### Method 5: Python Library (Programmatic)
**For integration into your own code**

```python
from Py.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(output_root="./outputs")

# Test with different repos
repos = [
    "https://github.com/openai/gym",
    "https://github.com/pallets/flask",
    "https://github.com/encode/httpx",
]

for repo_url in repos:
    result = orchestrator.run(repo_url, verbose=False)
    if result["success"]:
        print(f"✓ {result['repo_name']}: {result['docs_path']}")
    else:
        print(f"✗ {result['repo_name']}: {result['error']}")
```

---

## Common Test Repos

| Repo | URL | Type | Size |
|------|-----|------|------|
| Gym | https://github.com/openai/gym | ML/RL | Small |
| Flask | https://github.com/pallets/flask | Web | Small |
| HTTPX | https://github.com/encode/httpx | HTTP Client | Very Small (FAST) |
| Scikit-learn | https://github.com/scikit-learn/scikit-learn | ML | Large |
| PyTorch | https://github.com/pytorch/pytorch | Deep Learning | Very Large |

**Recommendation for quick testing:** Start with HTTPX (smallest, fastest)

---

## Troubleshooting Test Issues

### Issue: "Cannot find module Py.orchestrator"
**Solution:** Make sure you're running from workspace root:
```bash
cd c:\Users\Anonymous\Desktop\Jac_lang\agentic_codebase_genius
python Py/jac_bridge.py https://github.com/openai/gym
```

### Issue: "git not installed"
**Solution:** Install Git from https://git-scm.com/download/win

### Issue: "Cloning times out or is very slow"
**Solution:** Use a smaller repo (e.g., HTTPX instead of PyTorch)
```bash
python Py/jac_bridge.py https://github.com/encode/httpx
```

### Issue: "Output directory ./outputs not created"
**Solution:** The system creates it automatically. If it fails:
```bash
mkdir outputs
```

### Issue: "Documentation file is empty"
**Solution:** This usually means the repo analysis failed. Check verbose output:
```bash
python Py/jac_bridge.py https://github.com/owner/repo
```

Look for error messages in [RepoMapper], [CodeAnalyzer], or [DocGenie] sections.

---

## Viewing Results

After any test, view the generated documentation:

```bash
# Open the docs in default browser (if on Windows GUI)
start ./outputs/gym/docs.md

# Or view with PowerShell
Get-Content ./outputs/gym/docs.md

# Or view size
(Get-Item ./outputs/gym/docs.md).Length
```

Expected output:
- **File:** `./outputs/<repo>/docs.md`
- **Size:** 2-10 KB (depending on repo)
- **Format:** Markdown with sections: Overview, File Tree, CCG Diagram

---

## Test Script Template

Save this as `test_custom.py` to quickly test any repos:

```python
#!/usr/bin/env python
"""Test any repositories."""

from Py.orchestrator import Orchestrator

# Test these repos
test_repos = [
    "https://github.com/encode/httpx",
    "https://github.com/pallets/flask",
    "https://github.com/openai/gym",
]

orchestrator = Orchestrator(output_root="./outputs", max_workers=2)

print("\n" + "="*70)
print("TESTING MULTIPLE REPOSITORIES")
print("="*70 + "\n")

passed = 0
failed = 0

for repo_url in test_repos:
    print(f"Testing: {repo_url}")
    try:
        result = orchestrator.run(repo_url, verbose=False)
        if result["success"]:
            print(f"  ✓ SUCCESS: {result['docs_path']}\n")
            passed += 1
        else:
            print(f"  ✗ FAILED: {result['error']}\n")
            failed += 1
    except Exception as e:
        print(f"  ✗ ERROR: {e}\n")
        failed += 1

print("="*70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("="*70)
```

Save and run:
```bash
python test_custom.py
```

---

## Performance Expectations

| Stage | Time | Notes |
|-------|------|-------|
| Git clone | 5-30s | Depends on repo size |
| File tree scan | 1-5s | Recursive directory scan |
| Code parsing | 5-30s | Regex-based or tree-sitter |
| CCG building | 2-10s | Dependency graph construction |
| Doc generation | 1-5s | Markdown writing |
| **Total** | **15-80s** | Small repo: ~20s, Large repo: ~60s |

**Fastest combo:** HTTPX repo via API method = ~15-20s total

---

## Next Steps

**Immediate:**
- [ ] Run Method 1: `python test_orchestrator.py`
- [ ] Run Method 2: `python Py/jac_bridge.py https://github.com/encode/httpx`
- [ ] Check output in `./outputs/httpx/docs.md`

**After verifying it works:**
- [ ] Try different repos (flask, gym, scikit-learn)
- [ ] Start API server and test via curl
- [ ] Run full integration tests: `python test_jac_integration.py`

**For production:**
- [ ] Deploy FastAPI server (Method 3)
- [ ] Monitor performance with different repo sizes
- [ ] Configure output_root for persistent storage

---

**Status:** All testing methods ready. Pick the one that fits your workflow! 🚀
