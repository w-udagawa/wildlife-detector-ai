"""
Batch Processing Engine for Wildlife Detector
Handles parallel processing of multiple images with progress tracking
"""

import os
import logging
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from .species_detector import SpeciesDetector, DetectionResult, create_detector


@dataclass
class ProcessingStats:
    """Statistics for batch processing"""
    total_images: int = 0
    processed_images: int = 0
    successful_detections: int = 0
    failed_detections: int = 0
    total_detections: int = 0
    processing_time: float = 0.0
    errors: List[Dict[str, str]] = field(default_factory=list)
    species_counts: Dict[str, int] = field(default_factory=dict)
    
    @property
    def average_time_per_image(self) -> float:
        """Calculate average processing time per image"""
        if self.processed_images == 0:
            return 0.0
        return self.processing_time / self.processed_images
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.processed_images == 0:
            return 0.0
        return (self.successful_detections / self.processed_images) * 100
    
    def update_species_count(self, species_name: str):
        """Update species count"""
        if species_name:
            self.species_counts[species_name] = self.species_counts.get(species_name, 0) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total_images': self.total_images,
            'processed_images': self.processed_images,
            'successful_detections': self.successful_detections,
            'failed_detections': self.failed_detections,
            'total_detections': self.total_detections,
            'processing_time': self.processing_time,
            'average_time_per_image': self.average_time_per_image,
            'success_rate': self.success_rate,
            'errors': self.errors,
            'species_counts': self.species_counts
        }


class BatchProcessor:
    """
    Batch processor for wildlife detection
    Supports parallel processing with progress tracking
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize batch processor
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Processing parameters
        self.max_workers = config.get('max_workers', 4)
        self.batch_size = config.get('batch_size', 10)
        self.use_gpu = config.get('use_gpu', False)
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        
        # State
        self.detector = None
        self.is_cancelled = False
        self.progress_queue = queue.Queue()
        self.stats = ProcessingStats()
        
        # Thread safety
        self.stats_lock = threading.Lock()
        
    def initialize(self, progress_callback: Optional[Callable] = None) -> bool:
        """
        Initialize the detector
        
        Args:
            progress_callback: Optional callback for initialization progress
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if progress_callback:
                progress_callback("検出器を初期化しています...")
                
            # Create detector with configuration
            detector_config = {
                'country_code': self.config.get('country_code', 'JPN'),
                'timeout': self.config.get('timeout', 300),
                'batch_size': self.batch_size
            }
            
            self.detector = create_detector(config=detector_config)
            
            if progress_callback:
                progress_callback("検出器の初期化が完了しました")
                
            self.logger.info("Batch processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize batch processor: {e}")
            if progress_callback:
                progress_callback(f"初期化エラー: {str(e)}")
            return False
    
    def process_batch(self, 
                     image_paths: List[str], 
                     progress_callback: Optional[Callable] = None) -> List[DetectionResult]:
        """
        Process batch of images
        
        Args:
            image_paths: List of image file paths
            progress_callback: Optional callback(current, total, status, filename)
            
        Returns:
            List of DetectionResult objects
        """
        if not self.detector:
            raise RuntimeError("Detector not initialized. Call initialize() first.")
            
        # Reset state
        self.is_cancelled = False
        self.stats = ProcessingStats(total_images=len(image_paths))
        
        # Start processing
        start_time = time.time()
        results = []
        
        try:
            if self.max_workers == 1:
                # Sequential processing
                results = self._process_sequential(image_paths, progress_callback)
            else:
                # Parallel processing
                results = self._process_parallel(image_paths, progress_callback)
                
        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")
            raise
            
        finally:
            # Update total processing time
            self.stats.processing_time = time.time() - start_time
            
        return results
    
    def _process_sequential(self, 
                          image_paths: List[str], 
                          progress_callback: Optional[Callable]) -> List[DetectionResult]:
        """Process images sequentially"""
        results = []
        
        for i, image_path in enumerate(image_paths):
            if self.is_cancelled:
                break
                
            # Update progress
            if progress_callback:
                filename = Path(image_path).name
                progress_callback(i, len(image_paths), "処理中", filename)
            
            # Process image
            result = self._process_single_image(image_path)
            results.append(result)
            
            # Update stats
            self._update_stats(result)
            
        # Final progress update
        if progress_callback:
            progress_callback(len(results), len(image_paths), "完了", "")
            
        return results
    
    def _process_parallel(self, 
                        image_paths: List[str], 
                        progress_callback: Optional[Callable]) -> List[DetectionResult]:
        """Process images in parallel"""
        results = []
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._process_single_image, path): path 
                for path in image_paths
            }
            
            # Process completed tasks
            for future in as_completed(future_to_path):
                if self.is_cancelled:
                    # Cancel remaining tasks
                    for f in future_to_path:
                        f.cancel()
                    break
                    
                path = future_to_path[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    self._update_stats(result)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {path}: {e}")
                    # Create error result
                    result = DetectionResult(
                        image_path=path,
                        detections=[],
                        mode=self.detector.mode,
                        processing_time=0.0,
                        success=False,
                        error_message=str(e)
                    )
                    results.append(result)
                    self._update_stats(result)
                
                # Update progress
                processed_count += 1
                if progress_callback:
                    filename = Path(path).name
                    progress_callback(processed_count, len(image_paths), "処理中", filename)
        
        # Final progress update
        if progress_callback:
            progress_callback(len(results), len(image_paths), "完了", "")
            
        return results
    
    def _process_single_image(self, image_path: str) -> DetectionResult:
        """Process a single image"""
        try:
            # Check file size
            file_size_mb = Path(image_path).stat().st_size / (1024 * 1024)
            max_size_mb = self.config.get('max_image_size_mb', 50.0)
            
            if file_size_mb > max_size_mb:
                raise ValueError(f"Image file too large: {file_size_mb:.1f}MB (max: {max_size_mb}MB)")
            
            # Detect species
            result = self.detector.detect_single(image_path)
            
            # Filter by confidence threshold
            if result.success and result.detections:
                filtered_detections = [
                    det for det in result.detections 
                    if det.get('confidence', 0) >= self.confidence_threshold
                ]
                result.detections = filtered_detections
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {image_path}: {e}")
            return DetectionResult(
                image_path=image_path,
                detections=[],
                mode=self.detector.mode if self.detector else None,
                processing_time=0.0,
                success=False,
                error_message=str(e)
            )
    
    def _update_stats(self, result: DetectionResult):
        """Update processing statistics"""
        with self.stats_lock:
            self.stats.processed_images += 1
            
            if result.success:
                self.stats.successful_detections += 1
                self.stats.total_detections += len(result.detections)
                
                # Update species counts
                for detection in result.detections:
                    species_name = detection.get('common_name', '不明')
                    self.stats.update_species_count(species_name)
            else:
                self.stats.failed_detections += 1
                if result.error_message:
                    self.stats.errors.append({
                        'image': result.image_path,
                        'error': result.error_message
                    })
    
    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.is_cancelled = True
        self.logger.info("Batch processing cancelled")
    
    def get_statistics(self) -> ProcessingStats:
        """Get current processing statistics"""
        with self.stats_lock:
            return self.stats
    
    def cleanup(self):
        """Cleanup resources"""
        self.detector = None
        self.progress_queue = queue.Queue()
        self.logger.info("Batch processor cleaned up")
    
    def estimate_processing_time(self, num_images: int) -> float:
        """
        Estimate processing time for given number of images
        
        Args:
            num_images: Number of images to process
            
        Returns:
            Estimated time in seconds
        """
        # Based on average processing time or default estimate
        avg_time = self.stats.average_time_per_image if self.stats.processed_images > 0 else 2.0
        
        # Account for parallelization
        if self.max_workers > 1:
            estimated_time = (num_images * avg_time) / self.max_workers
        else:
            estimated_time = num_images * avg_time
            
        # Add some buffer
        return estimated_time * 1.2