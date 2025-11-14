#!/usr/bin/env python
"""
Minimal API server launcher with instructions.
"""

if __name__ == "__main__":
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from tools.api_server import app
    import uvicorn
    
    print("\n" + "="*70)
    print("CODEBASE GENIUS API - PRODUCTION SERVER")
    print("="*70)
    print("\n✅ Server is starting on http://localhost:8000")
    print("\n📚 Available Endpoints:")
    print("  - GET  /health                  ➜ Health check")
    print("  - POST /generate                ➜ Generate documentation for GitHub repo")
    print("  - GET  /docs                    ➜ Interactive Swagger UI")
    print("  - GET  /redoc                   ➜ ReDoc documentation")
    print("\n📝 Example Request (curl):")
    print('  curl -X POST http://localhost:8000/generate \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"url": "https://github.com/openai/gym", "verbose": true}\'')
    print("\n⚠️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
