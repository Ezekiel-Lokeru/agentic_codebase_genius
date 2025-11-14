# tools/api_server.py - FastAPI HTTP endpoint for Codebase Genius
# Exposes the orchestrator as a REST API

import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path so we can import Py modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Py.orchestrator import Orchestrator

# Initialize FastAPI app
app = FastAPI(
    title="Codebase Genius API",
    description="Multi-agent system for automatic codebase documentation generation",
    version="0.1.0",
)

# Initialize orchestrator
orchestrator = Orchestrator(output_root="./outputs")


# Request/Response Models
class GenerateRequest(BaseModel):
    """Request to generate documentation for a repository"""
    url: str
    verbose: Optional[bool] = True


class GenerateResponse(BaseModel):
    """Response from documentation generation"""
    success: bool
    repo_name: Optional[str] = None
    docs_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Codebase Genius API"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_docs(request: GenerateRequest) -> GenerateResponse:
    """
    Generate documentation for a GitHub repository.

    Request Body:
        - url: GitHub repository URL (e.g., "https://github.com/openai/gym")
        - verbose: Enable verbose logging (default: true)

    Returns:
        - success: Whether generation succeeded
        - repo_name: Name of the repository
        - docs_path: Path to generated docs.md file
        - error: Error message (if success=false)
    """
    try:
        result = orchestrator.run(request.url, verbose=request.verbose)
        if result.get("success"):
            return GenerateResponse(
                success=True,
                repo_name=result.get("repo_name"),
                docs_path=result.get("docs_path"),
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Unknown error"),
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/docs-openapi")
async def docs_redirect():
    """Redirect to OpenAPI docs"""
    return {"message": "See /docs for Swagger UI or /redoc for ReDoc"}


if __name__ == "__main__":
    import uvicorn

    print("\n[Codebase Genius API] Starting server...")
    print("  📚 OpenAPI Docs: http://localhost:8000/docs")
    print("  📘 ReDoc Docs: http://localhost:8000/redoc")
    print("  ❤️  Health: http://localhost:8000/health")
    print("  🔧 POST /generate to start documentation generation\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
