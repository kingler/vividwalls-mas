#!/usr/bin/env python3
"""
Safety tests for image generation to ensure NO HUMANS OR ANIMALS rule is enforced.

These tests verify that the generation configuration properly prevents
any humans or animals from appearing in generated images.
"""

import pytest
import sys
import os
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_processing.generation_config import (
    ImageGenerationConfig,
    STRICT_GENERATION_CONFIG,
    get_safe_generation_prompt
)


class TestGenerationSafetyRules:
    """Test suite for NO HUMANS OR ANIMALS enforcement."""
    
    def test_negative_prompts_comprehensive(self):
        """Test that negative prompts cover all necessary exclusions."""
        config = STRICT_GENERATION_CONFIG
        negative_text = " ".join(config.negative_prompts).lower()
        
        # Human-related terms that must be excluded
        human_terms = [
            "human", "people", "person", "faces", "hands", 
            "body parts", "figures", "silhouettes"
        ]
        
        # Animal-related terms that must be excluded
        animal_terms = [
            "animals", "pets", "dogs", "cats", "birds", 
            "fish", "insects", "creatures"
        ]
        
        # Verify all terms are covered
        for term in human_terms:
            assert term in negative_text, f"Missing human exclusion: {term}"
            
        for term in animal_terms:
            assert term in negative_text, f"Missing animal exclusion: {term}"
    
    def test_validate_clean_requests(self):
        """Test that clean requests pass validation."""
        config = STRICT_GENERATION_CONFIG
        
        clean_requests = [
            {"room": "modern living room with sofa and table"},
            {"artwork": "abstract painting with blue and gold"},
            {"description": "minimalist bedroom with white walls"},
            {"details": "empty office space with desk and chair"}
        ]
        
        for request in clean_requests:
            assert config.validate_generation_request(request) == True
    
    def test_validate_rejects_human_references(self):
        """Test that requests with human references are rejected."""
        config = STRICT_GENERATION_CONFIG
        
        human_requests = [
            {"room": "living room with person sitting on sofa"},
            {"room": "bedroom with woman standing by window"},
            {"description": "add a man looking at the artwork"},
            {"details": "include children playing in the room"},
            {"scene": "customer admiring the artwork"},
            {"note": "show the homeowner in the space"}
        ]
        
        for request in human_requests:
            with pytest.raises(ValueError) as exc_info:
                config.validate_generation_request(request)
            assert "REJECTED" in str(exc_info.value)
            assert "humans or animals" in str(exc_info.value)
    
    def test_validate_rejects_animal_references(self):
        """Test that requests with animal references are rejected."""
        config = STRICT_GENERATION_CONFIG
        
        animal_requests = [
            {"room": "living room with dog on couch"},
            {"room": "bedroom with cat on bed"},
            {"description": "add a pet bird in cage"},
            {"details": "include fish tank with fish"},
            {"scene": "hamster cage on the shelf"},
            {"note": "spider in the corner"}
        ]
        
        for request in animal_requests:
            with pytest.raises(ValueError) as exc_info:
                config.validate_generation_request(request)
            assert "REJECTED" in str(exc_info.value)
            assert "humans or animals" in str(exc_info.value)
    
    def test_validate_allows_negated_references(self):
        """Test that negated references (no humans, without animals) are allowed."""
        config = STRICT_GENERATION_CONFIG
        
        negated_requests = [
            {"room": "living room with no people"},
            {"room": "bedroom without any animals"},
            {"description": "empty of humans"},
            {"details": "devoid of pets"}
        ]
        
        for request in negated_requests:
            assert config.validate_generation_request(request) == True
    
    def test_build_prompt_includes_all_safety_elements(self):
        """Test that generated prompts include all safety elements."""
        config = STRICT_GENERATION_CONFIG
        
        prompt = config.build_prompt(
            room_description="Modern living room",
            artwork_description="Abstract painting",
            wall_position={"description": "above sofa"}
        )
        
        # Check for critical sections
        assert "🚫 ABSOLUTELY CRITICAL RULES" in prompt
        assert "❌ NO humans whatsoever" in prompt
        assert "❌ NO animals of any kind" in prompt
        assert "⚠️ FINAL REMINDER" in prompt
        assert "COMPLETELY EMPTY of any humans, animals" in prompt
        
        # Check structure markers
        assert "━" * 50 in prompt
        assert "✅ REQUIRED ELEMENTS" in prompt
        assert "🎨 ARTWORK INTEGRATION" in prompt
    
    def test_post_generation_check_validates_prompts(self):
        """Test that post-generation check validates prompts correctly."""
        config = STRICT_GENERATION_CONFIG
        
        # Valid prompt with all required phrases
        valid_prompt = """
        Generate a room with NO humans and NO animals.
        The space must be empty of life and completely uninhabited.
        """
        assert config.post_generation_check(valid_prompt) == True
        
        # Invalid prompt missing required phrases
        invalid_prompt = "Generate a beautiful room with artwork"
        assert config.post_generation_check(invalid_prompt) == False
    
    def test_get_safe_generation_prompt_full_flow(self):
        """Test the complete safe generation flow."""
        # Test with clean inputs
        prompt = get_safe_generation_prompt(
            room_desc="Minimalist living room with beige walls",
            artwork_desc="Abstract blue canvas, 30x40 inches",
            wall_pos={"description": "centered on main wall"}
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 500  # Should be comprehensive
        assert "NO humans" in prompt
        assert "NO animals" in prompt
        
        # Test with forbidden inputs
        with pytest.raises(ValueError):
            get_safe_generation_prompt(
                room_desc="Living room with dog sleeping",
                artwork_desc="Nature painting",
                wall_pos={"description": "above fireplace"}
            )
    
    def test_config_singleton_consistency(self):
        """Test that the singleton config is consistently applied."""
        config1 = STRICT_GENERATION_CONFIG
        config2 = STRICT_GENERATION_CONFIG
        
        assert config1 is config2
        assert len(config1.negative_prompts) == len(config2.negative_prompts)
        assert config1.negative_prompts == config2.negative_prompts
    
    def test_edge_cases_and_variations(self):
        """Test edge cases and variations of forbidden terms."""
        config = STRICT_GENERATION_CONFIG
        
        # Test plural/singular variations
        edge_cases = [
            {"text": "multiple persons in room"},
            {"text": "a human figure"},
            {"text": "pet's bed"},
            {"text": "animal shelter"},
            {"text": "people's furniture"},
            {"text": "man's office"},
            {"text": "woman's bedroom"}
        ]
        
        for case in edge_cases:
            with pytest.raises(ValueError):
                config.validate_generation_request(case)


class TestPromptExamples:
    """Test actual prompt generation examples."""
    
    def test_living_room_prompt(self):
        """Test prompt generation for a living room."""
        prompt = get_safe_generation_prompt(
            room_desc="Contemporary living room with gray sectional sofa, marble coffee table, floor-to-ceiling windows",
            artwork_desc="Large abstract canvas with navy blue and gold accents, 48x36 inches, black frame",
            wall_pos={"description": "centered above the sectional sofa at eye level"}
        )
        
        # Verify content
        assert "Contemporary living room" in prompt
        assert "NO humans whatsoever" in prompt
        assert "NO pets whatsoever" in prompt
        assert "professional gallery-style presentation" in prompt
    
    def test_bedroom_prompt(self):
        """Test prompt generation for a bedroom."""
        prompt = get_safe_generation_prompt(
            room_desc="Serene master bedroom with upholstered headboard, neutral tones, soft lighting",
            artwork_desc="Set of three botanical prints in white frames, each 16x20 inches",
            wall_pos={"description": "arranged horizontally above the headboard"}
        )
        
        # Verify content
        assert "Serene master bedroom" in prompt
        assert "ABSOLUTELY empty of life" in prompt
        assert "ONLY furniture and decor" in prompt
        assert "botanical prints" in prompt
    
    def test_office_prompt(self):
        """Test prompt generation for an office."""
        prompt = get_safe_generation_prompt(
            room_desc="Modern home office with standing desk, ergonomic chair, built-in shelving",
            artwork_desc="Minimalist black and white photography print, 24x24 inches, thin metal frame",
            wall_pos={"description": "on the wall behind the desk at seated eye level"},
            custom="Ensure the artwork is visible from the desk position"
        )
        
        # Verify custom instructions included
        assert "Modern home office" in prompt
        assert "Ensure the artwork is visible" in prompt
        assert "COMPLETELY uninhabited" in prompt


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 