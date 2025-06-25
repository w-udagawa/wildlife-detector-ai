"""
CSV Export Module for Wildlife Detector
Exports detection results and statistics to CSV format
"""

import csv
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import ast

from core.species_detector import DetectionResult, DetectionMode
from core.batch_processor import ProcessingStats


class CSVExporter:
    """
    Exports detection results to CSV format
    """
    
    def __init__(self, output_directory: str = "output"):
        """
        Initialize CSV exporter
        
        Args:
            output_directory: Directory to save CSV files
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def export_all(self, 
                   results: List[DetectionResult], 
                   stats: Optional[ProcessingStats] = None) -> Dict[str, str]:
        """
        Export all results to CSV files
        
        Args:
            results: List of detection results
            stats: Optional processing statistics
            
        Returns:
            Dictionary of output file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_files = {}
        
        try:
            # Export detailed results
            details_file = self.export_detailed_results(results, timestamp)
            output_files['detailed_results'] = details_file
            
            # Export summary
            summary_file = self.export_summary(results, stats, timestamp)
            output_files['summary'] = summary_file
            
            # Export species statistics
            species_file = self.export_species_stats(results, timestamp)
            output_files['species_stats'] = species_file
            
            # Export errors if any
            if stats and stats.errors:
                errors_file = self.export_errors(stats.errors, timestamp)
                output_files['errors'] = errors_file
                
            self.logger.info(f"CSV export completed: {len(output_files)} files created")
            
        except Exception as e:
            self.logger.error(f"CSV export error: {e}")
            raise
            
        return output_files
    
    def export_detailed_results(self, 
                               results: List[DetectionResult], 
                               timestamp: str) -> str:
        """Export detailed detection results"""
        filename = f"wildlife_detection_results_{timestamp}.csv"
        filepath = self.output_directory / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'Image File', 
                'Detection Count', 
                'Species Name', 
                'Scientific Name',
                'Common Name',
                'Category',
                'Confidence', 
                'Bounding Box',
                'Processing Time (s)',
                'Status',
                'Error Message'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                if not result.detections:
                    # No detections or failed
                    writer.writerow({
                        'Image File': Path(result.image_path).name,
                        'Detection Count': 0,
                        'Species Name': 'No detection' if result.success else 'Error',
                        'Scientific Name': '',
                        'Common Name': '',
                        'Category': '',
                        'Confidence': '',
                        'Bounding Box': '',
                        'Processing Time (s)': f"{result.processing_time:.3f}",
                        'Status': 'Success' if result.success else 'Failed',
                        'Error Message': result.error_message or ''
                    })
                else:
                    # Write row for each detection
                    for detection in result.detections:
                        bbox_str = self._format_bbox(detection.get('bbox', []))
                        
                        writer.writerow({
                            'Image File': Path(result.image_path).name,
                            'Detection Count': len(result.detections),
                            'Species Name': detection.get('common_name', 'Unknown'),
                            'Scientific Name': detection.get('scientific_name', ''),
                            'Common Name': detection.get('english_name', ''),
                            'Category': detection.get('category', ''),
                            'Confidence': f"{detection.get('confidence', 0):.3f}",
                            'Bounding Box': bbox_str,
                            'Processing Time (s)': f"{result.processing_time:.3f}",
                            'Status': 'Success',
                            'Error Message': ''
                        })
        
        self.logger.info(f"Detailed results exported to: {filepath}")
        return str(filepath)
    
    def export_summary(self, 
                      results: List[DetectionResult], 
                      stats: Optional[ProcessingStats],
                      timestamp: str) -> str:
        """Export processing summary"""
        filename = f"wildlife_detection_summary_{timestamp}.csv"
        filepath = self.output_directory / filename
        
        # Calculate summary statistics
        total_images = len(results)
        successful_detections = sum(1 for r in results if r.success and r.detections)
        failed_detections = sum(1 for r in results if not r.success)
        total_animals = sum(len(r.detections) for r in results if r.success)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Wildlife Detector Processing Summary'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Write statistics
            writer.writerow(['Item', 'Value'])
            writer.writerow(['Total Images', total_images])
            writer.writerow(['Successful Detections', successful_detections])
            writer.writerow(['Failed Detections', failed_detections])
            writer.writerow(['Total Animals Detected', total_animals])
            
            if stats:
                writer.writerow(['Processing Time (s)', f"{stats.processing_time:.2f}"])
                writer.writerow(['Average Time per Image (s)', f"{stats.average_time_per_image:.3f}"])
                writer.writerow(['Success Rate (%)', f"{stats.success_rate:.1f}"])
                
            writer.writerow([])
            
            # Write species summary
            if stats and stats.species_counts:
                writer.writerow(['Species Detection Statistics'])
                writer.writerow(['Species Name', 'Detection Count'])
                for species, count in sorted(stats.species_counts.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True):
                    writer.writerow([species, count])
        
        self.logger.info(f"Summary exported to: {filepath}")
        return str(filepath)
    
    def export_species_stats(self, 
                           results: List[DetectionResult], 
                           timestamp: str) -> str:
        """Export species statistics"""
        filename = f"wildlife_species_stats_{timestamp}.csv"
        filepath = self.output_directory / filename
        
        # Collect species statistics
        species_data = {}
        
        for result in results:
            if result.success:
                for detection in result.detections:
                    species = detection.get('common_name', 'Unknown')
                    scientific = detection.get('scientific_name', '')
                    confidence = detection.get('confidence', 0)
                    
                    if species not in species_data:
                        species_data[species] = {
                            'scientific_name': scientific,
                            'count': 0,
                            'confidences': [],
                            'images': set()
                        }
                    
                    species_data[species]['count'] += 1
                    species_data[species]['confidences'].append(confidence)
                    species_data[species]['images'].add(Path(result.image_path).name)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'Species Name',
                'Scientific Name',
                'Total Detections',
                'Images with Detection',
                'Average Confidence',
                'Maximum Confidence',
                'Minimum Confidence'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Sort by detection count
            sorted_species = sorted(species_data.items(), 
                                  key=lambda x: x[1]['count'], 
                                  reverse=True)
            
            for species, data in sorted_species:
                confidences = data['confidences']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                writer.writerow({
                    'Species Name': species,
                    'Scientific Name': data['scientific_name'],
                    'Total Detections': data['count'],
                    'Images with Detection': len(data['images']),
                    'Average Confidence': f"{avg_confidence:.3f}",
                    'Maximum Confidence': f"{max(confidences):.3f}" if confidences else '',
                    'Minimum Confidence': f"{min(confidences):.3f}" if confidences else ''
                })
        
        self.logger.info(f"Species statistics exported to: {filepath}")
        return str(filepath)
    
    def export_errors(self, errors: List[Dict[str, str]], timestamp: str) -> str:
        """Export error log"""
        filename = f"wildlife_detection_errors_{timestamp}.csv"
        filepath = self.output_directory / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['Image File', 'Error Details']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for error in errors:
                writer.writerow({
                    'Image File': Path(error['image']).name,
                    'Error Details': error['error']
                })
        
        self.logger.info(f"Error log exported to: {filepath}")
        return str(filepath)
    
    def export_simple_list(self, results: List[DetectionResult], timestamp: str) -> str:
        """Export simple species list"""
        filename = f"wildlife_species_list_{timestamp}.csv"
        filepath = self.output_directory / filename
        
        # Collect unique species
        all_species = set()
        
        for result in results:
            if result.success:
                for detection in result.detections:
                    species = detection.get('common_name', 'Unknown')
                    if species and species != 'Unknown':
                        all_species.add(species)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Detected Species List'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            for species in sorted(all_species):
                writer.writerow([species])
        
        self.logger.info(f"Species list exported to: {filepath}")
        return str(filepath)
    
    def _format_bbox(self, bbox: List[float]) -> str:
        """Format bounding box coordinates"""
        if not bbox or len(bbox) < 4:
            return ""
        
        # Format as "x1,y1,x2,y2"
        return f"{bbox[0]:.3f},{bbox[1]:.3f},{bbox[2]:.3f},{bbox[3]:.3f}"
    
    def _parse_bbox(self, bbox_str: str) -> List[float]:
        """Parse bounding box coordinates from string"""
        if not bbox_str:
            return []
        
        try:
            parts = bbox_str.split(',')
            if len(parts) >= 4:
                return [float(x) for x in parts[:4]]
        except:
            pass
        return []
    
    def import_from_csv(self, csv_filepath: str) -> List[DetectionResult]:
        """Import detection results from CSV file
        
        Args:
            csv_filepath: Path to the CSV file containing detection results
            
        Returns:
            List of DetectionResult objects reconstructed from CSV
        """
        # Dictionary to store detections grouped by image file
        image_detections = {}
        
        try:
            with open(csv_filepath, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    image_file = row.get('Image File', '')
                    if not image_file:
                        continue
                    
                    # Initialize entry for this image if not exists
                    if image_file not in image_detections:
                        image_detections[image_file] = {
                            'detections': [],
                            'processing_time': float(row.get('Processing Time (s)', '0')),
                            'status': row.get('Status', ''),
                            'error_message': row.get('Error Message', '') or None
                        }
                    
                    # Parse detection data
                    if row.get('Status', '') == 'Success' and int(row.get('Detection Count', '0')) > 0:
                        species_name = row.get('Species Name', '')
                        if species_name and species_name != 'No detection':
                            detection = {
                                'common_name': species_name,
                                'scientific_name': row.get('Scientific Name', ''),
                                'english_name': row.get('Common Name', ''),
                                'category': row.get('Category', ''),
                                'confidence': float(row.get('Confidence', '0')),
                                'bbox': self._parse_bbox(row.get('Bounding Box', '')),
                                'bbox_format': 'normalized'
                            }
                            image_detections[image_file]['detections'].append(detection)
            
            # Convert to DetectionResult objects
            results = []
            for image_path, data in image_detections.items():
                result = DetectionResult(
                    image_path=image_path,
                    detections=data['detections'],
                    mode=DetectionMode.SPECIESNET,
                    processing_time=data['processing_time'],
                    success=data['status'] == 'Success',
                    error_message=data['error_message']
                )
                results.append(result)
            
            self.logger.info(f"Imported {len(results)} detection results from {csv_filepath}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error importing CSV: {e}")
            raise