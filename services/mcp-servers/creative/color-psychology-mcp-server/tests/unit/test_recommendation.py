#!/usr/bin/env python3
"""
Unit tests for recommendation engine modules.

Following TDD principles - these tests define expected behavior
for color harmony scoring and psychological analysis functionality.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import List, Dict, Any
import math

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import modules to be tested
from recommendation.color_harmony import (
    ColorHarmonyScorer, 
    HarmonyType,
    ColorScheme,
    HarmonyScore
)
from recommendation.psychological_analysis import (
    PsychologicalAnalyzer,
    EmotionalProfile,
    SpaceCompatibility,
    PsychologicalScore
)


class TestColorHarmonyScorer:
    """Test color harmony scoring functionality."""
    
    def test_scorer_initialization(self):
        """Test ColorHarmonyScorer initialization."""
        # Act
        scorer = ColorHarmonyScorer()
        
        # Assert
        assert scorer is not None
        assert hasattr(scorer, 'harmony_weights')
        assert len(scorer.harmony_weights) > 0
    
    def test_score_complementary_colors(self):
        """Test scoring of complementary color harmony."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#FF0000"]  # Red
        artwork_colors = ["#00FF00"]  # Green (roughly complementary)
        
        # Act
        score = scorer.calculate_harmony_score(
            room_colors, 
            artwork_colors,
            harmony_type=HarmonyType.COMPLEMENTARY
        )
        
        # Assert
        assert isinstance(score, HarmonyScore)
        assert score.overall_score > 70  # Should score high for complementary
        assert score.harmony_type == HarmonyType.COMPLEMENTARY
        assert "complementary" in score.explanation.lower()
    
    def test_score_analogous_colors(self):
        """Test scoring of analogous color harmony."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#FF0000"]  # Red
        artwork_colors = ["#FF8800", "#FF0088"]  # Orange and red-purple
        
        # Act
        score = scorer.calculate_harmony_score(
            room_colors,
            artwork_colors,
            harmony_type=HarmonyType.ANALOGOUS
        )
        
        # Assert
        assert score.overall_score > 60  # Should score well for analogous
        assert score.harmony_type == HarmonyType.ANALOGOUS
        assert "analogous" in score.explanation.lower()
    
    def test_score_triadic_colors(self):
        """Test scoring of triadic color harmony."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#FF0000"]  # Red (0°)
        artwork_colors = ["#00FF00", "#0000FF"]  # Green (120°), Blue (240°)
        
        # Act
        score = scorer.calculate_harmony_score(
            room_colors,
            artwork_colors,
            harmony_type=HarmonyType.TRIADIC
        )
        
        # Assert
        assert score.overall_score > 65  # Should score well for triadic
        assert score.harmony_type == HarmonyType.TRIADIC
        assert score.color_relationships is not None
    
    def test_score_monochromatic_scheme(self):
        """Test scoring of monochromatic color scheme."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#404040", "#808080"]  # Gray shades
        artwork_colors = ["#606060", "#A0A0A0", "#303030"]  # More gray shades
        
        # Act
        score = scorer.calculate_harmony_score(
            room_colors,
            artwork_colors,
            harmony_type=HarmonyType.MONOCHROMATIC
        )
        
        # Assert
        assert score.overall_score > 75  # Should score high for monochromatic
        assert score.harmony_type == HarmonyType.MONOCHROMATIC
        assert "monochromatic" in score.explanation.lower()
    
    def test_score_clashing_colors(self):
        """Test that clashing colors receive low scores."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#FF0000", "#00FF00"]  # Red and green
        artwork_colors = ["#FF00FF", "#FFFF00"]  # Magenta and yellow
        
        # Act
        score = scorer.calculate_harmony_score(room_colors, artwork_colors)
        
        # Assert
        assert score.overall_score < 40  # Should score low for clashing
        assert "clash" in score.explanation.lower() or "contrast" in score.explanation.lower()
    
    def test_auto_detect_harmony_type(self):
        """Test automatic detection of harmony type."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#FF0000"]  # Red
        artwork_colors = ["#00FFFF"]  # Cyan (complementary)
        
        # Act
        score = scorer.calculate_harmony_score(
            room_colors,
            artwork_colors
            # No harmony_type specified - should auto-detect
        )
        
        # Assert
        assert score.detected_harmony_type == HarmonyType.COMPLEMENTARY
        assert score.overall_score > 70
    
    def test_color_temperature_compatibility(self):
        """Test color temperature compatibility scoring."""
        # Arrange
        scorer = ColorHarmonyScorer()
        warm_room = ["#FF6B6B", "#FFE66D"]  # Warm colors
        warm_artwork = ["#FF8E53", "#FFA23A"]  # Warm colors
        cool_artwork = ["#4ECDC4", "#44A1A0"]  # Cool colors
        
        # Act
        warm_score = scorer.calculate_harmony_score(warm_room, warm_artwork)
        cool_score = scorer.calculate_harmony_score(warm_room, cool_artwork)
        
        # Assert
        assert warm_score.temperature_compatibility > cool_score.temperature_compatibility
        assert warm_score.overall_score > cool_score.overall_score
    
    def test_saturation_balance_scoring(self):
        """Test saturation balance between room and artwork."""
        # Arrange
        scorer = ColorHarmonyScorer()
        muted_room = ["#A8A8A8", "#C0C0C0"]  # Low saturation
        muted_artwork = ["#B0B0B0", "#989898"]  # Low saturation
        vibrant_artwork = ["#FF0000", "#00FF00"]  # High saturation
        
        # Act
        balanced_score = scorer.calculate_harmony_score(muted_room, muted_artwork)
        unbalanced_score = scorer.calculate_harmony_score(muted_room, vibrant_artwork)
        
        # Assert
        assert balanced_score.saturation_balance > unbalanced_score.saturation_balance
        assert balanced_score.overall_score > unbalanced_score.overall_score
    
    def test_get_color_scheme_recommendations(self):
        """Test generation of color scheme recommendations."""
        # Arrange
        scorer = ColorHarmonyScorer()
        room_colors = ["#2E86AB", "#A23B72"]  # Blue and purple
        
        # Act
        recommendations = scorer.get_color_scheme_recommendations(room_colors)
        
        # Assert
        assert len(recommendations) > 0
        assert all(isinstance(r, ColorScheme) for r in recommendations)
        assert recommendations[0].score > recommendations[-1].score  # Sorted by score
        
        # Check that different harmony types are represented
        harmony_types = {r.harmony_type for r in recommendations}
        assert len(harmony_types) >= 3


class TestPsychologicalAnalyzer:
    """Test psychological analysis functionality."""
    
    def test_analyzer_initialization(self):
        """Test PsychologicalAnalyzer initialization."""
        # Act
        analyzer = PsychologicalAnalyzer()
        
        # Assert
        assert analyzer is not None
        assert hasattr(analyzer, 'color_emotions')
        assert hasattr(analyzer, 'space_profiles')
    
    def test_analyze_color_emotions(self):
        """Test emotional analysis of colors."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        warm_colors = ["#FF6B6B", "#FFD93D"]  # Red-orange, yellow
        cool_colors = ["#6BCB77", "#4D96FF"]  # Green, blue
        
        # Act
        warm_profile = analyzer.analyze_color_emotions(warm_colors)
        cool_profile = analyzer.analyze_color_emotions(cool_colors)
        
        # Assert
        assert isinstance(warm_profile, EmotionalProfile)
        assert isinstance(cool_profile, EmotionalProfile)
        
        # Warm colors should evoke energy, excitement
        assert "energetic" in warm_profile.primary_emotions or "exciting" in warm_profile.primary_emotions
        assert warm_profile.energy_level > 0.7
        
        # Cool colors should evoke calm, relaxation
        assert "calm" in cool_profile.primary_emotions or "peaceful" in cool_profile.primary_emotions
        assert cool_profile.energy_level < 0.5
    
    def test_analyze_space_compatibility(self):
        """Test compatibility analysis for different spaces."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        calming_artwork = {
            "colors": ["#E3F2FD", "#90CAF9", "#42A5F5"],  # Light blues
            "mood": "serene"
        }
        energetic_artwork = {
            "colors": ["#FF5252", "#FF9800", "#FFEB3B"],  # Red, orange, yellow
            "mood": "vibrant"
        }
        
        # Act
        bedroom_calm = analyzer.analyze_space_compatibility(calming_artwork, "bedroom")
        bedroom_energy = analyzer.analyze_space_compatibility(energetic_artwork, "bedroom")
        office_calm = analyzer.analyze_space_compatibility(calming_artwork, "office")
        office_energy = analyzer.analyze_space_compatibility(energetic_artwork, "office")
        
        # Assert
        assert isinstance(bedroom_calm, SpaceCompatibility)
        
        # Calming artwork should score higher for bedroom
        assert bedroom_calm.compatibility_score > bedroom_energy.compatibility_score
        
        # Energetic artwork might work better in office
        assert office_energy.compatibility_score > bedroom_energy.compatibility_score
        
        # Check recommendations
        assert len(bedroom_calm.recommendations) > 0
        assert any("sleep" in r.lower() or "relax" in r.lower() for r in bedroom_calm.recommendations)
    
    def test_psychological_scoring(self):
        """Test overall psychological compatibility scoring."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        room_data = {
            "space_type": "living_room",
            "existing_mood": "neutral",
            "lighting": "bright",
            "size": "large"
        }
        
        artwork1 = {
            "emotional_profile": EmotionalProfile(
                primary_emotions=["joyful", "energetic"],
                energy_level=0.8,
                complexity=0.6,
                warmth=0.9
            ),
            "colors": ["#FFC107", "#FF5722"]
        }
        
        artwork2 = {
            "emotional_profile": EmotionalProfile(
                primary_emotions=["melancholic", "contemplative"],
                energy_level=0.2,
                complexity=0.8,
                warmth=0.3
            ),
            "colors": ["#37474F", "#455A64"]
        }
        
        # Act
        score1 = analyzer.calculate_psychological_score(room_data, artwork1)
        score2 = analyzer.calculate_psychological_score(room_data, artwork2)
        
        # Assert
        assert isinstance(score1, PsychologicalScore)
        assert isinstance(score2, PsychologicalScore)
        
        # Living room should prefer more energetic artwork
        assert score1.overall_score > score2.overall_score
        assert score1.mood_enhancement > score2.mood_enhancement
    
    def test_cognitive_load_analysis(self):
        """Test cognitive load assessment of artwork."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        
        simple_artwork = {
            "colors": ["#FFFFFF", "#000000"],  # Just black and white
            "pattern_complexity": 0.2
        }
        
        complex_artwork = {
            "colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"],
            "pattern_complexity": 0.9
        }
        
        # Act
        simple_load = analyzer.assess_cognitive_load(simple_artwork)
        complex_load = analyzer.assess_cognitive_load(complex_artwork)
        
        # Assert
        assert simple_load < complex_load
        assert simple_load < 0.3  # Low cognitive load
        assert complex_load > 0.7  # High cognitive load
    
    def test_therapeutic_value_assessment(self):
        """Test assessment of therapeutic value."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        
        nature_artwork = {
            "colors": ["#228B22", "#87CEEB", "#F4A460"],  # Forest green, sky blue, sandy
            "subject": "landscape",
            "mood": "peaceful"
        }
        
        abstract_artwork = {
            "colors": ["#FF1744", "#F50057", "#D500F9"],  # Intense colors
            "subject": "abstract",
            "mood": "chaotic"
        }
        
        # Act
        nature_value = analyzer.assess_therapeutic_value(nature_artwork)
        abstract_value = analyzer.assess_therapeutic_value(abstract_artwork)
        
        # Assert
        assert nature_value.stress_reduction > abstract_value.stress_reduction
        assert nature_value.mood_improvement > abstract_value.mood_improvement
        assert "biophilic" in nature_value.therapeutic_elements
    
    def test_cultural_sensitivity_check(self):
        """Test cultural sensitivity analysis."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        
        # Red has different meanings in different cultures
        red_artwork = {
            "colors": ["#FF0000", "#DC143C"],
            "dominant_color": "red",
            "subject": "abstract"
        }
        
        # Act
        western_context = analyzer.check_cultural_sensitivity(red_artwork, "western")
        eastern_context = analyzer.check_cultural_sensitivity(red_artwork, "eastern")
        
        # Assert
        assert western_context.considerations != eastern_context.considerations
        assert any("luck" in c.lower() or "prosperity" in c.lower() 
                  for c in eastern_context.considerations)
    
    def test_circadian_rhythm_compatibility(self):
        """Test artwork compatibility with circadian rhythms."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        
        cool_blue_artwork = {
            "colors": ["#1E88E5", "#0D47A1"],
            "brightness": 0.3
        }
        
        warm_orange_artwork = {
            "colors": ["#FF6F00", "#FFB300"],
            "brightness": 0.8
        }
        
        # Act
        bedroom_evening_cool = analyzer.check_circadian_compatibility(
            cool_blue_artwork, "bedroom", "evening"
        )
        bedroom_evening_warm = analyzer.check_circadian_compatibility(
            warm_orange_artwork, "bedroom", "evening"
        )
        
        # Assert
        assert bedroom_evening_cool.compatibility > bedroom_evening_warm.compatibility
        assert "melatonin" in bedroom_evening_cool.explanation.lower()
    
    def test_personal_preference_learning(self):
        """Test learning from user preferences."""
        # Arrange
        analyzer = PsychologicalAnalyzer()
        
        user_preferences = {
            "liked_artworks": [
                {"colors": ["#4CAF50", "#8BC34A"], "mood": "natural"},
                {"colors": ["#03A9F4", "#00BCD4"], "mood": "serene"}
            ],
            "disliked_artworks": [
                {"colors": ["#F44336", "#E91E63"], "mood": "intense"}
            ]
        }
        
        # Act
        preference_profile = analyzer.learn_user_preferences(user_preferences)
        
        # Assert
        assert preference_profile.preferred_moods == ["natural", "serene"]
        assert preference_profile.avoided_moods == ["intense"]
        assert preference_profile.color_temperature_preference == "cool"


class TestRecommendationIntegration:
    """Integration tests for recommendation system."""
    
    def test_harmony_and_psychology_integration(self):
        """Test integration of color harmony and psychological scoring."""
        # Arrange
        harmony_scorer = ColorHarmonyScorer()
        psych_analyzer = PsychologicalAnalyzer()
        
        room_data = {
            "colors": ["#E1F5FE", "#81D4FA"],  # Light blues
            "space_type": "bedroom",
            "mood": "relaxing"
        }
        
        artwork_data = {
            "colors": ["#B3E5FC", "#4FC3F7"],  # Harmonious blues
            "mood": "serene",
            "subject": "seascape"
        }
        
        # Act
        harmony_score = harmony_scorer.calculate_harmony_score(
            room_data["colors"],
            artwork_data["colors"]
        )
        
        psych_score = psych_analyzer.calculate_psychological_score(
            room_data,
            artwork_data
        )
        
        # Calculate combined score
        combined_score = (harmony_score.overall_score * 0.6 + 
                         psych_score.overall_score * 0.4)
        
        # Assert
        assert harmony_score.overall_score > 70
        assert psych_score.overall_score > 75
        assert combined_score > 72
        
        # Both should support the recommendation
        assert "harmonious" in harmony_score.explanation.lower()
        assert "relaxing" in psych_score.rationale.lower() or "calming" in psych_score.rationale.lower() 