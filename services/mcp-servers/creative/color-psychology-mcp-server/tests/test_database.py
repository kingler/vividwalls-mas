#!/usr/bin/env python3
"""
Unit tests for database configuration and models.

Tests database connection, pgvector support, and all model operations
following TDD principles to ensure robust data layer functionality.
"""

import os
import sys
import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import (
    DatabaseConfig,
    get_database,
    init_database,
    ColorTheoryKnowledge,
    Artwork,
    RoomAnalysis,
    ColorHarmonyCache,
    PsychologicalProfile,
    AnalysisStatus,
    SpaceType,
    create_color_hash,
    ensure_no_living_beings
)


class TestDatabaseConfig:
    """Test database configuration and connection management."""
    
    def test_init_requires_database_url(self):
        """Test that DatabaseConfig requires a database URL."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL must be provided"):
                DatabaseConfig()
    
    def test_init_with_url_parameter(self):
        """Test initialization with URL parameter."""
        db = DatabaseConfig("postgresql://user:pass@localhost:5432/testdb")
        assert db.database_url == "postgresql://user:pass@localhost:5432/testdb"
    
    def test_init_from_environment(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"}):
            db = DatabaseConfig()
            assert db.database_url == "postgresql://test:test@localhost/test"
    
    def test_pool_configuration(self):
        """Test pool configuration from environment."""
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql://test:test@localhost/test",
            "DB_POOL_SIZE": "20",
            "DB_MAX_OVERFLOW": "40",
            "DB_POOL_TIMEOUT": "60",
            "DB_POOL_RECYCLE": "7200"
        }):
            db = DatabaseConfig()
            assert db.pool_config['pool_size'] == 20
            assert db.pool_config['max_overflow'] == 40
            assert db.pool_config['pool_timeout'] == 60
            assert db.pool_config['pool_recycle'] == 7200
            assert db.pool_config['pool_pre_ping'] is True
    
    @patch('data.database.create_engine')
    def test_engine_creation(self, mock_create_engine):
        """Test synchronous engine creation."""
        db = DatabaseConfig("postgresql://test:test@localhost/test")
        engine = db.engine
        
        mock_create_engine.assert_called_once()
        # Check it returns the same instance on subsequent calls
        assert db.engine is engine
    
    @patch('data.database.create_async_engine')
    def test_async_engine_creation(self, mock_create_async_engine):
        """Test asynchronous engine creation."""
        db = DatabaseConfig("postgresql://test:test@localhost/test")
        engine = db.async_engine
        
        mock_create_async_engine.assert_called_once()
        # URL should be converted to async format
        args, _ = mock_create_async_engine.call_args
        assert "postgresql+asyncpg://" in args[0]
    
    @patch('data.database.create_engine')
    def test_verify_connection_success(self, mock_create_engine):
        """Test successful connection verification."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)
        mock_conn.execute.return_value = mock_result
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConfig("postgresql://test:test@localhost/test")
        assert db.verify_connection() is True
    
    @patch('data.database.create_engine')
    def test_verify_pgvector_installed(self, mock_create_engine):
        """Test pgvector extension verification."""
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ('vector',)
        mock_conn.execute.return_value = mock_result
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConfig("postgresql://test:test@localhost/test")
        assert db.verify_pgvector() is True
    
    @patch('data.database.create_engine')
    def test_get_session_context_manager(self, mock_create_engine):
        """Test session context manager behavior."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        db = DatabaseConfig("postgresql://test:test@localhost/test")
        
        # Test successful transaction
        with db.get_session() as session:
            assert session is not None
            # Session should have transaction methods
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')


class TestColorTheoryKnowledge:
    """Test ColorTheoryKnowledge model."""
    
    def test_model_structure(self):
        """Test model has required attributes."""
        knowledge = ColorTheoryKnowledge()
        
        # Check required fields exist
        assert hasattr(knowledge, 'id')
        assert hasattr(knowledge, 'title')
        assert hasattr(knowledge, 'content')
        assert hasattr(knowledge, 'category')
        assert hasattr(knowledge, 'embedding')
        assert hasattr(knowledge, 'confidence_score')
    
    def test_confidence_validation(self):
        """Test confidence score validation."""
        knowledge = ColorTheoryKnowledge()
        
        # Valid scores
        knowledge.confidence_score = 0.5
        assert knowledge.validate_confidence('confidence_score', 0.5) == 0.5
        
        # Invalid scores
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 1"):
            knowledge.validate_confidence('confidence_score', 1.5)
        
        with pytest.raises(ValueError, match="Confidence score must be between 0 and 1"):
            knowledge.validate_confidence('confidence_score', -0.1)


class TestArtwork:
    """Test Artwork model."""
    
    def test_model_structure(self):
        """Test model has required attributes."""
        artwork = Artwork()
        
        # Check required fields
        assert hasattr(artwork, 'id')
        assert hasattr(artwork, 'title')
        assert hasattr(artwork, 'dominant_colors')
        assert hasattr(artwork, 'style_embedding')
        assert hasattr(artwork, 'color_embedding')
        assert hasattr(artwork, 'analysis_status')
    
    def test_default_values(self):
        """Test default values are set correctly."""
        artwork = Artwork()
        
        assert artwork.availability is True
        assert artwork.analysis_status == AnalysisStatus.PENDING


class TestRoomAnalysis:
    """Test RoomAnalysis model."""
    
    def test_model_structure(self):
        """Test model has required attributes."""
        analysis = RoomAnalysis()
        
        # Check required fields
        assert hasattr(analysis, 'id')
        assert hasattr(analysis, 'image_path')
        assert hasattr(analysis, 'color_palette')
        assert hasattr(analysis, 'room_embedding')
        assert hasattr(analysis, 'analysis_status')
    
    def test_default_status(self):
        """Test default analysis status."""
        analysis = RoomAnalysis()
        assert analysis.analysis_status == AnalysisStatus.PENDING


class TestColorHarmonyCache:
    """Test ColorHarmonyCache model."""
    
    def test_model_structure(self):
        """Test model has required attributes."""
        cache = ColorHarmonyCache()
        
        # Check required fields
        assert hasattr(cache, 'color_set_1')
        assert hasattr(cache, 'color_set_2')
        assert hasattr(cache, 'colors_hash')
        assert hasattr(cache, 'overall_harmony_score')
    
    def test_default_values(self):
        """Test default values."""
        cache = ColorHarmonyCache()
        
        assert cache.calculation_version == '1.0'
        assert cache.access_count == 1


class TestPsychologicalProfile:
    """Test PsychologicalProfile model."""
    
    def test_model_structure(self):
        """Test model has required attributes."""
        profile = PsychologicalProfile()
        
        # Check required fields
        assert hasattr(profile, 'space_type')
        assert hasattr(profile, 'color_scheme')
        assert hasattr(profile, 'primary_emotions')
        assert hasattr(profile, 'energy_level')
    
    def test_default_version(self):
        """Test default profile version."""
        profile = PsychologicalProfile()
        assert profile.profile_version == '1.0'


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_color_hash_consistency(self):
        """Test color hash creation is consistent."""
        colors1 = ['#FF0000', '#00FF00', '#0000FF']
        colors2 = ['#FFFF00', '#FF00FF']
        
        # Same inputs should produce same hash
        hash1 = create_color_hash(colors1, colors2)
        hash2 = create_color_hash(colors1, colors2)
        assert hash1 == hash2
        
        # Order within sets shouldn't matter
        colors1_reordered = ['#00FF00', '#FF0000', '#0000FF']
        hash3 = create_color_hash(colors1_reordered, colors2)
        assert hash3 == hash1
        
        # Different colors should produce different hash
        colors3 = ['#000000']
        hash4 = create_color_hash(colors1, colors3)
        assert hash4 != hash1
    
    def test_ensure_no_living_beings(self):
        """Test filtering of living beings from objects."""
        objects = [
            {'type': 'chair', 'confidence': 0.9},
            {'type': 'person', 'confidence': 0.8},  # Should be filtered
            {'type': 'table', 'confidence': 0.95},
            {'type': 'dog', 'confidence': 0.7},     # Should be filtered
            {'type': 'painting', 'confidence': 0.85},
            {'type': 'cat', 'confidence': 0.6},     # Should be filtered
            {'type': 'lamp', 'confidence': 0.88}
        ]
        
        filtered = ensure_no_living_beings(objects)
        
        # Check that only non-living objects remain
        assert len(filtered) == 4
        assert all(obj['type'] not in ['person', 'dog', 'cat'] for obj in filtered)
        assert filtered[0]['type'] == 'chair'
        assert filtered[1]['type'] == 'table'
        assert filtered[2]['type'] == 'painting'
        assert filtered[3]['type'] == 'lamp'
    
    def test_ensure_no_living_beings_comprehensive(self):
        """Test comprehensive filtering of all forbidden types."""
        forbidden_objects = [
            {'type': 'person'}, {'type': 'people'}, {'type': 'human'},
            {'type': 'man'}, {'type': 'woman'}, {'type': 'child'},
            {'type': 'dog'}, {'type': 'cat'}, {'type': 'animal'},
            {'type': 'pet'}, {'type': 'bird'}, {'type': 'fish'}
        ]
        
        # All should be filtered out
        filtered = ensure_no_living_beings(forbidden_objects)
        assert len(filtered) == 0
        
        # Case insensitive
        mixed_case = [
            {'type': 'Person'}, {'type': 'DOG'}, {'type': 'Cat'}
        ]
        filtered = ensure_no_living_beings(mixed_case)
        assert len(filtered) == 0


class TestDatabaseSingleton:
    """Test database singleton pattern."""
    
    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"})
    def test_get_database_singleton(self):
        """Test get_database returns same instance."""
        db1 = get_database()
        db2 = get_database()
        
        assert db1 is db2
    
    @patch('data.database.DatabaseConfig.verify_connection')
    @patch('data.database.DatabaseConfig.verify_pgvector')
    @patch('data.database.DatabaseConfig.create_tables')
    def test_init_database_complete_setup(self, mock_create, mock_pgvector, mock_connection):
        """Test init_database performs all setup steps."""
        mock_connection.return_value = True
        mock_pgvector.return_value = True
        
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"}):
            db = init_database()
            
            # Verify all setup methods were called
            mock_connection.assert_called_once()
            mock_pgvector.assert_called_once()
            mock_create.assert_called_once()
    
    @patch('data.database.DatabaseConfig.verify_connection')
    def test_init_database_connection_failure(self, mock_connection):
        """Test init_database handles connection failure."""
        mock_connection.return_value = False
        
        with patch.dict(os.environ, {"DATABASE_URL": "postgresql://test:test@localhost/test"}):
            with pytest.raises(RuntimeError, match="Failed to connect to database"):
                init_database()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 