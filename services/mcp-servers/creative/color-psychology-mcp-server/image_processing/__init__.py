"""
Image processing package for VividWalls Color Palette Agent.

This package contains modules for:
- OpenAI Vision API integration
- Color extraction from images
- Image generation configuration
- Composite image creation
"""

from .generation_config import (
    ImageGenerationConfig,
    DEFAULT_GENERATION_CONFIG,
    get_generation_prompt
)

__all__ = [
    'ImageGenerationConfig',
    'DEFAULT_GENERATION_CONFIG',
    'get_generation_prompt'
]
