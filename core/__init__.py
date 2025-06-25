"""
Wildlife Detector AI v2.0
Core package for wildlife detection functionality
"""

__version__ = "2.0.0"
__author__ = "Wildlife Detector AI Team"

from .config import ConfigManager, AppConfig
from .species_detector import SpeciesDetector, DetectionResult, create_detector
from .batch_processor import BatchProcessor, ProcessingStats

# Legacy support
try:
    from .detector import WildlifeDetector
except ImportError:
    pass

__all__ = [
    "ConfigManager",
    "AppConfig",
    "SpeciesDetector",
    "DetectionResult",
    "create_detector",
    "BatchProcessor",
    "ProcessingStats",
    "WildlifeDetector",  # Legacy
]
