#!/usr/bin/env python3
"""
Database configuration and connection management for VividWalls Color Psychology MCP Server.

This module handles PostgreSQL connections with pgvector extension support,
connection pooling, and provides base functionality for all database operations.
"""

import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from urllib.parse import urlparse

from sqlalchemy import create_engine, text, pool
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
from pgvector.sqlalchemy import Vector

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy base for model declarations
Base = declarative_base()

class DatabaseConfig:
    """Database configuration and connection management."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database configuration.
        
        Args:
            database_url: PostgreSQL connection URL. If not provided, reads from environment.
        """
        self.database_url = database_url or os.getenv('DATABASE_URL', '')
        if not self.database_url:
            raise ValueError("DATABASE_URL must be provided or set in environment variables")
        
        # Parse URL for logging (without password)
        parsed = urlparse(self.database_url)
        safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
        logger.info(f"Initializing database connection to: {safe_url}")
        
        # Connection pool configuration
        self.pool_config = {
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
            'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
            'pool_pre_ping': True  # Verify connections before use
        }
        
        # Initialize engines
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
    
    @property
    def engine(self):
        """Get or create synchronous database engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                poolclass=pool.StaticPool if 'sqlite' in self.database_url else pool.QueuePool,
                **self.pool_config,
                echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
            )
            logger.info("Created synchronous database engine")
        return self._engine
    
    @property
    def async_engine(self):
        """Get or create asynchronous database engine."""
        if self._async_engine is None:
            # Convert postgresql:// to postgresql+asyncpg://
            async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
            self._async_engine = create_async_engine(
                async_url,
                pool_size=self.pool_config['pool_size'],
                max_overflow=self.pool_config['max_overflow'],
                pool_timeout=self.pool_config['pool_timeout'],
                pool_recycle=self.pool_config['pool_recycle'],
                pool_pre_ping=self.pool_config['pool_pre_ping'],
                echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
            )
            logger.info("Created asynchronous database engine")
        return self._async_engine
    
    @property
    def session_factory(self):
        """Get synchronous session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory
    
    @property
    def async_session_factory(self):
        """Get asynchronous session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._async_session_factory
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session with automatic cleanup.
        
        Yields:
            Session: SQLAlchemy session
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    async def get_async_session(self) -> AsyncSession:
        """
        Get an async database session.
        
        Returns:
            AsyncSession: SQLAlchemy async session
        """
        async with self.async_session_factory() as session:
            return session
    
    def verify_connection(self) -> bool:
        """
        Verify database connection is working.
        
        Returns:
            bool: True if connection successful
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database connection verified")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    def verify_pgvector(self) -> bool:
        """
        Verify pgvector extension is installed.
        
        Returns:
            bool: True if pgvector is available
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                )
                if result.fetchone():
                    logger.info("pgvector extension verified")
                    return True
                else:
                    logger.warning("pgvector extension not found")
                    return False
        except Exception as e:
            logger.error(f"Error checking pgvector: {str(e)}")
            return False
    
    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all database tables. Use with caution!"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Error dropping tables: {str(e)}")
            raise
    
    async def test_async_connection(self) -> bool:
        """
        Test async database connection.
        
        Returns:
            bool: True if async connection successful
        """
        try:
            async with self.async_engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()
                logger.info("Async database connection verified")
                return True
        except Exception as e:
            logger.error(f"Async database connection failed: {str(e)}")
            return False
    
    def close(self):
        """Close database connections and cleanup."""
        if self._engine:
            self._engine.dispose()
            logger.info("Closed synchronous database engine")
        
        if self._async_engine:
            # Note: async engine disposal should be done in async context
            logger.info("Async engine marked for disposal")


# Global database instance
_db_instance: Optional[DatabaseConfig] = None


def get_database(database_url: Optional[str] = None) -> DatabaseConfig:
    """
    Get or create database instance (singleton pattern).
    
    Args:
        database_url: Optional database URL override
    
    Returns:
        DatabaseConfig: Database configuration instance
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConfig(database_url)
    
    return _db_instance


def init_database(database_url: Optional[str] = None) -> DatabaseConfig:
    """
    Initialize database and verify setup.
    
    Args:
        database_url: Optional database URL override
    
    Returns:
        DatabaseConfig: Initialized database instance
    
    Raises:
        RuntimeError: If database or pgvector setup fails
    """
    db = get_database(database_url)
    
    # Verify connection
    if not db.verify_connection():
        raise RuntimeError("Failed to connect to database")
    
    # Verify pgvector
    if not db.verify_pgvector():
        raise RuntimeError("pgvector extension not found. Please install it first.")
    
    # Create tables
    db.create_tables()
    
    return db


# Example usage
if __name__ == "__main__":
    # Test database connection
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize database
    db = init_database()
    
    # Test async connection
    async def test_async():
        return await db.test_async_connection()
    
    asyncio.run(test_async())
    
    print("Database setup complete!") 