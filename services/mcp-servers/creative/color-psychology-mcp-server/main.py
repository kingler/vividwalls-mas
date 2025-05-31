"""Color Psychology MCP Server

This module exposes the `ColorPsychologyAnalyzer` via an HTTP JSON API that
conforms to our internal MCP contract.  The implementation prefers the
`fastmcp` library if available (provides ready-made FastAPI wrappers for MCP
function registration).  When `fastmcp` is not present (e.g. local dev
without the enterprise package) we gracefully fall back to a vanilla FastAPI
setup so that developers can still run and test the service.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from color_psychology import ColorPsychologyAnalyzer

# ---------------------------------------------------------------------------
# Optional fastMCP import
# ---------------------------------------------------------------------------
try:
    # fastMCP is a thin wrapper around FastAPI tailored for Task Master MCP
    # services.  If it's available we use it; otherwise we fall back to plain
    # FastAPI while keeping the same route signatures so that the service is
    # compatible with the MCP gateway.
    from fastmcp import FastMCP  # type: ignore

    app = FastMCP(title="Color Psychology MCP Server", version="1.0.0")
    mcp_native = True
except ImportError:  # pragma: no cover – CI may not have fastmcp installed
    from fastapi import FastAPI, HTTPException, UploadFile, File
    from fastapi.responses import JSONResponse

    app = FastAPI(title="Color Psychology MCP Server", version="1.0.0")
    mcp_native = False

# ---------------------------------------------------------------------------
# Configure logging – align with Winston style where possible
# ---------------------------------------------------------------------------
_LOG_FORMAT = "% (asctime)s | %(levelname)8s | ColorPsychologyMCP | %(message)s"
logging.basicConfig(format=_LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger("vividwalls.color_psychology_mcp")

# ---------------------------------------------------------------------------
# Initialiser
# ---------------------------------------------------------------------------

_ANALYZER = ColorPsychologyAnalyzer()

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _save_temp_upload(upload: UploadFile) -> Path:  # type: ignore
    """Persist UploadFile to /tmp and return the path."""
    suffix = Path(upload.filename or "upload.bin").suffix
    temp_path = Path("/tmp") / f"vw_mas_{os.getpid()}_{upload.filename}"
    with temp_path.open("wb") as f_out:
        f_out.write(upload.file.read())
    return temp_path

# ---------------------------------------------------------------------------
# Routes / MCP functions
# ---------------------------------------------------------------------------

if mcp_native:

    @app.mcp_func(name="analyze_image", description="Analyze image and return color-psychology metadata")  # type: ignore[attr-defined]
    def analyze_image(image_path: str) -> Dict[str, Any]:  # noqa: D401
        """Analyze the supplied image path on the MCP server filesystem."""
        logger.info("/analyze_image called with %s", image_path)
        result = _ANALYZER.analyze_image(image_path)
        # Convert ColourEffect objects to dicts for JSON serialisation
        result["effects"] = [e.__dict__ for e in result["effects"]]
        return result

else:

    from pydantic import BaseModel  # pylint: disable=wrong-import-order

    class AnalyzeRequest(BaseModel):
        """Request payload for /analyze endpoint."""

        image_path: str

    @app.post("/analyze", response_model=Dict[str, Any], summary="Analyze image file")
    async def analyze(req: AnalyzeRequest):  # type: ignore
        """Analyze image located on server accessible path; return palette data."""
        try:
            logger.info("/analyze called with %s", req.image_path)
            result = _ANALYZER.analyze_image(req.image_path)
            result["effects"] = [e.__dict__ for e in result["effects"]]
            return JSONResponse(result)
        except FileNotFoundError as exc:
            logger.warning("File not found %s", exc)
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/analyze/upload", response_model=Dict[str, Any], summary="Analyze uploaded image")
    async def analyze_upload(file: UploadFile = File(...)):  # type: ignore
        """Accept raw image upload and run analysis."""
        temp_path = _save_temp_upload(file)
        try:
            logger.info("/analyze/upload processing temp file %s", temp_path)
            result = _ANALYZER.analyze_image(temp_path)
            result["effects"] = [e.__dict__ for e in result["effects"]]
            return JSONResponse(result)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)

# ---------------------------------------------------------------------------
# Entry-point for `uvicorn` or similar ASGI servers
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    log_level = os.environ.get("LOG_LEVEL", "info")
    
    logger.info(f"Starting MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level=log_level) 