"""
Tests for the wildlife detector module
"""
import pytest
from pathlib import Path
from core.detector import WildlifeDetector, DetectionMode, create_detector

def test_create_detector():
    """Test detector creation"""
    detector = create_detector()
    assert detector is not None
    assert detector.mode in [DetectionMode.MOCK, DetectionMode.SPECIESNET]

def test_mock_detection():
    """Test mock detection mode"""
    detector = WildlifeDetector(mode=DetectionMode.MOCK)
    
    # Create a dummy image path
    test_image = Path("test_image.jpg")
    
    # Run detection
    result = detector.detect_single(test_image)
    
    # Check results
    assert result is not None
    assert result.mode == DetectionMode.MOCK
    assert len(result.detections) > 0
    assert result.success == False  # File doesn't exist
    assert "not found" in result.error_message

def test_available_modes():
    """Test available modes detection"""
    detector = WildlifeDetector(mode=DetectionMode.MOCK)
    modes = detector.available_modes()
    
    assert DetectionMode.MOCK in modes
    # SpeciesNet should be available based on verify_environment.py results
    assert DetectionMode.SPECIESNET in modes
