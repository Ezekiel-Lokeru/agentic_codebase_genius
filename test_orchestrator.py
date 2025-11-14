#!/usr/bin/env python
"""
Quick test of the Codebase Genius orchestrator.
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Py.orchestrator import Orchestrator

def main():
    print("\n" + "="*70)
    print("CODEBASE GENIUS ORCHESTRATOR - END-TO-END TEST")
    print("="*70)

    # Test with openai/gym repo (small, well-structured)
    repo_url = "https://github.com/openai/gym"

    orchestrator = Orchestrator(output_root="./outputs")
    
    result = orchestrator.run(repo_url, verbose=True)

    print("\n" + "="*70)
    print("TEST RESULT")
    print("="*70)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Repository: {result['repo_name']}")
        print(f"Documentation saved to: {result['docs_path']}")
        
        # Show first 500 chars of generated docs
        with open(result['docs_path'], 'r') as f:
            content = f.read()
        print(f"\n--- Generated Docs Preview (first 800 chars) ---")
        print(content[:800])
        print("\n--- (truncated) ---\n")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
