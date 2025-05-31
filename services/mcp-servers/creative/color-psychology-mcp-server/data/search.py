#!/usr/bin/env python3
"""
Semantic search functionality for VividWalls Color Psychology MCP Server.

This module provides vector-based semantic search capabilities for
querying the color theory knowledge base using pgvector.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from sqlalchemy import text, func, and_, or_
from sqlalchemy.orm import Session
from openai import OpenAI

from .models import (
    ColorTheoryKnowledge,
    Artwork,
    RoomAnalysis,
    ColorHarmonyCache,
    AnalysisStatus
)
from .database import get_database

# Configure logging
logger = logging.getLogger(__name__)


class ColorTheorySearch:
    """Semantic search for color theory knowledge base."""
    
    def __init__(self, openai_client: OpenAI):
        """
        Initialize search with OpenAI client for embeddings.
        
        Args:
            openai_client: OpenAI client instance
        """
        self.client = openai_client
        self.db = get_database()
        self.embedding_model = "text-embedding-3-small"
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector
        """
        try:
            logger.info(f"Generating embedding for query: {query[:50]}...")
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def search_color_theory(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search color theory knowledge base using semantic similarity.
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of search results with scores
        """
        logger.info(f"Searching color theory for: {query}")
        
        # Generate query embedding
        query_embedding = self.generate_query_embedding(query)
        
        with self.db.get_session() as session:
            # Build base query with vector similarity
            # Using cosine similarity (1 - cosine_distance)
            similarity_expr = 1 - func.cosine_distance(
                ColorTheoryKnowledge.embedding,
                query_embedding
            )
            
            query_obj = session.query(
                ColorTheoryKnowledge,
                similarity_expr.label('similarity_score')
            )
            
            # Apply category filter if specified
            if category:
                query_obj = query_obj.filter(
                    ColorTheoryKnowledge.category == category
                )
            
            # Filter by minimum score and order by similarity
            results = (
                query_obj
                .filter(similarity_expr >= min_score)
                .order_by(similarity_expr.desc())
                .limit(limit)
                .all()
            )
            
            # Format results
            formatted_results = []
            for knowledge, score in results:
                formatted_results.append({
                    'id': str(knowledge.id),
                    'title': knowledge.title,
                    'content': knowledge.content,
                    'category': knowledge.category,
                    'keywords': knowledge.keywords or [],
                    'similarity_score': float(score),
                    'source': knowledge.source
                })
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
    
    def search_by_keywords(
        self,
        keywords: List[str],
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search by exact keyword matches.
        
        Args:
            keywords: List of keywords to search
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        logger.info(f"Searching by keywords: {keywords}")
        
        with self.db.get_session() as session:
            query = session.query(ColorTheoryKnowledge)
            
            # Apply category filter
            if category:
                query = query.filter(ColorTheoryKnowledge.category == category)
            
            # Search in keywords JSON field
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(
                    ColorTheoryKnowledge.keywords.contains([keyword])
                )
            
            if keyword_conditions:
                query = query.filter(or_(*keyword_conditions))
            
            results = query.limit(limit).all()
            
            # Format results
            formatted_results = []
            for knowledge in results:
                formatted_results.append({
                    'id': str(knowledge.id),
                    'title': knowledge.title,
                    'content': knowledge.content,
                    'category': knowledge.category,
                    'keywords': knowledge.keywords or [],
                    'source': knowledge.source
                })
            
            return formatted_results
    
    def get_related_knowledge(
        self,
        knowledge_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find related color theory knowledge based on similarity.
        
        Args:
            knowledge_id: ID of reference knowledge
            limit: Maximum number of results
            
        Returns:
            List of related knowledge entries
        """
        logger.info(f"Finding related knowledge for ID: {knowledge_id}")
        
        with self.db.get_session() as session:
            # Get the reference knowledge
            reference = session.query(ColorTheoryKnowledge).filter(
                ColorTheoryKnowledge.id == knowledge_id
            ).first()
            
            if not reference:
                logger.warning(f"Knowledge ID {knowledge_id} not found")
                return []
            
            # Find similar entries using vector similarity
            similarity_expr = 1 - func.cosine_distance(
                ColorTheoryKnowledge.embedding,
                reference.embedding
            )
            
            results = (
                session.query(
                    ColorTheoryKnowledge,
                    similarity_expr.label('similarity_score')
                )
                .filter(ColorTheoryKnowledge.id != knowledge_id)
                .order_by(similarity_expr.desc())
                .limit(limit)
                .all()
            )
            
            # Format results
            formatted_results = []
            for knowledge, score in results:
                formatted_results.append({
                    'id': str(knowledge.id),
                    'title': knowledge.title,
                    'content': knowledge.content,
                    'category': knowledge.category,
                    'similarity_score': float(score)
                })
            
            return formatted_results


class ArtworkSearch:
    """Semantic search for artwork database."""
    
    def __init__(self, openai_client: OpenAI):
        """
        Initialize search with OpenAI client.
        
        Args:
            openai_client: OpenAI client instance
        """
        self.client = openai_client
        self.db = get_database()
        self.embedding_model = "text-embedding-3-small"
    
    def search_by_color_similarity(
        self,
        color_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Search artworks by color similarity.
        
        Args:
            color_embedding: Color composition embedding
            limit: Maximum number of results
            min_score: Minimum similarity score
            
        Returns:
            List of matching artworks
        """
        logger.info("Searching artworks by color similarity")
        
        with self.db.get_session() as session:
            # Calculate color similarity
            similarity_expr = 1 - func.cosine_distance(
                Artwork.color_embedding,
                color_embedding
            )
            
            results = (
                session.query(
                    Artwork,
                    similarity_expr.label('color_match_score')
                )
                .filter(
                    and_(
                        Artwork.availability == True,
                        Artwork.analysis_status == AnalysisStatus.COMPLETED,
                        similarity_expr >= min_score
                    )
                )
                .order_by(similarity_expr.desc())
                .limit(limit)
                .all()
            )
            
            # Format results
            formatted_results = []
            for artwork, score in results:
                formatted_results.append({
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist,
                    'dominant_colors': artwork.dominant_colors,
                    'color_temperature': artwork.color_temperature,
                    'mood_attributes': artwork.mood_attributes,
                    'recommended_spaces': artwork.recommended_spaces,
                    'color_match_score': float(score),
                    'price': artwork.price,
                    'image_url': artwork.image_url
                })
            
            return formatted_results
    
    def search_by_style_and_mood(
        self,
        style_query: str,
        mood_attributes: List[str],
        space_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search artworks by style and mood attributes.
        
        Args:
            style_query: Style description for embedding
            mood_attributes: List of mood attributes
            space_type: Optional space type filter
            limit: Maximum number of results
            
        Returns:
            List of matching artworks
        """
        logger.info(f"Searching artworks by style: {style_query}, moods: {mood_attributes}")
        
        # Generate style embedding
        style_embedding = self._generate_embedding(style_query)
        
        with self.db.get_session() as session:
            # Calculate style similarity
            similarity_expr = 1 - func.cosine_distance(
                Artwork.style_embedding,
                style_embedding
            )
            
            query = session.query(
                Artwork,
                similarity_expr.label('style_match_score')
            ).filter(
                Artwork.availability == True,
                Artwork.analysis_status == AnalysisStatus.COMPLETED
            )
            
            # Filter by mood attributes
            if mood_attributes:
                mood_conditions = []
                for mood in mood_attributes:
                    mood_conditions.append(
                        Artwork.mood_attributes.contains([mood])
                    )
                query = query.filter(or_(*mood_conditions))
            
            # Filter by space type
            if space_type:
                query = query.filter(
                    Artwork.recommended_spaces.contains([space_type])
                )
            
            results = query.order_by(similarity_expr.desc()).limit(limit).all()
            
            # Format results
            formatted_results = []
            for artwork, score in results:
                formatted_results.append({
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist,
                    'style_match_score': float(score),
                    'mood_attributes': artwork.mood_attributes,
                    'recommended_spaces': artwork.recommended_spaces,
                    'image_url': artwork.image_url
                })
            
            return formatted_results
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise


# Cache search for performance optimization
class CachedColorHarmonySearch:
    """Search cached color harmony calculations."""
    
    def __init__(self):
        """Initialize cache search."""
        self.db = get_database()
    
    def find_cached_harmony(
        self,
        colors1: List[str],
        colors2: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Find cached harmony calculation for color sets.
        
        Args:
            colors1: First color set
            colors2: Second color set
            
        Returns:
            Cached harmony data if found
        """
        from .models import create_color_hash
        
        # Create hash for lookup
        colors_hash = create_color_hash(colors1, colors2)
        
        with self.db.get_session() as session:
            cache_entry = session.query(ColorHarmonyCache).filter(
                ColorHarmonyCache.colors_hash == colors_hash
            ).first()
            
            if cache_entry:
                # Update access metadata
                cache_entry.accessed_at = datetime.utcnow()
                cache_entry.access_count += 1
                session.commit()
                
                return {
                    'complementary_score': cache_entry.complementary_score,
                    'analogous_score': cache_entry.analogous_score,
                    'triadic_score': cache_entry.triadic_score,
                    'monochromatic_score': cache_entry.monochromatic_score,
                    'overall_harmony_score': cache_entry.overall_harmony_score,
                    'temperature_compatibility': cache_entry.temperature_compatibility,
                    'harmony_type': cache_entry.harmony_type,
                    'color_relationships': cache_entry.color_relationships
                }
            
            return None


# Convenience functions for quick searches
def quick_color_theory_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Quick search of color theory knowledge base.
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        Search results
    """
    import os
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    search = ColorTheorySearch(client)
    return search.search_color_theory(query, limit=limit) 