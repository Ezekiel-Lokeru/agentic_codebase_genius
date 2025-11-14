#!/usr/bin/env python
"""
Integration test: Jac+Python bridge and orchestrator.
Tests that Py/jac_bridge.py correctly calls the orchestrator.
"""

import sys
import os
import subprocess

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Py.orchestrator import Orchestrator


def test_python_bridge():
    """Test Py/jac_bridge.py works correctly."""
    print("\n" + "="*70)
    print("TEST 1: Python Bridge (Py/jac_bridge.py)")
    print("="*70 + "\n")

    test_repo = "https://github.com/openai/gym"
    bridge_script = os.path.join(os.path.dirname(__file__), "Py", "jac_bridge.py")

    print(f"Running: python Py/jac_bridge.py {test_repo}\n")

    result = subprocess.run(
        [sys.executable, bridge_script, test_repo],
        capture_output=False,
        timeout=120,
    )

    success = result.returncode == 0
    print("\nBridge result:", "SUCCESS" if success else "FAILED")
    return success


def test_orchestrator_direct():
    """Test Orchestrator directly."""
    print("\n" + "="*70)
    print("TEST 2: Orchestrator Direct (Py/orchestrator.py)")
    print("="*70 + "\n")

    test_repo = "https://github.com/encode/httpx"

    orchestrator = Orchestrator(output_root="./outputs")
    result = orchestrator.run(test_repo, verbose=True)

    success = result.get("success", False)
    if success:
        print(f"\nOrchestrator result: SUCCESS")
        print(f"  Repo: {result['repo_name']}")
        print(f"  Docs: {result['docs_path']}")
    else:
        print(f"\nOrchestrator result: FAILED")
        print(f"  Error: {result.get('error')}")

    return success


def main():
    print("\n" + "="*70)
    print("CODEBASE GENIUS - JAC+PYTHON INTEGRATION TESTS")
    print("="*70)

    tests = [
        ("Python Bridge", test_python_bridge),
        ("Orchestrator Direct", test_orchestrator_direct),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\nException in {name}: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed\n")

    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
