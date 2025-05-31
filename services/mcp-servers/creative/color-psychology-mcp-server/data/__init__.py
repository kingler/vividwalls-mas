"""
Data layer for VividWalls Color Psychology MCP Server.

This package contains database models, configuration, utilities,
and search functionality for storing and retrieving color theory knowledge,
artwork data, and analysis results using PostgreSQL with pgvector.
"""

from .database import (
    DatabaseConfig,
    get_database,
    init_database,
    Base
)

from .models import (
    AnalysisStatus,
    SpaceType,
    ColorTheoryKnowledge,
    Artwork,
    RoomAnalysis,
    ColorHarmonyCache,
    PsychologicalProfile,
    create_color_hash,
    ensure_no_living_beings
)

from .search import (
    ColorTheorySearch,
    ArtworkSearch,
    CachedColorHarmonySearch,
    quick_color_theory_search
)

__all__ = [
    # Database
    'DatabaseConfig',
    'get_database',
    'init_database',
    'Base',
    
    # Enums
    'AnalysisStatus',
    'SpaceType',
    
    # Models
    'ColorTheoryKnowledge',
    'Artwork',
    'RoomAnalysis',
    'ColorHarmonyCache',
    'PsychologicalProfile',
    
    # Utilities
    'create_color_hash',
    'ensure_no_living_beings',
    
    # Search
    'ColorTheorySearch',
    'ArtworkSearch',
    'CachedColorHarmonySearch',
    'quick_color_theory_search'
] 