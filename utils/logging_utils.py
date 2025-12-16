"""
Logging utility functions
"""

import logging
import os
from datetime import datetime
from typing import Optional

def setup_logging(log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_dir: Directory for log files
        level: Logging level
    
    Returns:
        Root logger
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"android_root_suite_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
