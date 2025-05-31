#!/usr/bin/env python3
"""
Unit tests for semantic search functionality.

Tests the vector-based search capabilities for color theory knowledge
and artwork matching following TDD principles.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.search import (
    ColorTheorySearch,
    ArtworkSearch,
    CachedColorHarmonySearch,
    quick_color_theory_search
)
from data.models import (
    ColorTheoryKnowledge,
    Artwork,
    ColorHarmonyCache,
    AnalysisStatus
)


class TestColorTheorySearch:
    """Test color theory semantic search functionality."""
    
    @patch('data.search.get_database')
    def test_init(self, mock_get_db):
        """Test search initialization."""
        mock_client = MagicMock()
        search = ColorTheorySearch(mock_client)
        
        assert search.client == mock_client
        assert search.embedding_model == "text-embedding-3-small"
        mock_get_db.assert_called_once()
    
    def test_generate_query_embedding(self):
        """Test query embedding generation."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        
        with patch('data.search.get_database'):
            search = ColorTheorySearch(mock_client)
            embedding = search.generate_query_embedding("test query")
        
        assert embedding == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input="test query"
        )
    
    @patch('data.search.get_database')
    def test_search_color_theory(self, mock_get_db):
        """Test semantic search for color theory."""
        # Mock database and session
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock query results
        mock_knowledge = MagicMock(spec=ColorTheoryKnowledge)
        mock_knowledge.id = uuid4()
        mock_knowledge.title = "Color Harmony"
        mock_knowledge.content = "Test content"
        mock_knowledge.category = "harmony"
        mock_knowledge.keywords = ["complementary", "harmony"]
        mock_knowledge.source = "color-theory.md"
        
        mock_result = [(mock_knowledge, 0.85)]
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        
        # Perform search
        search = ColorTheorySearch(mock_client)
        results = search.search_color_theory("color harmony", limit=5)
        
        # Verify results
        assert len(results) == 1
        assert results[0]['title'] == "Color Harmony"
        assert results[0]['category'] == "harmony"
        assert results[0]['similarity_score'] == 0.85
        assert results[0]['keywords'] == ["complementary", "harmony"]
    
    @patch('data.search.get_database')
    def test_search_by_keywords(self, mock_get_db):
        """Test keyword-based search."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock results
        mock_knowledge = MagicMock(spec=ColorTheoryKnowledge)
        mock_knowledge.id = uuid4()
        mock_knowledge.title = "Complementary Colors"
        mock_knowledge.content = "Content about complementary colors"
        mock_knowledge.category = "harmony"
        mock_knowledge.keywords = ["complementary", "red", "green"]
        mock_knowledge.source = "color-theory.md"
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_knowledge]
        mock_session.query.return_value = mock_query
        
        # Perform search
        mock_client = MagicMock()
        search = ColorTheorySearch(mock_client)
        results = search.search_by_keywords(["complementary"], category="harmony")
        
        # Verify results
        assert len(results) == 1
        assert results[0]['title'] == "Complementary Colors"
        assert "complementary" in results[0]['keywords']
    
    @patch('data.search.get_database')
    def test_get_related_knowledge(self, mock_get_db):
        """Test finding related knowledge entries."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock reference knowledge
        knowledge_id = str(uuid4())
        mock_reference = MagicMock(spec=ColorTheoryKnowledge)
        mock_reference.embedding = [0.1, 0.2, 0.3]
        
        # Mock related knowledge
        mock_related = MagicMock(spec=ColorTheoryKnowledge)
        mock_related.id = uuid4()
        mock_related.title = "Related Topic"
        mock_related.content = "Related content"
        mock_related.category = "harmony"
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_reference
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [(mock_related, 0.92)]
        
        # Need to handle different query calls
        mock_session.query.side_effect = [
            mock_session.query.return_value,  # First call for reference
            mock_query  # Second call for search
        ]
        
        # Perform search
        mock_client = MagicMock()
        search = ColorTheorySearch(mock_client)
        results = search.get_related_knowledge(knowledge_id, limit=3)
        
        # Verify results
        assert len(results) == 1
        assert results[0]['title'] == "Related Topic"
        assert results[0]['similarity_score'] == 0.92


class TestArtworkSearch:
    """Test artwork search functionality."""
    
    @patch('data.search.get_database')
    def test_search_by_color_similarity(self, mock_get_db):
        """Test searching artworks by color similarity."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock artwork
        mock_artwork = MagicMock(spec=Artwork)
        mock_artwork.id = "vw_abstract_001"
        mock_artwork.title = "Abstract Harmony"
        mock_artwork.artist = "Test Artist"
        mock_artwork.dominant_colors = [{"hex": "#FF0000", "percentage": 40}]
        mock_artwork.color_temperature = "warm"
        mock_artwork.mood_attributes = ["energetic", "bold"]
        mock_artwork.recommended_spaces = ["living_room", "office"]
        mock_artwork.price = 299.99
        mock_artwork.image_url = "https://example.com/image.jpg"
        
        mock_result = [(mock_artwork, 0.88)]
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        # Perform search
        mock_client = MagicMock()
        search = ArtworkSearch(mock_client)
        color_embedding = [0.1, 0.2, 0.3]  # Mock embedding
        results = search.search_by_color_similarity(color_embedding)
        
        # Verify results
        assert len(results) == 1
        assert results[0]['id'] == "vw_abstract_001"
        assert results[0]['color_match_score'] == 0.88
        assert results[0]['color_temperature'] == "warm"
    
    @patch('data.search.get_database')
    def test_search_by_style_and_mood(self, mock_get_db):
        """Test searching artworks by style and mood."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock artwork
        mock_artwork = MagicMock(spec=Artwork)
        mock_artwork.id = "vw_modern_002"
        mock_artwork.title = "Modern Serenity"
        mock_artwork.artist = "Contemporary Artist"
        mock_artwork.mood_attributes = ["calm", "peaceful"]
        mock_artwork.recommended_spaces = ["bedroom", "office"]
        mock_artwork.image_url = "https://example.com/modern.jpg"
        
        mock_result = [(mock_artwork, 0.91)]
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_result
        mock_session.query.return_value = mock_query
        
        # Mock OpenAI client for style embedding
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.4, 0.5, 0.6])]
        mock_client.embeddings.create.return_value = mock_response
        
        # Perform search
        search = ArtworkSearch(mock_client)
        results = search.search_by_style_and_mood(
            "modern minimalist",
            ["calm", "peaceful"],
            space_type="bedroom"
        )
        
        # Verify results
        assert len(results) == 1
        assert results[0]['id'] == "vw_modern_002"
        assert results[0]['style_match_score'] == 0.91
        assert "calm" in results[0]['mood_attributes']


class TestCachedColorHarmonySearch:
    """Test cached color harmony search."""
    
    @patch('data.search.get_database')
    def test_find_cached_harmony(self, mock_get_db):
        """Test finding cached harmony calculations."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # Mock cache entry
        mock_cache = MagicMock(spec=ColorHarmonyCache)
        mock_cache.complementary_score = 0.85
        mock_cache.analogous_score = 0.72
        mock_cache.triadic_score = 0.68
        mock_cache.monochromatic_score = 0.45
        mock_cache.overall_harmony_score = 0.75
        mock_cache.temperature_compatibility = 0.90
        mock_cache.harmony_type = "complementary"
        mock_cache.color_relationships = {"primary": "red", "complement": "green"}
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_cache
        
        # Perform search
        search = CachedColorHarmonySearch()
        colors1 = ["#FF0000", "#FF6600"]
        colors2 = ["#00FF00", "#00FF66"]
        result = search.find_cached_harmony(colors1, colors2)
        
        # Verify result
        assert result is not None
        assert result['overall_harmony_score'] == 0.75
        assert result['harmony_type'] == "complementary"
        assert result['temperature_compatibility'] == 0.90
        
        # Verify cache update
        assert mock_cache.access_count == 1  # Initial value
        mock_session.commit.assert_called_once()
    
    @patch('data.search.get_database')
    def test_find_cached_harmony_not_found(self, mock_get_db):
        """Test when cached harmony is not found."""
        # Mock database
        mock_db = MagicMock()
        mock_session = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.get_session.return_value.__enter__.return_value = mock_session
        
        # No cache entry found
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Perform search
        search = CachedColorHarmonySearch()
        result = search.find_cached_harmony(["#FF0000"], ["#00FF00"])
        
        # Verify result
        assert result is None
        mock_session.commit.assert_not_called()


class TestQuickSearch:
    """Test convenience search functions."""
    
    @patch('data.search.OpenAI')
    @patch('data.search.ColorTheorySearch')
    def test_quick_color_theory_search(self, mock_search_class, mock_openai_class):
        """Test quick search function."""
        # Mock search instance
        mock_search = MagicMock()
        mock_search.search_color_theory.return_value = [
            {
                'title': 'Test Result',
                'content': 'Test content',
                'similarity_score': 0.85
            }
        ]
        mock_search_class.return_value = mock_search
        
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Set environment variable
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            results = quick_color_theory_search("test query", limit=3)
        
        # Verify
        assert len(results) == 1
        assert results[0]['title'] == 'Test Result'
        mock_search.search_color_theory.assert_called_once_with("test query", limit=3)
        mock_openai_class.assert_called_once_with(api_key='test_key')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 