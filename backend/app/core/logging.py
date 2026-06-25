"""
Logging configuration
"""
import logging
import sys
from datetime import datetime


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure application logging"""
    logger = logging.getLogger("interview_api")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


logger = setup_logging()
