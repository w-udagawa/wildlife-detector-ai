"""
File management utilities for Wildlife Detector AI
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
import hashlib


class FileManager:
    """Handles file operations for the application"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.logger = logging.getLogger(__name__)
        
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """Ensure a directory exists"""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def get_image_files(self, directory: Union[str, Path], 
                       extensions: Optional[List[str]] = None,
                       recursive: bool = True) -> List[Path]:
        """Get all image files in a directory"""
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
            
        directory = Path(directory)
        image_files = []
        
        # Use rglob for recursive search, glob for non-recursive
        glob_func = directory.rglob if recursive else directory.glob
        
        for ext in extensions:
            image_files.extend(glob_func(f'*{ext}'))
            image_files.extend(glob_func(f'*{ext.upper()}'))
            
        # Remove duplicates and sort
        image_files = list(set(image_files))
        return sorted(image_files)
        
    def copy_with_structure(self, source: Path, dest_base: Path, 
                          preserve_structure: bool = True) -> Path:
        """Copy file preserving directory structure"""
        if preserve_structure:
            try:
                relative = source.relative_to(self.base_path)
                dest = dest_base / relative
            except ValueError:
                # If source is not relative to base_path, just use filename
                dest = dest_base / source.name
        else:
            dest = dest_base / source.name
            
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return dest
        
    def get_file_hash(self, file_path: Union[str, Path]) -> str:
        """Calculate SHA256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def organize_images_by_species(self, 
                                 detection_results: List[Any],
                                 output_base: Optional[str] = None,
                                 copy_files: bool = True,
                                 confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Organize images into folders by detected species
        
        Args:
            detection_results: List of DetectionResult objects
            output_base: Base directory for organized files
            copy_files: If True, copy files; if False, move files
            confidence_threshold: Minimum confidence for species assignment
            
        Returns:
            Dictionary with organization results
        """
        if output_base is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_base = self.base_path / f"organized_{timestamp}"
        else:
            output_base = Path(output_base)
            
        output_base = self.ensure_directory(output_base)
        
        # Create species folders and organize files
        organized_count = 0
        total_count = len(detection_results)
        species_folders = {}
        errors = []
        
        for result in detection_results:
            try:
                if not result.success or not result.detections:
                    # No detection - put in "no_detection" folder
                    species_folder = output_base / "no_detection"
                    species_folder.mkdir(exist_ok=True)
                    
                    src_path = Path(result.image_path)
                    if src_path.exists():
                        dest_path = species_folder / src_path.name
                        if copy_files:
                            shutil.copy2(src_path, dest_path)
                        else:
                            shutil.move(str(src_path), str(dest_path))
                        organized_count += 1
                    continue
                
                # Get best detection above threshold
                best_detection = None
                for detection in result.detections:
                    if detection.get('confidence', 0) >= confidence_threshold:
                        if best_detection is None or detection['confidence'] > best_detection['confidence']:
                            best_detection = detection
                
                if best_detection:
                    # Create species folder
                    species_name = best_detection.get('common_name', 'Unknown')
                    # Sanitize folder name
                    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                                      for c in species_name).strip()
                    
                    species_folder = output_base / safe_name
                    species_folder.mkdir(exist_ok=True)
                    
                    # Track species folders
                    if safe_name not in species_folders:
                        species_folders[safe_name] = 0
                    species_folders[safe_name] += 1
                    
                    # Copy or move file
                    src_path = Path(result.image_path)
                    if src_path.exists():
                        # Handle duplicate filenames
                        dest_path = species_folder / src_path.name
                        if dest_path.exists():
                            stem = src_path.stem
                            suffix = src_path.suffix
                            counter = 1
                            while dest_path.exists():
                                dest_path = species_folder / f"{stem}_{counter}{suffix}"
                                counter += 1
                        
                        if copy_files:
                            shutil.copy2(src_path, dest_path)
                        else:
                            shutil.move(str(src_path), str(dest_path))
                        organized_count += 1
                else:
                    # Low confidence - put in "low_confidence" folder
                    species_folder = output_base / "low_confidence"
                    species_folder.mkdir(exist_ok=True)
                    
                    src_path = Path(result.image_path)
                    if src_path.exists():
                        dest_path = species_folder / src_path.name
                        if copy_files:
                            shutil.copy2(src_path, dest_path)
                        else:
                            shutil.move(str(src_path), str(dest_path))
                        organized_count += 1
                        
            except Exception as e:
                self.logger.error(f"Error organizing {result.image_path}: {e}")
                errors.append({'file': result.image_path, 'error': str(e)})
        
        # Create summary
        result_info = {
            'success': len(errors) == 0,
            'output_directory': str(output_base),
            'total_images': total_count,
            'processed_images': organized_count,
            'species_folders': species_folders,
            'operation': 'copy' if copy_files else 'move',
            'errors': errors
        }
        
        # Create summary file
        summary_file = output_base / "organization_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Wildlife Detector - 画像振り分け結果\n")
            f.write(f"{'=' * 50}\n\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"処理画像数: {organized_count}/{total_count}\n")
            f.write(f"操作: {'コピー' if copy_files else '移動'}\n")
            f.write(f"信頼度閾値: {confidence_threshold:.2f}\n\n")
            
            f.write(f"種別フォルダ:\n")
            for species, count in sorted(species_folders.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  - {species}: {count} 枚\n")
            
            if errors:
                f.write(f"\nエラー:\n")
                for error in errors:
                    f.write(f"  - {error['file']}: {error['error']}\n")
        
        self.logger.info(f"Images organized: {organized_count}/{total_count} to {output_base}")
        
        return result_info
    
    def create_backup(self, source_dir: Union[str, Path], 
                     backup_name: Optional[str] = None) -> Path:
        """Create a backup of a directory"""
        source_dir = Path(source_dir)
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_dir.name}_backup_{timestamp}"
        
        backup_path = source_dir.parent / backup_name
        
        shutil.copytree(source_dir, backup_path)
        self.logger.info(f"Backup created: {backup_path}")
        
        return backup_path
    
    def get_directory_stats(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """Get statistics about a directory"""
        directory = Path(directory)
        
        if not directory.exists():
            return {'exists': False}
        
        total_size = 0
        file_count = 0
        file_types = {}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_count += 1
                size = file_path.stat().st_size
                total_size += size
                
                ext = file_path.suffix.lower()
                if ext not in file_types:
                    file_types[ext] = {'count': 0, 'size': 0}
                file_types[ext]['count'] += 1
                file_types[ext]['size'] += size
        
        return {
            'exists': True,
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_types': file_types
        }
