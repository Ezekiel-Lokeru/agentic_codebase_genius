#!/usr/bin/env python
"""
QUICK TESTER - Test Codebase Genius with ANY repository in one command.

Usage:
    python quick_test.py <repo_url> [optional_flags]

Examples:
    python quick_test.py https://github.com/openai/gym
    python quick_test.py https://github.com/pallets/flask --verbose
    python quick_test.py https://github.com/encode/httpx --no-verbose

Supported flags:
    --verbose      Show detailed output (default)
    --quiet        Show only final result
    --help         Show this message
"""

import sys
import os
from Py.orchestrator import Orchestrator


def main():
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print(__doc__)
        return 0

    repo_url = sys.argv[1]
    verbose = "--quiet" not in sys.argv
    
    print("\n" + "="*70)
    print("CODEBASE GENIUS - QUICK TESTER")
    print("="*70)
    print(f"\nRepository: {repo_url}")
    print(f"Verbose: {verbose}\n")

    try:
        orchestrator = Orchestrator(output_root="./outputs")
        result = orchestrator.run(repo_url, verbose=verbose)

        print("\n" + "="*70)
        if result["success"]:
            print("✓ SUCCESS")
            print(f"  Repository: {result['repo_name']}")
            print(f"  Documentation: {result['docs_path']}")
            
            # Show file size
            if os.path.exists(result['docs_path']):
                size_kb = os.path.getsize(result['docs_path']) / 1024
                print(f"  File Size: {size_kb:.1f} KB")
                
                # Show first few lines
                with open(result['docs_path'], 'r') as f:
                    lines = f.readlines()[:10]
                    print(f"  Preview (first {len(lines)} lines):")
                    for line in lines:
                        print(f"    {line.rstrip()}")
                    if len(lines) == 10:
                        print("    ...")
        else:
            print("✗ FAILED")
            print(f"  Error: {result.get('error', 'Unknown error')}")
        print("="*70 + "\n")
        
        return 0 if result["success"] else 1

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
