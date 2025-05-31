#!/usr/bin/env python3
"""
Database models for VividWalls Color Psychology MCP Server.

This module defines SQLAlchemy models for storing color theory knowledge,
artwork metadata, analysis results, and vector embeddings using pgvector.
"""

import json
import enum
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, 
    ForeignKey, Index, JSON, Enum, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from .database import Base


class AnalysisStatus(enum.Enum):
    """Status of analysis operations."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


class SpaceType(enum.Enum):
    """Types of spaces for psychological compatibility."""
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    OFFICE = "office"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    DINING_ROOM = "dining_room"
    HALLWAY = "hallway"
    KIDS_ROOM = "kids_room"
    STUDIO = "studio"
    OTHER = "other"


class ColorTheoryKnowledge(Base):
    """
    Store color theory knowledge with vector embeddings for semantic search.
    
    This table stores chunks of color theory text with their vector embeddings
    for efficient similarity search using pgvector.
    """
    __tablename__ = 'color_theory_knowledge'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Content and metadata
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)  # e.g., 'harmony', 'psychology', 'temperature'
    source = Column(String(255))  # Source reference
    
    # Vector embedding for semantic search (1536 dimensions for OpenAI embeddings)
    embedding = Column(Vector(1536), nullable=False)
    
    # Metadata
    keywords = Column(JSON)  # List of relevant keywords
    confidence_score = Column(Float, default=1.0)  # Confidence in the knowledge accuracy
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient searching
    __table_args__ = (
        Index('idx_color_theory_category', 'category'),
        Index('idx_color_theory_embedding', 'embedding', postgresql_using='ivfflat'),
    )
    
    @validates('confidence_score')
    def validate_confidence(self, key, value):
        """Ensure confidence score is between 0 and 1."""
        if not 0 <= value <= 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return value


class Artwork(Base):
    """
    Store VividWalls artwork metadata and attributes.
    
    This table contains all artwork information including color analysis,
    psychological attributes, and embeddings for similarity matching.
    """
    __tablename__ = 'artworks'
    
    id = Column(String(50), primary_key=True)  # e.g., 'vw_abstract_001'
    
    # Basic metadata
    title = Column(String(255), nullable=False)
    artist = Column(String(255))
    description = Column(Text)
    
    # Physical attributes
    width_inches = Column(Float, nullable=False)
    height_inches = Column(Float, nullable=False)
    medium = Column(String(100))  # e.g., 'canvas print', 'framed print'
    
    # Color analysis results
    dominant_colors = Column(JSON, nullable=False)  # List of {hex, percentage, name}
    color_palette = Column(JSON)  # Extended color information
    color_temperature = Column(String(20))  # 'warm', 'cool', 'neutral'
    
    # Psychological attributes
    mood_attributes = Column(JSON)  # List of mood descriptors
    psychological_impact = Column(JSON)  # Detailed psychological analysis
    recommended_spaces = Column(JSON)  # List of SpaceType values
    
    # Vector embeddings
    style_embedding = Column(Vector(1536))  # Style characteristics embedding
    color_embedding = Column(Vector(1536))  # Color composition embedding
    
    # Metadata
    tags = Column(JSON)  # List of descriptive tags
    price = Column(Float)
    availability = Column(Boolean, default=True)
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    
    # Analysis status
    analysis_status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    analysis_timestamp = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    room_analyses = relationship("RoomAnalysis", back_populates="recommended_artworks")
    
    # Indexes
    __table_args__ = (
        Index('idx_artwork_mood', 'mood_attributes', postgresql_using='gin'),
        Index('idx_artwork_tags', 'tags', postgresql_using='gin'),
        Index('idx_artwork_style_embedding', 'style_embedding', postgresql_using='ivfflat'),
        Index('idx_artwork_color_embedding', 'color_embedding', postgresql_using='ivfflat'),
    )


class RoomAnalysis(Base):
    """
    Store room analysis results and recommendations.
    
    This table contains the analysis results from customer room images
    and the artwork recommendations generated for them.
    """
    __tablename__ = 'room_analyses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Customer/session information
    session_id = Column(String(100))  # Optional session tracking
    customer_email = Column(String(255))  # Optional for follow-up
    
    # Room image data
    image_path = Column(String(500), nullable=False)
    image_hash = Column(String(64))  # For duplicate detection
    
    # Room analysis results
    room_type = Column(Enum(SpaceType))
    color_palette = Column(JSON, nullable=False)  # Extracted colors
    objects_detected = Column(JSON)  # Furniture and decor (NO HUMANS/ANIMALS)
    wall_analysis = Column(JSON)  # Optimal wall information
    spatial_analysis = Column(JSON)  # Room layout data
    
    # Lighting and ambiance
    lighting_conditions = Column(String(50))  # 'bright', 'dim', 'natural', etc.
    ambiance_score = Column(Float)  # Overall room ambiance rating
    
    # Vector embedding of room characteristics
    room_embedding = Column(Vector(1536))
    
    # Recommendations
    recommended_artwork_ids = Column(JSON)  # List of artwork IDs
    recommendation_scores = Column(JSON)  # Detailed scoring breakdown
    
    # Composite images
    composite_image_urls = Column(JSON)  # Generated visualization URLs
    
    # Status and metadata
    analysis_status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PENDING)
    processing_time_ms = Column(Integer)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    recommended_artworks = relationship("Artwork", back_populates="room_analyses")
    
    # Indexes
    __table_args__ = (
        Index('idx_room_analysis_session', 'session_id'),
        Index('idx_room_analysis_status', 'analysis_status'),
        Index('idx_room_analysis_created', 'created_at'),
        UniqueConstraint('image_hash', name='uq_room_analysis_image'),
    )


class ColorHarmonyCache(Base):
    """
    Cache color harmony calculations for performance.
    
    This table stores pre-calculated color harmony scores between
    color combinations to avoid redundant calculations.
    """
    __tablename__ = 'color_harmony_cache'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Color combination (stored as sorted JSON array for consistency)
    color_set_1 = Column(JSON, nullable=False)  # First set of colors
    color_set_2 = Column(JSON, nullable=False)  # Second set of colors
    colors_hash = Column(String(64), nullable=False, unique=True)  # Hash of both sets
    
    # Harmony scores
    complementary_score = Column(Float)
    analogous_score = Column(Float)
    triadic_score = Column(Float)
    monochromatic_score = Column(Float)
    overall_harmony_score = Column(Float, nullable=False)
    
    # Temperature compatibility
    temperature_compatibility = Column(Float)
    
    # Detailed analysis
    harmony_type = Column(String(50))  # Detected harmony type
    color_relationships = Column(JSON)  # Detailed color relationships
    
    # Cache metadata
    calculation_version = Column(String(20), default='1.0')
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    
    # Indexes
    __table_args__ = (
        Index('idx_harmony_cache_hash', 'colors_hash'),
        Index('idx_harmony_cache_accessed', 'accessed_at'),
    )


class PsychologicalProfile(Base):
    """
    Store psychological analysis profiles for different contexts.
    
    This table contains pre-analyzed psychological profiles for
    various color combinations and space types.
    """
    __tablename__ = 'psychological_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Context
    space_type = Column(Enum(SpaceType), nullable=False)
    color_scheme = Column(JSON, nullable=False)  # Colors involved
    
    # Emotional analysis
    primary_emotions = Column(JSON)  # List of primary emotions evoked
    energy_level = Column(Float)  # 0-1 scale
    complexity_score = Column(Float)  # Cognitive load score
    warmth_score = Column(Float)  # Emotional warmth
    
    # Psychological impact
    stress_reduction = Column(Float)  # Potential for stress reduction
    creativity_boost = Column(Float)  # Potential for creativity enhancement
    focus_enhancement = Column(Float)  # Potential for focus improvement
    mood_stability = Column(Float)  # Emotional stability score
    
    # Recommendations
    therapeutic_value = Column(JSON)  # Therapeutic benefits
    activity_compatibility = Column(JSON)  # Compatible activities
    time_of_day_preference = Column(JSON)  # Best times for the scheme
    
    # Metadata
    profile_version = Column(String(20), default='1.0')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_psych_profile_space', 'space_type'),
        Index('idx_psych_profile_emotions', 'primary_emotions', postgresql_using='gin'),
    )


# Helper functions for model operations

def create_color_hash(colors1: List[str], colors2: List[str]) -> str:
    """
    Create a consistent hash for color combinations.
    
    Args:
        colors1: First set of colors
        colors2: Second set of colors
        
    Returns:
        Hex hash string for the color combination
    """
    import hashlib
    
    # Sort both sets and combine
    all_colors = sorted(colors1) + ['|'] + sorted(colors2)
    color_string = ','.join(all_colors)
    
    # Create hash
    return hashlib.sha256(color_string.encode()).hexdigest()


def ensure_no_living_beings(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out any living beings from object detection results.
    
    CRITICAL: Enforces NO HUMANS OR ANIMALS rule.
    
    Args:
        objects: List of detected objects
        
    Returns:
        Filtered list with no living beings
    """
    forbidden_types = {
        'person', 'people', 'human', 'man', 'woman', 'child',
        'dog', 'cat', 'animal', 'pet', 'bird', 'fish'
    }
    
    return [
        obj for obj in objects 
        if obj.get('type', '').lower() not in forbidden_types
    ] 