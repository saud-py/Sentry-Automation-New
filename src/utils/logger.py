"""
Logging utilities for Sentry Alert Automation.

This module provides a centralized logging configuration
for consistent logging across all modules.
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "sentry_alerts", level: str = None) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: The logger name
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Find the project root directory (where logs/ directory should be)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # Go up from src/utils/ to project root
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler for all logs with UTF-8 encoding
    log_file = logs_dir / "sentry_alerts.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'  # Add UTF-8 encoding for Windows
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler with UTF-8 encoding
    error_log_file = logs_dir / "sentry_alerts_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'  # Add UTF-8 encoding for Windows
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: The logger name (optional)
    
    Returns:
        Logger instance
    """
    if name is None:
        name = "sentry_alerts"
    
    return logging.getLogger(name)

def log_function_call(func):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        func: The function to decorate
    
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        # Log function call
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func_name} raised exception: {e}")
            raise
    
    return wrapper

def log_execution_time(func):
    """
    Decorator to log function execution time.
    
    Args:
        func: The function to decorate
    
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func_name} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func_name} failed after {execution_time:.2f} seconds: {e}")
            raise
    
    return wrapper

class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self):
        """Get a logger instance for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def log_debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def log_exception(self, message: str, exc_info=True):
        """Log an exception with traceback."""
        self.logger.exception(message, exc_info=exc_info) 