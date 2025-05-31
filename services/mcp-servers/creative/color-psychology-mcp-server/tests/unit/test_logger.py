#!/usr/bin/env python3
"""
Unit tests for the logger module.

Following TDD principles - these tests are written before implementation
to ensure the logger meets all requirements.

Requirements:
- Winston-style modular logging
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output
- Structured logging format
- Integration with all modules
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the logger module (to be implemented)
from utils.logger import setup_logger, get_logger, LogLevel, LogConfig


class TestLoggerSetup:
    """Test logger setup and configuration."""
    
    def test_setup_logger_creates_default_configuration(self):
        """Test that setup_logger creates a logger with default settings."""
        # Arrange
        logger_name = "test_logger"
        
        # Act
        logger = setup_logger(logger_name)
        
        # Assert
        assert logger is not None
        assert logger.name == logger_name
        assert logger.level == LogLevel.INFO.value  # Default level
        assert len(logger.handlers) >= 1  # At least console handler
    
    def test_setup_logger_with_custom_config(self):
        """Test that setup_logger accepts and applies custom configuration."""
        # Arrange
        config = LogConfig(
            level=LogLevel.DEBUG,
            console_enabled=True,
            file_enabled=True,
            file_path="test.log",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Act
        logger = setup_logger("test_logger", config)
        
        # Assert
        assert logger.level == LogLevel.DEBUG.value
        assert any(h.name == "console" for h in logger.handlers)
        assert any(h.name == "file" for h in logger.handlers)
    
    def test_setup_logger_creates_log_directory(self):
        """Test that logger creates log directory if it doesn't exist."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "logs", "test.log")
            config = LogConfig(file_enabled=True, file_path=log_path)
            
            # Act
            logger = setup_logger("test_logger", config)
            
            # Assert
            assert os.path.exists(os.path.dirname(log_path))
    
    def test_get_logger_returns_existing_logger(self):
        """Test that get_logger returns the same logger instance."""
        # Arrange
        logger_name = "test_singleton"
        
        # Act
        logger1 = setup_logger(logger_name)
        logger2 = get_logger(logger_name)
        
        # Assert
        assert logger1 is logger2


class TestLoggerFunctionality:
    """Test logger functionality and output."""
    
    def test_logger_logs_all_levels(self):
        """Test that logger can log messages at all levels."""
        # Arrange
        logger = setup_logger("test_levels", LogConfig(level=LogLevel.DEBUG))
        
        # Act & Assert - should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_logger_respects_log_level(self):
        """Test that logger only logs messages at or above set level."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            config = LogConfig(
                level=LogLevel.WARNING,
                file_enabled=True,
                file_path=temp_file.name,
                console_enabled=False
            )
            logger = setup_logger("test_level_filter", config)
            
            # Act
            logger.debug("Should not appear")
            logger.info("Should not appear")
            logger.warning("Should appear")
            logger.error("Should appear")
            
            # Assert
            temp_file.close()
            with open(temp_file.name, 'r') as f:
                content = f.read()
                assert "Should not appear" not in content
                assert "Should appear" in content
            
            os.unlink(temp_file.name)
    
    def test_logger_structured_output(self):
        """Test that logger outputs in structured format."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            config = LogConfig(
                file_enabled=True,
                file_path=temp_file.name,
                console_enabled=False,
                structured=True  # Enable structured JSON logging
            )
            logger = setup_logger("test_structured", config)
            
            # Act
            logger.info("Test message", extra={"user_id": 123, "action": "analyze"})
            
            # Assert
            temp_file.close()
            with open(temp_file.name, 'r') as f:
                line = f.readline()
                log_entry = json.loads(line)
                assert log_entry["message"] == "Test message"
                assert log_entry["user_id"] == 123
                assert log_entry["action"] == "analyze"
                assert "timestamp" in log_entry
                assert "level" in log_entry
            
            os.unlink(temp_file.name)
    
    def test_logger_handles_exceptions(self):
        """Test that logger can properly log exception information."""
        # Arrange
        logger = setup_logger("test_exceptions", LogConfig(level=LogLevel.DEBUG))
        
        # Act & Assert
        try:
            raise ValueError("Test exception")
        except ValueError:
            # Should not raise exception
            logger.exception("An error occurred")


class TestLoggerIntegration:
    """Test logger integration with other modules."""
    
    def test_logger_singleton_across_modules(self):
        """Test that logger maintains singleton pattern across imports."""
        # Arrange
        logger1 = get_logger("integration_test")
        
        # Simulate another module getting the logger
        logger2 = get_logger("integration_test")
        
        # Assert
        assert logger1 is logger2
        assert id(logger1) == id(logger2)
    
    def test_logger_config_from_environment(self):
        """Test that logger can be configured from environment variables."""
        # Arrange
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'DEBUG',
            'LOG_FILE_PATH': 'test_env.log',
            'DEBUG': 'true'
        }):
            # Act
            config = LogConfig.from_env()
            logger = setup_logger("test_env_config", config)
            
            # Assert
            assert logger.level == LogLevel.DEBUG.value
            assert config.file_path == 'test_env.log'
            assert config.debug_mode is True
    
    def test_logger_rotation(self):
        """Test that logger supports log file rotation."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "rotating.log")
            config = LogConfig(
                file_enabled=True,
                file_path=log_path,
                max_bytes=1024,  # 1KB for testing
                backup_count=3
            )
            logger = setup_logger("test_rotation", config)
            
            # Act - Write enough to trigger rotation
            for i in range(100):
                logger.info(f"Test message {i}" * 10)
            
            # Assert - Check that backup files were created
            log_dir = os.path.dirname(log_path)
            log_files = [f for f in os.listdir(log_dir) if f.startswith("rotating.log")]
            assert len(log_files) > 1  # Original + at least one backup


class TestLoggerPerformance:
    """Test logger performance characteristics."""
    
    def test_logger_async_handling(self):
        """Test that logger doesn't block on heavy I/O operations."""
        # Arrange
        config = LogConfig(
            async_mode=True,
            file_enabled=True,
            file_path="async_test.log"
        )
        logger = setup_logger("test_async", config)
        
        # Act - Log many messages rapidly
        import time
        start_time = time.time()
        for i in range(1000):
            logger.info(f"Async message {i}")
        elapsed = time.time() - start_time
        
        # Assert - Should complete quickly (async)
        assert elapsed < 0.5  # Should be much faster than sync I/O
    
    def test_logger_memory_efficiency(self):
        """Test that logger doesn't cause memory leaks with many messages."""
        # Arrange
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        logger = setup_logger("test_memory")
        
        # Act - Log many messages
        for i in range(10000):
            logger.info(f"Memory test message {i}" * 10)
        
        # Force garbage collection
        gc.collect()
        
        # Assert
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not increase by more than 50MB for 10k messages
        assert memory_increase < 50


# Test fixtures
@pytest.fixture
def clean_logger():
    """Fixture to ensure clean logger state between tests."""
    # Clear any existing loggers
    import logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    yield
    # Cleanup after test
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


@pytest.fixture
def temp_log_file():
    """Fixture to provide temporary log file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path) 