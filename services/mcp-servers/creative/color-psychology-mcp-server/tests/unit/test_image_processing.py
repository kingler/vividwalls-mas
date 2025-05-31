#!/usr/bin/env python3
"""
Unit tests for image processing modules.

Following TDD principles - these tests define expected behavior
for OpenAI Vision API integration and color extraction functionality.
"""

import os
import sys
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, Mock
from typing import List, Dict, Any
import tempfile
from PIL import Image
import json

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import modules to be tested
from image_processing.vision_api import VisionAPI, ImageAnalysisResult
from image_processing.color_extractor import ColorExtractor, ColorInfo, ColorPalette


class TestVisionAPI:
    """Test OpenAI Vision API integration."""
    
    def test_vision_api_initialization(self):
        """Test VisionAPI initialization with API key."""
        # Arrange
        api_key = "test-api-key"
        
        # Act
        vision_api = VisionAPI(api_key)
        
        # Assert
        assert vision_api is not None
        assert vision_api.api_key == api_key
        assert vision_api.model == "gpt-4o"
    
    @patch('openai.Client')
    def test_analyze_image_basic(self, mock_client):
        """Test basic image analysis functionality."""
        # Arrange
        vision_api = VisionAPI("test-key")
        test_image_path = "test.jpg"
        
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "objects": [
                    {"type": "sofa", "position": {"x": 100, "y": 200}, "confidence": 0.95},
                    {"type": "table", "position": {"x": 300, "y": 250}, "confidence": 0.89}
                ],
                "room_type": "living_room",
                "walls": [
                    {"id": 1, "position": "north", "empty_space": 80},
                    {"id": 2, "position": "east", "empty_space": 60}
                ]
            })))
        ]
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        # Act
        result = vision_api.analyze_image(test_image_path)
        
        # Assert
        assert isinstance(result, ImageAnalysisResult)
        assert len(result.objects) == 2
        assert result.room_type == "living_room"
        assert len(result.walls) == 2
    
    def test_analyze_image_filters_humans_and_animals(self):
        """Test that humans and animals are filtered from results."""
        # Arrange
        vision_api = VisionAPI("test-key")
        
        with patch.object(vision_api, '_call_vision_api') as mock_call:
            mock_call.return_value = {
                "objects": [
                    {"type": "person", "position": {"x": 100, "y": 100}},
                    {"type": "dog", "position": {"x": 200, "y": 200}},
                    {"type": "chair", "position": {"x": 300, "y": 300}},
                    {"type": "cat", "position": {"x": 400, "y": 400}},
                    {"type": "lamp", "position": {"x": 500, "y": 500}}
                ]
            }
            
            # Act
            result = vision_api.analyze_image("test.jpg")
            
            # Assert
            assert len(result.objects) == 2  # Only chair and lamp
            object_types = [obj.type for obj in result.objects]
            assert "person" not in object_types
            assert "dog" not in object_types
            assert "cat" not in object_types
            assert "chair" in object_types
            assert "lamp" in object_types
    
    def test_analyze_image_identifies_optimal_wall(self):
        """Test identification of optimal wall for artwork placement."""
        # Arrange
        vision_api = VisionAPI("test-key")
        
        with patch.object(vision_api, '_call_vision_api') as mock_call:
            mock_call.return_value = {
                "walls": [
                    {"id": 1, "position": "north", "empty_space": 60, "lighting": 0.7},
                    {"id": 2, "position": "east", "empty_space": 85, "lighting": 0.9},
                    {"id": 3, "position": "south", "empty_space": 40, "lighting": 0.5}
                ]
            }
            
            # Act
            result = vision_api.analyze_image("test.jpg")
            
            # Assert
            assert result.optimal_wall is not None
            assert result.optimal_wall.id == 2  # Highest score (empty space + lighting)
            assert result.optimal_wall.position == "east"
    
    def test_analyze_image_handles_api_errors(self):
        """Test error handling for API failures."""
        # Arrange
        vision_api = VisionAPI("test-key")
        
        with patch.object(vision_api, '_call_vision_api') as mock_call:
            mock_call.side_effect = Exception("API Error")
            
            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                vision_api.analyze_image("test.jpg")
            
            assert "API Error" in str(exc_info.value)
    
    def test_analyze_image_validates_image_path(self):
        """Test that image path is validated before API call."""
        # Arrange
        vision_api = VisionAPI("test-key")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            vision_api.analyze_image("nonexistent.jpg")
    
    def test_spatial_analysis_mapping(self):
        """Test spatial relationship analysis between objects."""
        # Arrange
        vision_api = VisionAPI("test-key")
        
        with patch.object(vision_api, '_call_vision_api') as mock_call:
            mock_call.return_value = {
                "objects": [
                    {"type": "sofa", "position": {"x": 100, "y": 200}, "bbox": [50, 150, 150, 250]},
                    {"type": "coffee_table", "position": {"x": 120, "y": 280}, "bbox": [70, 250, 170, 310]}
                ],
                "spatial_relationships": [
                    {"object1": "sofa", "object2": "coffee_table", "relation": "in_front_of"}
                ]
            }
            
            # Act
            result = vision_api.analyze_image("test.jpg")
            
            # Assert
            assert len(result.spatial_relationships) > 0
            assert result.spatial_relationships[0]["relation"] == "in_front_of"


class TestColorExtractor:
    """Test color extraction functionality."""
    
    def test_color_extractor_initialization(self):
        """Test ColorExtractor initialization."""
        # Act
        extractor = ColorExtractor()
        
        # Assert
        assert extractor is not None
        assert extractor.num_colors == 7  # Default
        assert extractor.color_space == "LAB"  # Default for better perception
    
    def test_extract_colors_from_image(self):
        """Test color extraction from an image."""
        # Arrange
        extractor = ColorExtractor()
        
        # Create a test image with known colors
        test_image = Image.new('RGB', (100, 100))
        pixels = test_image.load()
        # Fill with red, green, blue quadrants
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (255, 0, 0)  # Red
                pixels[i+50, j] = (0, 255, 0)  # Green
                pixels[i, j+50] = (0, 0, 255)  # Blue
                pixels[i+50, j+50] = (255, 255, 255)  # White
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        assert isinstance(palette, ColorPalette)
        assert len(palette.colors) <= extractor.num_colors
        assert len(palette.colors) >= 4  # At least our 4 main colors
        
        # Check that primary colors are detected
        hex_colors = [color.hex for color in palette.colors]
        assert any(self._is_close_to_red(hex_val) for hex_val in hex_colors)
        assert any(self._is_close_to_green(hex_val) for hex_val in hex_colors)
        assert any(self._is_close_to_blue(hex_val) for hex_val in hex_colors)
    
    def test_extract_colors_calculates_percentages(self):
        """Test that color percentages are calculated correctly."""
        # Arrange
        extractor = ColorExtractor()
        
        # Create an image that's 75% blue, 25% white
        test_image = Image.new('RGB', (100, 100), color='blue')
        pixels = test_image.load()
        for i in range(50):
            for j in range(50):
                pixels[i, j] = (255, 255, 255)  # White
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name, num_colors=2)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        percentages = [color.percentage for color in palette.colors]
        assert abs(sum(percentages) - 100.0) < 0.1  # Should sum to ~100%
        
        # Find blue and white colors
        blue_color = next((c for c in palette.colors if self._is_close_to_blue(c.hex)), None)
        white_color = next((c for c in palette.colors if self._is_close_to_white(c.hex)), None)
        
        assert blue_color is not None
        assert white_color is not None
        assert abs(blue_color.percentage - 75.0) < 5.0  # ~75%
        assert abs(white_color.percentage - 25.0) < 5.0  # ~25%
    
    def test_extract_colors_provides_color_names(self):
        """Test that extracted colors have human-readable names."""
        # Arrange
        extractor = ColorExtractor()
        test_image = Image.new('RGB', (50, 50), color='red')
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name, num_colors=1)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        color = palette.colors[0]
        assert color.name is not None
        assert isinstance(color.name, str)
        assert len(color.name) > 0
        assert "red" in color.name.lower() or "crimson" in color.name.lower()
    
    def test_extract_colors_calculates_hsl_values(self):
        """Test that HSL values are calculated for each color."""
        # Arrange
        extractor = ColorExtractor()
        test_image = Image.new('RGB', (50, 50), color='#FF6B6B')  # Coral
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name, num_colors=1)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        color = palette.colors[0]
        assert 0 <= color.hue <= 360
        assert 0 <= color.saturation <= 100
        assert 0 <= color.lightness <= 100
        
        # Coral should have specific HSL characteristics
        assert 0 <= color.hue <= 30 or color.hue >= 330  # Red-ish hue
        assert color.saturation > 50  # Fairly saturated
        assert 40 <= color.lightness <= 70  # Medium lightness
    
    def test_extract_colors_handles_grayscale(self):
        """Test color extraction from grayscale images."""
        # Arrange
        extractor = ColorExtractor()
        test_image = Image.new('L', (50, 50), color=128)  # Gray
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name, num_colors=1)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        color = palette.colors[0]
        assert color.saturation < 10  # Should be nearly desaturated
        assert color.name.lower() in ['gray', 'grey', 'neutral']
    
    def test_extract_colors_error_handling(self):
        """Test error handling for invalid images."""
        # Arrange
        extractor = ColorExtractor()
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            extractor.extract_colors("nonexistent.jpg")
    
    def test_color_clustering_algorithm(self):
        """Test that color clustering produces distinct colors."""
        # Arrange
        extractor = ColorExtractor()
        
        # Create an image with distinct color regions
        test_image = Image.new('RGB', (100, 100))
        pixels = test_image.load()
        
        # Create distinct color blocks
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        block_size = 20
        
        for i, color in enumerate(colors):
            x_start = (i % 5) * block_size
            y_start = (i // 5) * block_size
            for x in range(x_start, x_start + block_size):
                for y in range(y_start, y_start + block_size):
                    if x < 100 and y < 100:
                        pixels[x, y] = color
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            
            # Act
            palette = extractor.extract_colors(f.name, num_colors=5)
            
            # Clean up
            os.unlink(f.name)
        
        # Assert
        assert len(palette.colors) == 5
        
        # Check that colors are distinct (no two colors too similar)
        hex_colors = [c.hex for c in palette.colors]
        for i in range(len(hex_colors)):
            for j in range(i + 1, len(hex_colors)):
                assert self._color_distance(hex_colors[i], hex_colors[j]) > 50
    
    # Helper methods
    def _is_close_to_red(self, hex_color: str) -> bool:
        """Check if a hex color is close to red."""
        r, g, b = self._hex_to_rgb(hex_color)
        return r > 200 and g < 100 and b < 100
    
    def _is_close_to_green(self, hex_color: str) -> bool:
        """Check if a hex color is close to green."""
        r, g, b = self._hex_to_rgb(hex_color)
        return r < 100 and g > 200 and b < 100
    
    def _is_close_to_blue(self, hex_color: str) -> bool:
        """Check if a hex color is close to blue."""
        r, g, b = self._hex_to_rgb(hex_color)
        return r < 100 and g < 100 and b > 200
    
    def _is_close_to_white(self, hex_color: str) -> bool:
        """Check if a hex color is close to white."""
        r, g, b = self._hex_to_rgb(hex_color)
        return r > 200 and g > 200 and b > 200
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _color_distance(self, hex1: str, hex2: str) -> float:
        """Calculate Euclidean distance between two colors."""
        r1, g1, b1 = self._hex_to_rgb(hex1)
        r2, g2, b2 = self._hex_to_rgb(hex2)
        return ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2) ** 0.5


class TestImageProcessingIntegration:
    """Integration tests for image processing pipeline."""
    
    def test_vision_and_color_extraction_pipeline(self):
        """Test integration between vision API and color extraction."""
        # Arrange
        vision_api = VisionAPI("test-key")
        color_extractor = ColorExtractor()
        
        # Create test image
        test_image = Image.new('RGB', (200, 200), color='beige')
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            test_image.save(f.name)
            test_image_path = f.name
        
        with patch.object(vision_api, '_call_vision_api') as mock_vision:
            mock_vision.return_value = {
                "objects": [
                    {"type": "wall", "bbox": [0, 0, 200, 200]}
                ],
                "room_type": "bedroom"
            }
            
            # Act
            vision_result = vision_api.analyze_image(test_image_path)
            color_palette = color_extractor.extract_colors(test_image_path)
            
            # Clean up
            os.unlink(test_image_path)
        
        # Assert
        assert vision_result is not None
        assert color_palette is not None
        assert len(color_palette.colors) > 0
        
        # Beige should be detected
        beige_found = any(
            150 < c.rgb[0] < 255 and 
            100 < c.rgb[1] < 220 and 
            50 < c.rgb[2] < 200 
            for c in color_palette.colors
        ) 