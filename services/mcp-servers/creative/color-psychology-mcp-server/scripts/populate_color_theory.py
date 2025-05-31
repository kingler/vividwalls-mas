#!/usr/bin/env python3
"""
Populate the color theory knowledge base from markdown documents.

This script reads color theory documentation (especially color-theory.md)
and populates the PostgreSQL database with vector embeddings for
semantic search capability.
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from openai import OpenAI
import markdown

from data import (
    init_database,
    get_database,
    ColorTheoryKnowledge,
    AnalysisStatus
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ColorTheoryParser:
    """Parse and process color theory markdown documents."""
    
    def __init__(self, openai_client: OpenAI):
        """
        Initialize parser with OpenAI client.
        
        Args:
            openai_client: OpenAI client for embeddings
        """
        self.client = openai_client
        self.chunks: List[Dict] = []
    
    def parse_markdown_file(self, file_path: str) -> List[Dict]:
        """
        Parse a markdown file into structured chunks.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List of parsed chunks with metadata
        """
        logger.info(f"Parsing markdown file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into sections based on headers
        sections = self._split_into_sections(content)
        
        # Process each section
        chunks = []
        for section in sections:
            # Further split long sections
            if len(section['content']) > 2000:
                sub_chunks = self._split_long_section(section)
                chunks.extend(sub_chunks)
            else:
                chunks.append(section)
        
        logger.info(f"Parsed {len(chunks)} chunks from {file_path}")
        return chunks
    
    def _split_into_sections(self, content: str) -> List[Dict]:
        """Split markdown content into sections based on headers."""
        # Pattern to match markdown headers
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        sections = []
        current_section = {'title': 'Introduction', 'content': '', 'level': 0}
        current_category = 'general'
        
        for line in content.split('\n'):
            header_match = header_pattern.match(line)
            
            if header_match:
                # Save current section if it has content
                if current_section['content'].strip():
                    current_section['category'] = current_category
                    sections.append(current_section)
                
                # Start new section
                level = len(header_match.group(1))
                title = header_match.group(2)
                
                # Determine category based on title
                current_category = self._determine_category(title)
                
                current_section = {
                    'title': title,
                    'content': '',
                    'level': level,
                    'category': current_category
                }
            else:
                current_section['content'] += line + '\n'
        
        # Don't forget the last section
        if current_section['content'].strip():
            current_section['category'] = current_category
            sections.append(current_section)
        
        return sections
    
    def _determine_category(self, title: str) -> str:
        """Determine category based on section title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['harmony', 'complementary', 'analogous', 'triadic']):
            return 'harmony'
        elif any(word in title_lower for word in ['psychology', 'emotion', 'mood', 'feeling']):
            return 'psychology'
        elif any(word in title_lower for word in ['temperature', 'warm', 'cool', 'neutral']):
            return 'temperature'
        elif any(word in title_lower for word in ['culture', 'cultural', 'meaning']):
            return 'culture'
        elif any(word in title_lower for word in ['space', 'room', 'interior']):
            return 'space'
        elif any(word in title_lower for word in ['art', 'artwork', 'painting']):
            return 'artwork'
        else:
            return 'general'
    
    def _split_long_section(self, section: Dict) -> List[Dict]:
        """Split a long section into smaller chunks."""
        content = section['content']
        chunks = []
        
        # Split by paragraphs
        paragraphs = content.split('\n\n')
        current_chunk = ''
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > 1500:
                if current_chunk:
                    chunks.append({
                        'title': f"{section['title']} (Part {len(chunks) + 1})",
                        'content': current_chunk.strip(),
                        'level': section['level'],
                        'category': section['category']
                    })
                current_chunk = para
            else:
                current_chunk += '\n\n' + para if current_chunk else para
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                'title': f"{section['title']} (Part {len(chunks) + 1})",
                'content': current_chunk.strip(),
                'level': section['level'],
                'category': section['category']
            })
        
        return chunks if chunks else [section]
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Simple keyword extraction - could be enhanced with NLP
        keywords = []
        
        # Color names
        color_pattern = re.compile(r'\b(red|blue|green|yellow|orange|purple|pink|brown|black|white|gray|grey)\b', re.IGNORECASE)
        keywords.extend(color_pattern.findall(text.lower()))
        
        # Technical terms
        tech_terms = ['complementary', 'analogous', 'triadic', 'monochromatic', 'harmony',
                      'saturation', 'hue', 'value', 'temperature', 'psychology']
        for term in tech_terms:
            if term in text.lower():
                keywords.append(term)
        
        # Remove duplicates
        return list(set(keywords))


def populate_database(chunks: List[Dict], parser: ColorTheoryParser, db_session):
    """
    Populate database with color theory knowledge chunks.
    
    Args:
        chunks: List of parsed chunks
        parser: ColorTheoryParser instance for embeddings
        db_session: Database session
    """
    logger.info(f"Populating database with {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        try:
            # Generate embedding
            embedding = parser.generate_embedding(chunk['content'])
            
            # Extract keywords
            keywords = parser.extract_keywords(chunk['content'])
            
            # Create knowledge entry
            knowledge = ColorTheoryKnowledge(
                title=chunk['title'],
                content=chunk['content'],
                category=chunk['category'],
                source='color-theory.md',
                embedding=embedding,
                keywords=keywords,
                confidence_score=0.95  # High confidence for curated content
            )
            
            db_session.add(knowledge)
            
            # Commit periodically
            if (i + 1) % 10 == 0:
                db_session.commit()
                logger.info(f"Committed {i + 1} chunks")
        
        except Exception as e:
            logger.error(f"Error processing chunk {i}: {str(e)}")
            db_session.rollback()
            continue
    
    # Final commit
    db_session.commit()
    logger.info("Database population complete")


def main():
    """Main function to populate color theory knowledge base."""
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY environment variable required")
    
    if not os.getenv('DATABASE_URL'):
        raise ValueError("DATABASE_URL environment variable required")
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Initialize database
    logger.info("Initializing database...")
    db = init_database()
    
    # Create parser
    parser = ColorTheoryParser(openai_client)
    
    # Find color theory markdown file
    # First check in the project root
    color_theory_path = Path('../../../../color-theory.md')
    if not color_theory_path.exists():
        # Check alternative location
        color_theory_path = Path('color-theory.md')
    
    if not color_theory_path.exists():
        raise FileNotFoundError("Could not find color-theory.md file")
    
    # Parse the file
    chunks = parser.parse_markdown_file(str(color_theory_path))
    
    # Populate database
    with db.get_session() as session:
        # Clear existing data (optional)
        if input("Clear existing color theory data? (y/n): ").lower() == 'y':
            session.query(ColorTheoryKnowledge).delete()
            session.commit()
            logger.info("Cleared existing data")
        
        # Populate with new data
        populate_database(chunks, parser, session)
    
    logger.info("Color theory knowledge base population complete!")
    
    # Verify data
    with db.get_session() as session:
        count = session.query(ColorTheoryKnowledge).count()
        logger.info(f"Total knowledge entries: {count}")
        
        # Show sample entries
        samples = session.query(ColorTheoryKnowledge).limit(3).all()
        for sample in samples:
            logger.info(f"Sample: {sample.title} ({sample.category})")


if __name__ == "__main__":
    main() 