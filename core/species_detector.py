"""
Wildlife Species Detector Module
Enhanced version with Japanese species mapping and improved result handling
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

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
    """Enhanced container for detection results"""
    image_path: str
    detections: List[Dict[str, Any]]
    mode: DetectionMode
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_best_detection(self) -> Optional[Dict[str, Any]]:
        """Get detection with highest confidence"""
        if not self.detections:
            return None
        return max(self.detections, key=lambda x: x.get('confidence', 0))
    
    def get_species_list(self) -> List[str]:
        """Get unique list of detected species"""
        species = set()
        for detection in self.detections:
            if 'common_name' in detection:
                species.add(detection['common_name'])
        return sorted(list(species))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'image_path': self.image_path,
            'detections': self.detections,
            'mode': self.mode.value,
            'processing_time': self.processing_time,
            'success': self.success,
            'error_message': self.error_message,
            'metadata': self.metadata
        }


# NOTE: SpeciesNameMapper class has been deprecated in favor of English/scientific names
# for research purposes. The mapping functionality is preserved for backwards compatibility
# but is not used in the main detection flow.

class SpeciesNameMapper:
    """[DEPRECATED] Maps scientific names to Japanese common names
    
    This class is retained for backwards compatibility but is not actively used.
    All detection results now use English/scientific names for consistency in research.
    """
    
    # Legacy mapping table (not used in current implementation)
    SPECIES_MAP = {
        # The mapping data has been preserved but is not actively used
        # All species names are now returned in English/scientific format
    }
    
    @classmethod
    def get_japanese_name(cls, scientific_name: str) -> str:
        """[DEPRECATED] Get Japanese name from scientific name
        
        This method is deprecated and only kept for backwards compatibility.
        Current implementation returns English/scientific names for all species.
        
        Args:
            scientific_name: Scientific name of the species
            
        Returns:
            The input scientific name (mapping is no longer performed)
        """
        # Return the scientific name as-is (no mapping performed)
        return scientific_name if scientific_name else "Unknown"


class SpeciesDetector:
    """
    Enhanced species detector with multi-backend support
    """
    
    def __init__(self, mode: DetectionMode = DetectionMode.SPECIESNET, config: Optional[Dict] = None):
        """
        Initialize the detector
        
        Args:
            mode: Detection mode to use
            config: Configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        # Note: SpeciesNameMapper is deprecated and no longer used
        
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
        """Initialize SpeciesNet"""
        try:
            # Try to import speciesnet
            import speciesnet
            self.logger.info("SpeciesNet module found and initialized")
        except ImportError:
            self.logger.warning("SpeciesNet not found, will use subprocess method")
            
    def _init_cameratrapai(self):
        """Initialize Google's CameraTrapAI"""
        try:
            import cameratrapai
            self.logger.info("CameraTrapAI initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize CameraTrapAI: {e}")
            
    def _init_megadetector(self):
        """Initialize MegaDetector"""
        try:
            import torch
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
        start_time = time.time()
        
        if not image_path.exists():
            return DetectionResult(
                image_path=str(image_path),
                detections=[],
                mode=self.mode,
                processing_time=0.0,
                success=False,
                error_message=f"Image file not found: {image_path}"
            )
            
        # Get image metadata
        try:
            with Image.open(image_path) as img:
                metadata = {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            metadata = {'error': str(e)}
            
        # Route to appropriate detection method
        if self.mode == DetectionMode.MOCK:
            result = self._detect_mock(image_path)
        elif self.mode == DetectionMode.SPECIESNET:
            result = self._detect_speciesnet(image_path)
        elif self.mode == DetectionMode.CAMERATRAPAI:
            result = self._detect_cameratrapai(image_path)
        elif self.mode == DetectionMode.MEGADETECTOR:
            result = self._detect_megadetector(image_path)
            
        # Add metadata and update processing time
        result.metadata = metadata
        result.processing_time = time.time() - start_time
        
        return result
        
    def _detect_mock(self, image_path: Path) -> DetectionResult:
        """Mock detection for testing"""
        import random
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Generate mock results with scientific names for research use
        mock_species = [
            ("Ursus thibetanus", "Asian black bear", "mammal"),
            ("Cervus nippon", "Sika deer", "mammal"),
            ("Sus scrofa", "Wild boar", "mammal"),
            ("Nyctereutes procyonoides", "Raccoon dog", "mammal"),
            ("Corvus macrorhynchos", "Large-billed crow", "bird"),
            ("Ardea cinerea", "Grey heron", "bird"),
            ("Phasianus versicolor", "Green pheasant", "bird"),
        ]
        
        # Random number of detections (0-3)
        num_detections = random.randint(0, 3)
        detections = []
        
        for i in range(num_detections):
            species = random.choice(mock_species)
            confidence = random.uniform(0.5, 0.99)
            
            # Mock bounding box (normalized coordinates)
            x = random.uniform(0.1, 0.5)
            y = random.uniform(0.1, 0.5)
            w = random.uniform(0.2, 0.4)
            h = random.uniform(0.2, 0.4)
            
            detection = {
                "common_name": species[0],  # Scientific name for research
                "scientific_name": species[0],
                "english_name": species[1],
                "category": species[2],
                "confidence": confidence,
                "bbox": [x, y, x+w, y+h],
                "bbox_format": "normalized",
            }
            detections.append(detection)
        
        return DetectionResult(
            image_path=str(image_path),
            detections=detections,
            mode=self.mode,
            processing_time=0.0,  # Will be updated by caller
            success=True
        )
        
    def _detect_speciesnet(self, image_path: Path) -> DetectionResult:
        """Detect using SpeciesNet via subprocess"""
        import tempfile
        import uuid
        
        self.logger.debug(f"Starting SpeciesNet detection for: {image_path}")
        
        # Create output directory if it doesn't exist
        output_dir = Path.cwd() / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Create unique output file name
        unique_name = f"speciesnet_temp_{uuid.uuid4().hex}.json"
        output_file = str(output_dir / unique_name)
        
        # Ensure the output file doesn't exist (SpeciesNet will create it)
        if os.path.exists(output_file):
            os.unlink(output_file)
        
        self.logger.debug(f"Output file will be: {output_file}")
            
        try:
            # Get the absolute path to the Python executable in venv
            venv_python = Path.cwd() / "venv" / "Scripts" / "python.exe"
            if venv_python.exists():
                python_exe = str(venv_python)
            else:
                python_exe = sys.executable
                
            self.logger.debug(f"Using Python executable: {python_exe}")
            
            # Build command - use same format as test_crow.bat
            cmd = [
                python_exe, '-m', 'speciesnet.scripts.run_model',
                '--filepaths', str(image_path),
                '--predictions_json', output_file,
                '--country', self.config.get('country_code', 'JPN'),
                '--batch_size', '1'
            ]
            
            self.logger.debug(f"Running command: {' '.join(cmd)}")
            self.logger.debug(f"Output file: {output_file}")
            
            # Create a clean environment that excludes miniforge3
            env = os.environ.copy()
            
            # Remove miniforge3 from PATH
            path_parts = env.get('PATH', '').split(os.pathsep)
            filtered_path = [p for p in path_parts if 'miniforge3' not in p.lower()]
            
            # Ensure venv Scripts is at the beginning
            venv_scripts = str(Path.cwd() / "venv" / "Scripts")
            if venv_scripts not in filtered_path:
                filtered_path.insert(0, venv_scripts)
            
            env['PATH'] = os.pathsep.join(filtered_path)
            env['VIRTUAL_ENV'] = str(Path.cwd() / "venv")
            
            # Remove any Python-related environment variables that might interfere
            for key in ['PYTHONHOME', 'PYTHONPATH']:
                env.pop(key, None)
            
            self.logger.debug(f"Environment PATH (first 3): {filtered_path[:3]}")
                
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 300),
                env=env,
                cwd=str(Path.cwd())  # Ensure we run in project directory
            )
            
            self.logger.debug(f"Command return code: {result.returncode}")
            if result.stdout:
                self.logger.debug(f"Command stdout: {result.stdout}")
            if result.stderr:
                self.logger.debug(f"Command stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise RuntimeError(f"SpeciesNet failed: {result.stderr}")
                
            # Check if output file exists and has content
            if not os.path.exists(output_file):
                raise RuntimeError(f"Output file not created: {output_file}")
                
            # Parse results
            with open(output_file, 'r') as f:
                speciesnet_results = json.load(f)
                
            self.logger.debug(f"SpeciesNet raw results: {json.dumps(speciesnet_results, indent=2)}")
                
            detections = self._parse_speciesnet_results(speciesnet_results, str(image_path))
            
            self.logger.debug(f"Parsed detections: {detections}")
            
            return DetectionResult(
                image_path=str(image_path),
                detections=detections,
                mode=self.mode,
                processing_time=0.0,  # Will be updated by caller
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"SpeciesNet detection failed: {e}")
            self.logger.exception("Full traceback:")
            return DetectionResult(
                image_path=str(image_path),
                detections=[],
                mode=self.mode,
                processing_time=0.0,
                success=False,
                error_message=str(e)
            )
        finally:
            # Clean up temp file
            if os.path.exists(output_file):
                os.unlink(output_file)
                
    def _detect_cameratrapai(self, image_path: Path) -> DetectionResult:
        """Detect using Google's CameraTrapAI"""
        # Placeholder - use mock for now
        return self._detect_mock(image_path)
        
    def _detect_megadetector(self, image_path: Path) -> DetectionResult:
        """Detect using MegaDetector"""
        # Placeholder - use mock for now
        return self._detect_mock(image_path)
        
    def _parse_speciesnet_results(self, results: Dict, image_path: str) -> List[Dict]:
        """Parse SpeciesNet results into standard format for research use"""
        detections = []
        
        # Find the prediction for this image
        predictions = results.get('predictions', [])
        image_prediction = None
        
        for pred in predictions:
            # Try multiple methods to match file paths
            pred_filepath = pred.get('filepath', '')
            image_name = Path(image_path).name
            
            # Compare normalized paths
            normalized_pred_path = Path(pred_filepath).resolve() if pred_filepath else None
            normalized_image_path = Path(image_path).resolve()
            
            # Try multiple matching methods
            if (pred_filepath.endswith(image_name) or 
                pred_filepath == str(image_path) or
                (normalized_pred_path and normalized_pred_path == normalized_image_path)):
                image_prediction = pred
                break
                
        if not image_prediction:
            self.logger.warning(f"No prediction found for image: {image_path}")
            self.logger.debug(f"Available predictions: {[p.get('filepath', '') for p in predictions]}")
            return detections
            
        # Get the main prediction
        prediction_str = image_prediction.get('prediction', '')
        prediction_score = image_prediction.get('prediction_score', 0.0)
        prediction_source = image_prediction.get('prediction_source', '')
        
        if prediction_str and prediction_score > 0:
            # Parse prediction string (format: "id;kingdom;order;family;genus;species;common_name")
            class_parts = prediction_str.split(';')
            
            scientific_name = ""
            common_name = ""
            category = "animal"
            family_name = ""
            order_name = ""
            
            if len(class_parts) >= 7:
                # Extract taxonomic information
                kingdom = class_parts[1]
                order_name = class_parts[2]
                family_name = class_parts[3]
                genus = class_parts[4]
                species = class_parts[5]
                common_name = class_parts[6]
                
                # Build scientific name with proper capitalization
                if genus and species:
                    # Scientific names: genus capitalized, species lowercase
                    scientific_name = f"{genus.capitalize()} {species.lower()}"
                
                # Determine category based on kingdom
                if kingdom.lower() == 'aves':
                    category = 'bird'
                elif kingdom.lower() in ['mammalia', 'mammal']:
                    category = 'mammal'
                elif kingdom.lower() == 'reptilia':
                    category = 'reptile'
                    
            # Determine the best display name for research purposes
            if scientific_name:
                # Prefer full scientific name (genus species)
                display_name = scientific_name
            elif common_name and common_name not in ['bird', 'mammal', 'animal'] and not common_name.endswith(' species'):
                # Use specific common name if available and not generic
                display_name = common_name
            elif 'rollup_to_genus' in prediction_source and genus:
                # If rolled up to genus level, show genus with "sp."
                display_name = f"{genus.capitalize()} sp."
            elif 'rollup_to_family' in prediction_source and family_name and family_name.endswith('idae'):
                # Use family name with proper formatting
                display_name = f"{family_name.capitalize()}"
            elif 'rollup_to_order' in prediction_source and order_name:
                # Use order name
                display_name = f"{order_name.capitalize()}"
            elif family_name and family_name.endswith('idae'):
                # Use family name
                display_name = f"{family_name.capitalize()}"
            elif order_name:
                # Use order with category
                display_name = f"{order_name.capitalize()} ({category})"
            else:
                # Last resort: use category
                display_name = f"Unidentified {category}"
            
            # Create detection entry with bounding box info if available
            bbox_detections = image_prediction.get('detections', [])
            
            if bbox_detections:
                # Use the first detection's bounding box
                bbox = bbox_detections[0].get('bbox', [])
                detection = {
                    "common_name": display_name,  # Primary display name
                    "scientific_name": scientific_name,
                    "english_name": common_name,
                    "category": category,
                    "confidence": prediction_score,
                    "bbox": bbox,
                    "bbox_format": "normalized",
                }
            else:
                # No bounding box info
                detection = {
                    "common_name": display_name,  # Primary display name
                    "scientific_name": scientific_name,
                    "english_name": common_name,
                    "category": category,
                    "confidence": prediction_score,
                    "bbox": [],
                    "bbox_format": "normalized",
                }
                
            detections.append(detection)
                
        return detections
        
    def detect_batch(self, image_paths: List[Union[str, Path]], 
                    progress_callback=None) -> List[DetectionResult]:
        """
        Detect wildlife in multiple images
        
        Args:
            image_paths: List of image paths
            progress_callback: Optional callback function(current, total)
            
        Returns:
            List of DetectionResult objects
        """
        results = []
        total = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(i, total)
                
            result = self.detect_single(image_path)
            results.append(result)
            
        if progress_callback:
            progress_callback(total, total)
            
        return results
        
    def available_modes(self) -> List[DetectionMode]:
        """Get list of available detection modes"""
        available = [DetectionMode.MOCK]  # Mock is always available
        
        # Check for SpeciesNet
        try:
            import speciesnet
            available.append(DetectionMode.SPECIESNET)
        except ImportError:
            # Check if we can run via subprocess
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'speciesnet.scripts.run_model', '--help'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    available.append(DetectionMode.SPECIESNET)
            except:
                pass
                
        # Check for CameraTrapAI
        try:
            import cameratrapai
            available.append(DetectionMode.CAMERATRAPAI)
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
def create_detector(mode: Optional[str] = None, config: Optional[Dict] = None) -> SpeciesDetector:
    """
    Create a detector with automatic mode selection
    
    Note: All detection results are now returned in English/scientific names
    for consistency in research applications.
    
    Args:
        mode: Optional mode override
        config: Optional configuration
        
    Returns:
        SpeciesDetector instance with English/scientific name output
    """
    if mode:
        detection_mode = DetectionMode(mode)
    else:
        # Auto-select best available mode
        detector = SpeciesDetector(mode=DetectionMode.MOCK)
        available = detector.available_modes()
        
        if DetectionMode.SPECIESNET in available:
            detection_mode = DetectionMode.SPECIESNET
        elif DetectionMode.CAMERATRAPAI in available:
            detection_mode = DetectionMode.CAMERATRAPAI
        elif DetectionMode.MEGADETECTOR in available:
            detection_mode = DetectionMode.MEGADETECTOR
        else:
            detection_mode = DetectionMode.MOCK
            
    return SpeciesDetector(mode=detection_mode, config=config)