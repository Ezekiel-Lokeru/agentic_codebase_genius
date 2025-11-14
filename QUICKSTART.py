#!/usr/bin/env python
"""
QUICK START GUIDE - How to Use Codebase Genius

This file demonstrates all the ways to run the system.
"""

# ============================================================================
# METHOD 1: CLI (One-Shot)
# ============================================================================

def method1_cli():
    """Generate documentation for a repo and exit."""
    print("\n=== METHOD 1: CLI (One-Shot) ===\n")
    print("Command:")
    print("  python test_orchestrator.py")
    print("\nWhat it does:")
    print("  1. Clones openai/gym (shallow)")
    print("  2. Generates file tree")
    print("  3. Builds code context graph")
    print("  4. Saves to ./outputs/gym/docs.md")
    print("\nOutput:")
    print("  Success: True")
    print("  Repository: gym")
    print("  Documentation saved to: ./outputs/gym/docs.md")


# ============================================================================
# METHOD 2: FastAPI Server (HTTP API)
# ============================================================================

def method2_api_server():
    """Start a long-running HTTP server."""
    print("\n=== METHOD 2: FastAPI Server ===\n")
    print("Step 1: Start the server")
    print("  python run_api_server.py")
    print("\nStep 2: In another terminal, send requests")
    print("  curl -X GET http://localhost:8000/health")
    print("  curl -X POST http://localhost:8000/generate \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"url\": \"https://github.com/pallets/flask\", \"verbose\": true}'")
    print("\nStep 3: Visit interactive docs")
    print("  http://localhost:8000/docs          (Swagger UI)")
    print("  http://localhost:8000/redoc         (ReDoc)")
    print("\nResponse Example:")
    print("  {")
    print("    \"success\": true,")
    print("    \"repo_name\": \"flask\",")
    print("    \"docs_path\": \"./outputs/flask/docs.md\"")
    print("  }")


def method2b_jac_bridge():
    """Call Python bridge (Jac-compatible entry point)."""
    print("\n=== METHOD 2b: Jac+Python Bridge ===\n")
    print("Command:")
    print("  python Py/jac_bridge.py https://github.com/pallets/flask")
    print("\nWhat it does:")
    print("  1. Acts as a Jac-compatible entry point")
    print("  2. Accepts GitHub URL as command-line argument")
    print("  3. Delegates to Python orchestrator")
    print("  4. Saves docs to ./outputs/flask/docs.md")
    print("\nWhy:")
    print("  - Can be called from Jac via subprocess (v0.8.10 compatible)")
    print("  - Designed for future Jac integration (v0.9+)")
    print("  - Bridges Python and Jac layers")


# ============================================================================
# METHOD 3: Python Library (Programmatic)
# ============================================================================

def method3_python_library():
    """Import and use orchestrator in your own code."""
    print("\n=== METHOD 3: Python Library ===\n")
    print("Code:")
    print("""
from Py.orchestrator import Orchestrator

# Create orchestrator
orchestrator = Orchestrator(output_root="./outputs")

# Generate documentation
result = orchestrator.run(
    repo_url="https://github.com/openai/gym",
    verbose=True
)

# Check result
if result["success"]:
    print(f"Success! Docs at: {result['docs_path']}")
else:
    print(f"Error: {result['error']}")
""")


# ============================================================================
# METHOD 4: Docker/Cloud Deployment
# ============================================================================

def method4_docker():
    """Deploy with Docker for production."""
    print("\n=== METHOD 4: Docker Deployment ===\n")
    print("Dockerfile example:")
    print("""
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_api_server.py"]

# Build: docker build -t codebase-genius .
# Run: docker run -p 8000:8000 codebase-genius
""")


# ============================================================================
# EXAMPLES
# ============================================================================

def examples():
    """Show usage examples with different repos."""
    print("\n=== USAGE EXAMPLES ===\n")
    
    examples_list = [
        ("Python Project", "https://github.com/pallets/flask"),
        ("Data Science", "https://github.com/scikit-learn/scikit-learn"),
        ("DevOps", "https://github.com/kubernetes/kubernetes"),
        ("Machine Learning", "https://github.com/pytorch/pytorch"),
        ("CLI Tool", "https://github.com/cli/cli"),
    ]
    
    for name, url in examples_list:
        print(f"Example: {name}")
        print(f"  Repo: {url}")
        print(f"  Command (API):")
        print(f"    curl -X POST http://localhost:8000/generate \\")
        print(f"      -H 'Content-Type: application/json' \\")
        print(f"      -d '{{\"url\": \"{url}\"}}'")
        print()


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

def troubleshooting():
    """Common issues and solutions."""
    print("\n=== TROUBLESHOOTING ===\n")
    
    issues = [
        (
            "Port 8000 already in use",
            "Change port in run_api_server.py or kill process using port 8000"
        ),
        (
            "ModuleNotFoundError: fastapi",
            "Run: pip install -r requirements.txt"
        ),
        (
            "Git command not found",
            "Install Git: https://git-scm.com/download"
        ),
        (
            "Python 3.13 not found",
            "Install Python 3.13+ or use your system Python version"
        ),
        (
            "CCG/Tree-sitter errors",
            "These are optional; system will work without them"
        ),
    ]
    
    for issue, solution in issues:
        print(f"❌ Issue: {issue}")
        print(f"✓ Solution: {solution}")
        print()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("CODEBASE GENIUS - QUICK START GUIDE")
    print("="*70)
    
    method1_cli()
    method2_api_server()
    method2b_jac_bridge()
    method3_python_library()
    method4_docker()
    examples()
    troubleshooting()
    
    print("="*70)
    print("\n🚀 Ready to go! Start with METHOD 1 (CLI) or METHOD 2 (Server).\n")
