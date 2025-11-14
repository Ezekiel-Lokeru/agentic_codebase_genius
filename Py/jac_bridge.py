#!/usr/bin/env python
"""
Jac-Python bridge: Run Jac entrypoint with Python orchestrator delegation.
Provides a simple entry point that Jac can call via subprocess or direct Python invocation.
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Py.orchestrator import Orchestrator


def main():
    """
    Entry point for both Jac and Python CLI.
    Reads repo URL from command-line arguments and delegates to orchestrator.
    """
    if len(sys.argv) < 2:
        print("Usage: python jac_bridge.py <github_url>")
        print("Example: python jac_bridge.py https://github.com/openai/gym")
        sys.exit(1)

    repo_url = sys.argv[1]

    print("\n" + "="*70)
    print("CODEBASE GENIUS - JAC ENTRY POINT")
    print("="*70)
    print(f"\nRepository URL: {repo_url}\n")

    orchestrator = Orchestrator(output_root="./outputs")
    result = orchestrator.run(repo_url, verbose=True)

    print("\n" + "="*70)
    if result["success"]:
        print("SUCCESS - Documentation generated")
        print(f"Repository: {result['repo_name']}")
        print(f"Documentation: {result['docs_path']}")
    else:
        print("FAILED - Error occurred")
        print(f"Error: {result.get('error', 'Unknown error')}")
    print("="*70 + "\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
