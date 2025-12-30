import logging
import logging.handlers
from pathlib import Path
import os

def setup_logging():
    """Setup comprehensive logging for production."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure file logging
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/tajir_pos.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Configure error file logging
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    # Configure console logging for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    error_handler.setFormatter(error_formatter)
    console_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
