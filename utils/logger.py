"""
Logging configuration for Wildlife Detector AI
"""
import structlog
import logging
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "wildlife_detector",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    colorize: bool = True
) -> structlog.BoundLogger:
    """
    Set up structured logging
    
    Args:
        name: Logger name
        log_level: Logging level
        log_file: Optional log file path
        colorize: Whether to colorize console output
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer() if colorize else structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set up Python logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file) if log_file else logging.NullHandler()
        ]
    )
    
    return structlog.get_logger(name)
