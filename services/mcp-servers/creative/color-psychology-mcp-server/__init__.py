"""
VividWalls Color Psychology MCP Server

An MCP server that analyzes customer room images and recommends artwork
based on color composition and psychological analysis.

CRITICAL: NO HUMANS OR ANIMALS in any generated images.
"""

__version__ = "1.0.0"
__author__ = "VividWalls Team"
__description__ = "Color Psychology MCP Server for artwork recommendations"

# Import key components for easy access
from .image_processing.generation_config import (
    STRICT_GENERATION_CONFIG,
    get_safe_generation_prompt
)

from .data import (
    init_database,
    get_database,
    ColorTheoryKnowledge,
    Artwork,
    RoomAnalysis,
    ensure_no_living_beings
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__description__',
    
    # Database
    'init_database',
    'get_database',
    'ColorTheoryKnowledge',
    'Artwork', 
    'RoomAnalysis',
    
    # Safety
    'ensure_no_living_beings',
    'STRICT_GENERATION_CONFIG',
    'get_safe_generation_prompt'
] 