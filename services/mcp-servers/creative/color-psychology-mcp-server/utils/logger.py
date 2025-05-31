#!/usr/bin/env python3
"""
Winston-style modular logging utility for VividWalls Color Palette Agent.

This module provides:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console output with rotation support
- Structured logging format (JSON optional)
- Environment-based configuration
- Singleton pattern for consistent logging across modules
- Async logging support for performance
"""

import os
import sys
import logging
import logging.handlers
import json
import queue
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import threading

# Import required for structured logging
from pythonjsonlogger import jsonlogger

# Global logger registry for singleton pattern
_logger_registry: Dict[str, logging.Logger] = {}
_registry_lock = threading.Lock()


class LogLevel(Enum):
    """Log level enumeration matching Python's logging levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogConfig:
    """Configuration for logger setup."""
    level: LogLevel = LogLevel.INFO
    console_enabled: bool = True
    file_enabled: bool = False
    file_path: str = "logs/app.log"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    structured: bool = False  # Enable JSON structured logging
    max_bytes: int = 10 * 1024 * 1024  # 10MB default
    backup_count: int = 5
    async_mode: bool = False
    debug_mode: bool = False
    
    @classmethod
    def from_env(cls) -> 'LogConfig':
        """Create configuration from environment variables."""
        # Map string log level to enum
        level_map = {
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'WARNING': LogLevel.WARNING,
            'ERROR': LogLevel.ERROR,
            'CRITICAL': LogLevel.CRITICAL
        }
        
        level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
        level = level_map.get(level_str, LogLevel.INFO)
        
        return cls(
            level=level,
            file_enabled=os.environ.get('LOG_FILE_PATH') is not None,
            file_path=os.environ.get('LOG_FILE_PATH', 'logs/app.log'),
            debug_mode=os.environ.get('DEBUG', 'false').lower() == 'true',
            structured=os.environ.get('LOG_STRUCTURED', 'false').lower() == 'true'
        )


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level as string
        log_record['level'] = record.levelname
        
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'message', 'pathname', 'process', 'processName', 
                          'relativeCreated', 'stack_info', 'thread', 'threadName', 
                          'exc_info', 'exc_text']:
                log_record[key] = value


def setup_logger(name: str, config: Optional[LogConfig] = None) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Logger name (typically module name)
        config: Logger configuration. If None, uses default configuration.
    
    Returns:
        Configured logger instance
    """
    global _logger_registry
    
    # Use default config if none provided
    if config is None:
        config = LogConfig()
    
    with _registry_lock:
        # Return existing logger if already configured
        if name in _logger_registry:
            return _logger_registry[name]
        
        # Create new logger
        logger = logging.getLogger(name)
        logger.setLevel(config.level.value)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Configure formatters
        if config.structured:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(config.format)
        
        # Add console handler if enabled
        if config.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.name = "console"
            logger.addHandler(console_handler)
        
        # Add file handler if enabled
        if config.file_enabled:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(config.file_path)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler
            if config.async_mode:
                # Use queue handler for async logging
                log_queue = queue.Queue()
                queue_handler = logging.handlers.QueueHandler(log_queue)
                queue_handler.name = "file"
                logger.addHandler(queue_handler)
                
                # Set up queue listener with rotating file handler
                file_handler = logging.handlers.RotatingFileHandler(
                    config.file_path,
                    maxBytes=config.max_bytes,
                    backupCount=config.backup_count
                )
                file_handler.setFormatter(formatter)
                
                queue_listener = logging.handlers.QueueListener(
                    log_queue,
                    file_handler,
                    respect_handler_level=True
                )
                queue_listener.start()
                
                # Store listener for cleanup
                logger._queue_listener = queue_listener
            else:
                # Use standard rotating file handler
                file_handler = logging.handlers.RotatingFileHandler(
                    config.file_path,
                    maxBytes=config.max_bytes,
                    backupCount=config.backup_count
                )
                file_handler.setFormatter(formatter)
                file_handler.name = "file"
                logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        # Store in registry
        _logger_registry[name] = logger
        
        # Log initialization
        logger.info(f"Logger '{name}' initialized with level {config.level.name}")
        
        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default configuration.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    with _registry_lock:
        if name in _logger_registry:
            return _logger_registry[name]
        else:
            # Create with default configuration
            return setup_logger(name)


def cleanup_loggers():
    """Clean up all loggers and stop any async handlers."""
    global _logger_registry
    
    with _registry_lock:
        for logger in _logger_registry.values():
            # Stop any queue listeners
            if hasattr(logger, '_queue_listener'):
                logger._queue_listener.stop()
            
            # Clear handlers
            logger.handlers.clear()
        
        # Clear registry
        _logger_registry.clear()


# Set up module-level logger
_module_logger = setup_logger(__name__)


def log_function_call(func):
    """
    Decorator to log function calls with arguments and return values.
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            return result
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            # Call the function
            result = func(*args, **kwargs)
            
            # Log successful return
            logger.debug(f"Exiting {func.__name__} with result={result}")
            
            return result
        except Exception as e:
            # Log exception
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


# Example usage for module initialization
if __name__ == "__main__":
    # Example of setting up a logger
    config = LogConfig(
        level=LogLevel.DEBUG,
        file_enabled=True,
        file_path="logs/example.log",
        structured=True
    )
    
    logger = setup_logger("example", config)
    
    # Log some example messages
    logger.debug("Debug message with extra data", extra={"user_id": 123})
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    try:
        raise ValueError("Example exception")
    except ValueError:
        logger.exception("Caught an exception")
    
    # Cleanup
    cleanup_loggers() 