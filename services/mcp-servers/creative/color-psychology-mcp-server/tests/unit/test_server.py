#!/usr/bin/env python3
"""
Unit tests for the MCP server main functions.

Following TDD principles - these tests define the expected behavior
of all MCP tools and resources before implementation.
"""

import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any, List
import tempfile
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import server and related modules
from server import (
    analyze_room, 
    analyze_artwork,
    recommend_artwork,
    generate_composite_image,
    search_color_theory,
    get_color_theory_principles,
    get_artwork_catalog,
    get_configuration,
    health_check
)

# Import generation config to test negative prompts
from image_processing.generation_config import DEFAULT_GENERATION_CONFIG


class TestAnalyzeRoom:
    """Test room analysis functionality."""
    
    def test_analyze_room_with_valid_image(self):
        """Test room analysis with a valid image path."""
        # Arrange
        test_image = "tests/fixtures/test_room.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        assert result["status"] == "success"
        assert "color_palette" in result
        assert "objects" in result
        assert "wall_analysis" in result
        assert "spatial_analysis" in result
        assert isinstance(result["color_palette"], list)
        assert isinstance(result["objects"], list)
    
    def test_analyze_room_extracts_color_palette(self):
        """Test that room analysis extracts dominant colors."""
        # Arrange
        test_image = "tests/fixtures/room_with_colors.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        color_palette = result["color_palette"]
        assert len(color_palette) > 0
        assert all(isinstance(color["hex"], str) for color in color_palette)
        assert all(isinstance(color["percentage"], float) for color in color_palette)
        assert all(color["hex"].startswith("#") for color in color_palette)
        assert abs(sum(color["percentage"] for color in color_palette) - 100.0) < 0.1
    
    def test_analyze_room_identifies_objects(self):
        """Test that room analysis identifies furniture and objects."""
        # Arrange
        test_image = "tests/fixtures/furnished_room.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        objects = result["objects"]
        assert len(objects) > 0
        for obj in objects:
            assert "type" in obj
            assert "position" in obj
            assert "dominant_colors" in obj
            assert isinstance(obj["dominant_colors"], list)
    
    def test_analyze_room_excludes_humans_and_animals(self):
        """Test that humans and animals are excluded from analysis."""
        # Arrange
        test_image = "tests/fixtures/room_with_people.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        objects = result["objects"]
        object_types = [obj["type"] for obj in objects]
        assert "person" not in object_types
        assert "human" not in object_types
        assert "dog" not in object_types
        assert "cat" not in object_types
    
    def test_analyze_room_identifies_optimal_wall(self):
        """Test that analysis identifies the best wall for artwork."""
        # Arrange
        test_image = "tests/fixtures/room_multiple_walls.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        wall_analysis = result["wall_analysis"]
        assert "optimal_wall" in wall_analysis
        assert "position" in wall_analysis["optimal_wall"]
        assert "dimensions" in wall_analysis["optimal_wall"]
        assert "available_space" in wall_analysis["optimal_wall"]
        assert "lighting_score" in wall_analysis["optimal_wall"]
    
    def test_analyze_room_handles_invalid_image(self):
        """Test error handling for invalid image paths."""
        # Arrange
        test_image = "nonexistent/image.jpg"
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        assert result["status"] == "error"
        assert "message" in result
        assert "File not found" in result["message"]
    
    @patch('server.VisionAPI')
    def test_analyze_room_calls_openai_vision_api(self, mock_vision_api):
        """Test that analyze_room properly calls OpenAI Vision API."""
        # Arrange
        test_image = "tests/fixtures/test_room.jpg"
        mock_vision_api.analyze_image.return_value = {
            "objects": [{"type": "sofa", "bbox": [0, 0, 100, 100]}],
            "spatial_info": {"room_type": "living_room"}
        }
        
        # Act
        result = analyze_room(test_image)
        
        # Assert
        mock_vision_api.analyze_image.assert_called_once_with(test_image)


class TestAnalyzeArtwork:
    """Test artwork analysis functionality."""
    
    def test_analyze_artwork_with_valid_id(self):
        """Test artwork analysis with a valid artwork ID."""
        # Arrange
        artwork_id = "vw_abstract_001"
        
        # Act
        result = analyze_artwork(artwork_id)
        
        # Assert
        assert result["status"] == "success"
        assert result["artwork_id"] == artwork_id
        assert "color_composition" in result
        assert "mood_attributes" in result
        assert "psychological_impact" in result
    
    def test_analyze_artwork_extracts_color_composition(self):
        """Test that artwork analysis extracts detailed color information."""
        # Arrange
        artwork_id = "vw_landscape_042"
        
        # Act
        result = analyze_artwork(artwork_id)
        
        # Assert
        color_comp = result["color_composition"]
        assert len(color_comp) > 0
        for color in color_comp:
            assert "hex" in color
            assert "name" in color
            assert "percentage" in color
            assert "hue" in color
            assert "saturation" in color
            assert "lightness" in color
    
    def test_analyze_artwork_determines_mood_attributes(self):
        """Test mood and tone analysis of artwork."""
        # Arrange
        artwork_id = "vw_abstract_calm_005"
        
        # Act
        result = analyze_artwork(artwork_id)
        
        # Assert
        mood_attrs = result["mood_attributes"]
        assert len(mood_attrs) > 0
        assert all(isinstance(attr, str) for attr in mood_attrs)
        # Should include attributes like "calming", "energetic", "warm", etc.
    
    def test_analyze_artwork_evaluates_psychological_impact(self):
        """Test psychological impact analysis."""
        # Arrange
        artwork_id = "vw_modern_017"
        
        # Act
        result = analyze_artwork(artwork_id)
        
        # Assert
        psych_impact = result["psychological_impact"]
        assert "primary_emotions" in psych_impact
        assert "cognitive_effects" in psych_impact
        assert "recommended_spaces" in psych_impact
        assert isinstance(psych_impact["primary_emotions"], list)
    
    def test_analyze_artwork_handles_invalid_id(self):
        """Test error handling for non-existent artwork."""
        # Arrange
        artwork_id = "invalid_artwork_id"
        
        # Act
        result = analyze_artwork(artwork_id)
        
        # Assert
        assert result["status"] == "error"
        assert "message" in result
        assert "not found" in result["message"].lower()
    
    def test_analyze_artwork_caches_results(self):
        """Test that artwork analysis results are cached."""
        # Arrange
        artwork_id = "vw_cached_001"
        
        # Act
        result1 = analyze_artwork(artwork_id)
        result2 = analyze_artwork(artwork_id)
        
        # Assert
        assert result1 == result2
        # Second call should be faster (from cache)


class TestRecommendArtwork:
    """Test artwork recommendation functionality."""
    
    def test_recommend_artwork_returns_specified_number(self):
        """Test that recommendation returns requested number of results."""
        # Arrange
        room_analysis = {
            "color_palette": [
                {"hex": "#E8DCC6", "percentage": 40},
                {"hex": "#8B7355", "percentage": 30},
                {"hex": "#F5F5DC", "percentage": 30}
            ],
            "objects": [{"type": "sofa", "dominant_colors": ["#8B7355"]}]
        }
        num_recommendations = 5
        
        # Act
        results = recommend_artwork(room_analysis, num_recommendations)
        
        # Assert
        assert len(results) == num_recommendations
    
    def test_recommend_artwork_includes_scores(self):
        """Test that recommendations include harmony and psychological scores."""
        # Arrange
        room_analysis = {
            "color_palette": [{"hex": "#4169E1", "percentage": 50}],
            "mood": "modern"
        }
        
        # Act
        results = recommend_artwork(room_analysis, 3)
        
        # Assert
        for rec in results:
            assert "artwork_id" in rec
            assert "color_harmony_score" in rec
            assert "psychological_compatibility_score" in rec
            assert "overall_score" in rec
            assert 0 <= rec["color_harmony_score"] <= 100
            assert 0 <= rec["psychological_compatibility_score"] <= 100
            assert 0 <= rec["overall_score"] <= 100
    
    def test_recommend_artwork_includes_rationale(self):
        """Test that recommendations include explanation for selection."""
        # Arrange
        room_analysis = {"color_palette": [{"hex": "#FF6347", "percentage": 60}]}
        
        # Act
        results = recommend_artwork(room_analysis, 1)
        
        # Assert
        rec = results[0]
        assert "rationale" in rec
        assert "color_analysis" in rec["rationale"]
        assert "psychological_analysis" in rec["rationale"]
        assert isinstance(rec["rationale"]["color_analysis"], str)
    
    def test_recommend_artwork_considers_color_harmony(self):
        """Test that recommendations properly score color harmony."""
        # Arrange
        # Room with blue dominant colors
        room_analysis = {
            "color_palette": [
                {"hex": "#0000FF", "percentage": 70},  # Blue
                {"hex": "#FFFFFF", "percentage": 30}   # White
            ]
        }
        
        # Act
        results = recommend_artwork(room_analysis, 10)
        
        # Assert
        # Artworks with complementary colors (orange) should score higher
        # than those with clashing colors
        top_result = results[0]
        assert top_result["color_harmony_score"] > 70
    
    def test_recommend_artwork_includes_composite_preview(self):
        """Test that recommendations include preview images."""
        # Arrange
        room_analysis = {"color_palette": [{"hex": "#228B22", "percentage": 50}]}
        
        # Act
        results = recommend_artwork(room_analysis, 1)
        
        # Assert
        rec = results[0]
        assert "composite_preview_url" in rec
        assert rec["composite_preview_url"].startswith("http")
    
    def test_recommend_artwork_handles_empty_room_analysis(self):
        """Test graceful handling of minimal room data."""
        # Arrange
        room_analysis = {}
        
        # Act
        results = recommend_artwork(room_analysis, 3)
        
        # Assert
        assert len(results) == 3
        # Should still return recommendations based on general appeal


class TestGenerateCompositeImage:
    """Test composite image generation functionality."""
    
    def test_generate_composite_creates_image(self):
        """Test that composite generation creates an image file."""
        # Arrange
        room_image = "tests/fixtures/empty_room.jpg"
        artwork_id = "vw_abstract_001"
        wall_position = {
            "x": 100,
            "y": 50,
            "width": 200,
            "height": 150,
            "rotation": 0
        }
        
        # Act
        result = generate_composite_image(room_image, artwork_id, wall_position)
        
        # Assert
        assert result["status"] == "success"
        assert "composite_image_path" in result
        assert os.path.exists(result["composite_image_path"])
    
    def test_generate_composite_preserves_artwork_accuracy(self):
        """Test that artwork is accurately represented in composite."""
        # Arrange
        room_image = "tests/fixtures/room.jpg"
        artwork_id = "vw_detailed_pattern_001"
        wall_position = {"x": 200, "y": 100, "width": 300, "height": 200}
        
        # Act
        result = generate_composite_image(room_image, artwork_id, wall_position)
        
        # Assert
        assert result["status"] == "success"
        assert "generation_metadata" in result
        assert result["generation_metadata"]["artwork_preserved"] == True
        assert result["generation_metadata"]["quality_score"] > 0.9
    
    def test_generate_composite_respects_positioning(self):
        """Test that artwork is placed at specified position."""
        # Arrange
        room_image = "tests/fixtures/room.jpg"
        artwork_id = "vw_landscape_001"
        wall_position = {
            "x": 150,
            "y": 75,
            "width": 250,
            "height": 167,  # 3:2 aspect ratio
            "rotation": 0
        }
        
        # Act
        result = generate_composite_image(room_image, artwork_id, wall_position)
        
        # Assert
        metadata = result["generation_metadata"]
        assert metadata["actual_position"]["x"] == wall_position["x"]
        assert metadata["actual_position"]["y"] == wall_position["y"]
    
    @patch('server.openai.images.generate')
    def test_generate_composite_uses_openai_api(self, mock_generate):
        """Test that OpenAI Image Generation API is properly called."""
        # Arrange
        room_image = "tests/fixtures/room.jpg"
        artwork_id = "vw_test_001"
        wall_position = {"x": 100, "y": 100, "width": 200, "height": 200}
        
        mock_generate.return_value = MagicMock(
            data=[MagicMock(url="https://generated-image.png")]
        )
        
        # Act
        result = generate_composite_image(room_image, artwork_id, wall_position)
        
        # Assert
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert "model" in call_args.kwargs
        assert call_args.kwargs["model"] == "dall-e-3"
    
    def test_generate_composite_handles_errors(self):
        """Test error handling in composite generation."""
        # Arrange
        room_image = "invalid_path.jpg"
        artwork_id = "vw_001"
        wall_position = {"x": 0, "y": 0, "width": 100, "height": 100}
        
        # Act
        result = generate_composite_image(room_image, artwork_id, wall_position)
        
        # Assert
        assert result["status"] == "error"
        assert "message" in result
    
    def test_generate_composite_enforces_no_humans_animals_rule(self):
        """Test that NO HUMANS OR ANIMALS rule is enforced in prompts."""
        # Arrange
        room_image = "tests/fixtures/room.jpg"
        artwork_id = "vw_test_001"
        wall_position = {"x": 100, "y": 100, "width": 200, "height": 200}
        
        # Act - Get the generation prompt
        from image_processing.generation_config import DEFAULT_GENERATION_CONFIG
        prompt = DEFAULT_GENERATION_CONFIG.build_prompt(
            "Modern living room with beige walls",
            "Abstract blue and gold artwork",
            wall_position
        )
        
        # Assert - Verify negative prompts are included
        assert "NO humans" in prompt
        assert "NO people" in prompt
        assert "NO animals" in prompt
        assert "NO pets" in prompt
        assert "empty room only" in prompt
        assert "furniture and decor only" in prompt
        assert "CRITICAL REQUIREMENTS" in prompt
    
    def test_generation_config_validates_requests(self):
        """Test that generation requests are validated for forbidden content."""
        # Arrange
        from image_processing.generation_config import DEFAULT_GENERATION_CONFIG
        
        # Test valid request
        valid_request = {
            "room": "living room with sofa",
            "artwork": "abstract painting"
        }
        
        # Test invalid requests
        invalid_requests = [
            {"room": "living room with person sitting"},
            {"room": "bedroom with dog on bed"},
            {"description": "add a woman looking at the artwork"},
            {"details": "include a cat on the sofa"}
        ]
        
        # Act & Assert - Valid request should pass
        assert DEFAULT_GENERATION_CONFIG.validate_generation_request(valid_request) == True
        
        # Invalid requests should raise exceptions
        for invalid_req in invalid_requests:
            with pytest.raises(ValueError) as exc_info:
                DEFAULT_GENERATION_CONFIG.validate_generation_request(invalid_req)
            assert "cannot contain references to" in str(exc_info.value)
    
    def test_negative_prompts_comprehensive_coverage(self):
        """Test that negative prompts cover all variations of humans/animals."""
        # Arrange
        config = DEFAULT_GENERATION_CONFIG
        
        # Assert - Check comprehensive coverage
        negative_terms = " ".join(config.negative_prompts).lower()
        
        # Human-related terms
        assert "human" in negative_terms
        assert "people" in negative_terms
        assert "person" in negative_terms
        assert "faces" in negative_terms
        assert "hands" in negative_terms
        assert "body parts" in negative_terms
        
        # Animal-related terms
        assert "animals" in negative_terms
        assert "pets" in negative_terms
        assert "dogs" in negative_terms
        assert "cats" in negative_terms
        assert "birds" in negative_terms
        assert "living creatures" in negative_terms
        
        # Ensure we specify what we want instead
        assert "empty room only" in negative_terms
        assert "furniture and decor only" in negative_terms
        assert "architectural interior only" in negative_terms


class TestSearchColorTheory:
    """Test color theory knowledge base search."""
    
    def test_search_returns_relevant_results(self):
        """Test that search returns relevant color theory information."""
        # Arrange
        query = "complementary colors"
        
        # Act
        results = search_color_theory(query, top_k=5)
        
        # Assert
        assert len(results) <= 5
        assert all("text" in result for result in results)
        assert all("score" in result for result in results)
        assert all(result["score"] > 0 for result in results)
    
    def test_search_ranks_by_relevance(self):
        """Test that results are ordered by relevance score."""
        # Arrange
        query = "color harmony principles"
        
        # Act
        results = search_color_theory(query, top_k=10)
        
        # Assert
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_search_includes_context(self):
        """Test that search results include surrounding context."""
        # Arrange
        query = "warm colors psychology"
        
        # Act
        results = search_color_theory(query, top_k=3)
        
        # Assert
        for result in results:
            assert "text" in result
            assert "context" in result
            assert len(result["context"]) > len(result["text"])
    
    def test_search_handles_empty_query(self):
        """Test handling of empty search queries."""
        # Arrange
        query = ""
        
        # Act
        results = search_color_theory(query)
        
        # Assert
        assert isinstance(results, list)
        assert len(results) == 0


class TestMCPResources:
    """Test MCP resource endpoints."""
    
    def test_get_color_theory_principles(self):
        """Test color theory principles resource."""
        # Act
        principles = get_color_theory_principles()
        
        # Assert
        assert isinstance(principles, str)
        assert len(principles) > 0
        assert "color" in principles.lower()
    
    def test_get_artwork_catalog(self):
        """Test artwork catalog resource."""
        # Act
        catalog = get_artwork_catalog()
        
        # Assert
        assert isinstance(catalog, list)
        assert len(catalog) > 0
        for artwork in catalog:
            assert "id" in artwork
            assert "title" in artwork
            assert "artist" in artwork
            assert "dimensions" in artwork
            assert "tags" in artwork
            assert "image_url" in artwork
    
    def test_get_configuration(self):
        """Test configuration resource."""
        # Act
        config = get_configuration()
        
        # Assert
        assert isinstance(config, dict)
        assert "version" in config
        assert "openai_model" in config
        assert "image_generation_model" in config
        assert "vector_db" in config
        assert config["openai_model"] == "gpt-4o"


class TestHealthCheck:
    """Test health check functionality."""
    
    def test_health_check_returns_status(self):
        """Test that health check returns proper status."""
        # Act
        result = health_check()
        
        # Assert
        assert "status" in result
        assert result["status"] in ["healthy", "degraded", "unhealthy"]
        assert "version" in result
        assert "services" in result
    
    def test_health_check_validates_services(self):
        """Test that health check validates all service dependencies."""
        # Act
        result = health_check()
        
        # Assert
        services = result["services"]
        assert "database" in services
        assert "openai_api" in services
        assert "image_storage" in services
        assert all(status in ["connected", "available", "ready", "error"] 
                  for status in services.values())
    
    @patch('server.test_database_connection')
    def test_health_check_handles_service_failures(self, mock_db_test):
        """Test health check when services are down."""
        # Arrange
        mock_db_test.side_effect = Exception("Connection failed")
        
        # Act
        result = health_check()
        
        # Assert
        assert result["status"] in ["degraded", "unhealthy"]
        assert result["services"]["database"] == "error"


# Integration test fixtures
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    with patch('server.openai.Client') as mock:
        yield mock


@pytest.fixture
def test_room_image():
    """Create a test room image."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a simple test image
        from PIL import Image
        img = Image.new('RGB', (800, 600), color='beige')
        img.save(f.name)
        yield f.name
        os.unlink(f.name)


@pytest.fixture
def test_database():
    """Set up test database with pgvector."""
    # This would set up a test database in real implementation
    yield MagicMock() 