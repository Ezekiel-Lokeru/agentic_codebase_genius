#!/usr/bin/env python
"""
Quick test of the Codebase Genius FastAPI server.
Uses requests to test the /generate endpoint.
"""

import sys
import os
import time
import subprocess
import requests
import json

def test_api():
    """Test the API with a sample request"""
    
    print("\n" + "="*70)
    print("CODEBASE GENIUS API - INTEGRATION TEST")
    print("="*70)

    # Start server in background
    print("\n[API Test] Starting FastAPI server...")
    server_process = subprocess.Popen(
        [sys.executable, "tools/api_server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)

    try:
        # Test health check
        print("[API Test] Testing /health endpoint...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")

        # Test documentation generation
        print("\n[API Test] Posting to /generate endpoint...")
        payload = {"url": "https://github.com/pallets/flask", "verbose": True}
        print(f"  Request: {json.dumps(payload, indent=2)}")

        response = requests.post(
            "http://localhost:8000/generate",
            json=payload,
            timeout=120,  # 2 min timeout for cloning/analyzing
        )
        print(f"  Status: {response.status_code}")
        result = response.json()
        print(f"  Response: {json.dumps(result, indent=2)}")

        if response.status_code == 200 and result.get("success"):
            docs_path = result.get("docs_path")
            print(f"\n[API Test] ✓ Documentation generated successfully!")
            print(f"  Location: {docs_path}")
            if os.path.exists(docs_path):
                with open(docs_path, 'r') as f:
                    content = f.read()
                print(f"  File size: {len(content)} bytes")
        else:
            print(f"\n[API Test] ✗ Request failed: {result.get('error', 'Unknown error')}")

    except requests.exceptions.ConnectionError:
        print("  ✗ Could not connect to server on localhost:8000")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        # Stop server
        print("\n[API Test] Stopping server...")
        server_process.terminate()
        server_process.wait(timeout=5)
        print("[API Test] Server stopped.")

if __name__ == "__main__":
    test_api()
