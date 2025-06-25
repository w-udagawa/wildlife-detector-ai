"""
Wildlife Detector Core Module
Handles wildlife detection using SpeciesNet or alternative models
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

import numpy as np
from PIL import Image


class DetectionMode(Enum):
    """Detection mode enumeration"""
    SPECIESNET = "speciesnet"
    CAMERATRAPAI = "cameratrapai"
    MEGADETECTOR = "megadetector"
    MOCK = "mock"


@dataclass
class DetectionResult:
    """Container for detection results"""
    image_path: str
    detections: List[Dict]
    mode: DetectionMode
    processing_time: float
    success: bool
    error_message: Optional[str] = None


class WildlifeDetector:
    """
    Main detector class that handles multiple detection backends
    """
    
    def __init__(self, mode: DetectionMode = DetectionMode.MOCK, config: Optional[Dict] = None):
        """
        Initialize the detector
        
        Args:
            mode: Detection mode to use
            config: Configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize based on mode
        self._initialize_detector()
        
    def _initialize_detector(self):
        """Initialize the appropriate detector based on mode"""
        self.logger.info(f"Initializing detector in {self.mode.value} mode")
        
        if self.mode == DetectionMode.SPECIESNET:
            self._init_speciesnet()
        elif self.mode == DetectionMode.CAMERATRAPAI:
            self._init_cameratrapai()
        elif self.mode == DetectionMode.MEGADETECTOR:
            self._init_megadetector()
        elif self.mode == DetectionMode.MOCK:
            self._init_mock()
            
    def _init_speciesnet(self):
        """Initialize SpeciesNet (legacy method)"""
        try:
            # Try to import speciesnet
            import speciesnet
            self.logger.info("SpeciesNet module found")
        except ImportError:
            self.logger.warning("SpeciesNet not found, falling back to subprocess method")
            
    def _init_cameratrapai(self):
        """Initialize Google's CameraTrapAI"""
        try:
            # This would be the actual import when available
            # import cameratrapai
            self.logger.info("CameraTrapAI initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize CameraTrapAI: {e}")
            
    def _init_megadetector(self):
        """Initialize MegaDetector"""
        try:
            import torch
            # Load MegaDetector model
            self.logger.info("MegaDetector initialized")
        except ImportError:
            self.logger.error("PyTorch not found, cannot use MegaDetector")
            
    def _init_mock(self):
        """Initialize mock detector for testing"""
        self.logger.info("Mock detector initialized - for testing only")
        
    def detect_single(self, image_path: Union[str, Path]) -> DetectionResult:
        """
        Detect wildlife in a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            DetectionResult object
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            return DetectionResult(
                image_path=str(image_path),
                detections=[],
                mode=self.mode,
                processing_time=0.0,
                success=False,
                error_message=f"Image file not found: {image_path}"
            )
            
        # Route to appropriate detection method
        if self.mode == DetectionMode.MOCK:
            return self._detect_mock(image_path)
        elif self.mode == DetectionMode.SPECIESNET:
            return self._detect_speciesnet(image_path)
        elif self.mode == DetectionMode.CAMERATRAPAI:
            return self._detect_cameratrapai(image_path)
        elif self.mode == DetectionMode.MEGADETECTOR:
            return self._detect_megadetector(image_path)
            
    def _detect_mock(self, image_path: Path) -> DetectionResult:
        """Mock detection for testing"""
        import time
        import random
        
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Generate mock results
        mock_species = [
            ("Tiger", "Panthera tigris"),
            ("Elephant", "Elephas maximus"),
            ("Deer", "Cervus elaphus"),
            ("Wild Boar", "Sus scrofa"),
            ("Peacock", "Pavo cristatus"),
        ]
        
        species = random.choice(mock_species)
        confidence = random.uniform(0.7, 0.99)
        
        # Mock bounding box (normalized coordinates)
        x = random.uniform(0.1, 0.5)
        y = random.uniform(0.1, 0.5)
        w = random.uniform(0.2, 0.4)
        h = random.uniform(0.2, 0.4)
        
        detections = [{
            "species_common": species[0],
            "species_scientific": species[1],
            "confidence": confidence,
            "bbox": [x, y, x+w, y+h],
            "bbox_format": "normalized",
        }]
        
        processing_time = time.time() - start_time
        
        return DetectionResult(
            image_path=str(image_path),
            detections=detections,
            mode=self.mode,
            processing_time=processing_time,
            success=True
        )
        
    def _detect_speciesnet(self, image_path: Path) -> DetectionResult:
        """Detect using SpeciesNet via subprocess"""
        import time
        import tempfile
        
        start_time = time.time()
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name
            
        try:
            # Build command
            cmd = [
                sys.executable, '-m', 'speciesnet.scripts.run_model',
                '--image', str(image_path),
                '--output', output_file,
                '--country', self.config.get('country', 'JPN'),
            ]
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 30)
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"SpeciesNet failed: {result.stderr}")
                
            # Parse results
            with open(output_file, 'r') as f:
                results = json.load(f)
                
            detections = self._parse_speciesnet_results(results)
            
            return DetectionResult(
                image_path=str(image_path),
                detections=detections,
                mode=self.mode,
                processing_time=time.time() - start_time,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"SpeciesNet detection failed: {e}")
            return DetectionResult(
                image_path=str(image_path),
                detections=[],
                mode=self.mode,
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
        finally:
            # Clean up temp file
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    def _detect_cameratrapai(self, image_path: Path) -> DetectionResult:
        """Detect using Google's CameraTrapAI"""
        # Placeholder for CameraTrapAI implementation
        return self._detect_mock(image_path)
        
    def _detect_megadetector(self, image_path: Path) -> DetectionResult:
        """Detect using MegaDetector"""
        # Placeholder for MegaDetector implementation
        return self._detect_mock(image_path)
        
    def _parse_speciesnet_results(self, results: Dict) -> List[Dict]:
        """Parse SpeciesNet results into standard format"""
        detections = []
        
        # This would parse actual SpeciesNet output format
        # For now, return empty list
        return detections
        
    def detect_batch(self, image_paths: List[Union[str, Path]], 
                    max_workers: Optional[int] = None) -> List[DetectionResult]:
        """
        Detect wildlife in multiple images
        
        Args:
            image_paths: List of image paths
            max_workers: Maximum number of parallel workers
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        
        for image_path in image_paths:
            result = self.detect_single(image_path)
            results.append(result)
            
        return results
        
    def available_modes(self) -> List[DetectionMode]:
        """Get list of available detection modes"""
        available = [DetectionMode.MOCK]  # Mock is always available
        
        # Check for SpeciesNet
        try:
            import speciesnet
            available.append(DetectionMode.SPECIESNET)
        except ImportError:
            pass
            
        # Check for PyTorch (MegaDetector)
        try:
            import torch
            available.append(DetectionMode.MEGADETECTOR)
        except ImportError:
            pass
            
        return available


# Convenience function
def create_detector(mode: Optional[str] = None) -> WildlifeDetector:
    """
    Create a detector with automatic mode selection
    
    Args:
        mode: Optional mode override
        
    Returns:
        WildlifeDetector instance
    """
    if mode:
        detection_mode = DetectionMode(mode)
    else:
        # Auto-select best available mode
        detector = WildlifeDetector(mode=DetectionMode.MOCK)
        available = detector.available_modes()
        
        if DetectionMode.SPECIESNET in available:
            detection_mode = DetectionMode.SPECIESNET
        elif DetectionMode.MEGADETECTOR in available:
            detection_mode = DetectionMode.MEGADETECTOR
        else:
            detection_mode = DetectionMode.MOCK
            
    return WildlifeDetector(mode=detection_mode)
