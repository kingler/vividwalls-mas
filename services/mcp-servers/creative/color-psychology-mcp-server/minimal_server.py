"""Minimal Color Psychology MCP Server

A simplified version to get started with basic color extraction functionality.
"""
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="VividWalls Color Psychology MCP Server",
    version="1.0.0",
    description="Extract color information from artwork images"
)

# Configure logging without the problematic format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("color_psychology_mcp")

class AnalyzeRequest(BaseModel):
    """Request payload for /analyze endpoint."""
    image_path: str

def extract_colors(image_path: str, n_colors: int = 5) -> List[Dict[str, Any]]:
    """Extract dominant colors from an image using KMeans clustering."""
    try:
        # Open and resize image for processing
        img = Image.open(image_path)
        img = img.convert('RGB')
        
        # Resize for faster processing
        img.thumbnail((300, 300))
        
        # Convert to numpy array
        img_array = np.array(img)
        pixels = img_array.reshape(-1, 3)
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        # Get color centers and calculate percentages
        colors = kmeans.cluster_centers_.astype(int)
        labels = kmeans.labels_
        
        # Calculate percentage for each color
        color_info = []
        for i, color in enumerate(colors):
            count = np.sum(labels == i)
            percentage = (count / len(labels)) * 100
            
            # Convert to hex
            hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            
            color_info.append({
                "rgb": color.tolist(),
                "hex": hex_color,
                "percentage": round(percentage, 2)
            })
        
        # Sort by percentage
        color_info.sort(key=lambda x: x['percentage'], reverse=True)
        
        return color_info
        
    except Exception as e:
        logger.error(f"Error extracting colors: {str(e)}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "VividWalls Color Psychology MCP Server",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze(req: AnalyzeRequest):
    """Analyze image and extract color information."""
    try:
        logger.info(f"Analyzing image: {req.image_path}")
        
        # Check if file exists
        if not os.path.exists(req.image_path):
            raise HTTPException(status_code=404, detail=f"Image not found: {req.image_path}")
        
        # Extract colors
        colors = extract_colors(req.image_path)
        
        # Prepare response
        result = {
            "status": "success",
            "image_path": req.image_path,
            "colors": colors,
            "color_count": len(colors),
            "primary_color": colors[0] if colors else None
        }
        
        return JSONResponse(content=result)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/upload", response_model=Dict[str, Any])
async def analyze_upload(file: UploadFile = File(...)):
    """Accept image upload and analyze."""
    temp_path = None
    try:
        # Save uploaded file
        temp_path = Path(f"/tmp/{file.filename}")
        with temp_path.open("wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Processing uploaded file: {temp_path}")
        
        # Extract colors
        colors = extract_colors(str(temp_path))
        
        # Prepare response
        result = {
            "status": "success",
            "filename": file.filename,
            "colors": colors,
            "color_count": len(colors),
            "primary_color": colors[0] if colors else None
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if temp_path and temp_path.exists():
            temp_path.unlink()

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8001))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting MCP server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info") 