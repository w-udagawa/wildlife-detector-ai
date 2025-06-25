#!/usr/bin/env python3
"""
Wildlife Detector AI v2.0
Main entry point for the application
"""

import sys
import os
import click
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Version check
if sys.version_info < (3, 12):
    print("Error: Python 3.12 or higher is required for SpeciesNet compatibility.")
    print(f"Current version: {sys.version}")
    sys.exit(1)


@click.command()
@click.option('--gui/--no-gui', default=True, help='Launch GUI mode (default) or CLI mode')
@click.option('--image', type=click.Path(exists=True), help='Process a single image (CLI mode)')
@click.option('--batch', type=click.Path(exists=True), help='Process a folder of images (CLI mode)')
@click.option('--output', type=click.Path(), help='Output directory for results')
@click.option('--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--confidence', type=float, default=0.5, help='Confidence threshold (0.0-1.0)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.version_option(version='2.0.0')
def main(gui, image, batch, output, config, confidence, debug):
    """Wildlife Detector AI - AI-powered wildlife species detection"""
    
    # Setup logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    if debug:
        logger.debug("Debug mode enabled")
    
    if gui and not (image or batch):
        # GUI mode
        try:
            from PySide6.QtWidgets import QApplication
            from gui.main_window import MainWindow
            
            logger.info("Starting Wildlife Detector AI v2.0 in GUI mode...")
            
            app = QApplication(sys.argv)
            app.setApplicationName("Wildlife Detector")
            app.setOrganizationName("Wildlife AI")
            
            # Create and show main window
            window = MainWindow()
            window.show()
            
            # Run application
            sys.exit(app.exec())
            
        except ImportError as e:
            logger.error(f"Failed to import GUI components: {e}")
            print("❌ Error: GUI dependencies not installed.")
            print("   Please install PySide6: pip install PySide6")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"GUI startup error: {e}")
            print(f"❌ Error starting GUI: {e}")
            sys.exit(1)
        
    elif image:
        # Single image processing (CLI mode)
        try:
            from core.species_detector import create_detector
            from core.config import ConfigManager
            
            logger.info(f"Processing single image: {image}")
            
            # Load configuration
            config_manager = ConfigManager(config)
            app_config = config_manager.get_config()
            app_config.confidence_threshold = confidence
            
            # Create detector
            detector_config = {
                'country_code': app_config.country_code,
                'timeout': app_config.timeout,
                'confidence_threshold': confidence
            }
            detector = create_detector(config=detector_config)
            
            # Process image
            result = detector.detect_single(image)
            
            if result.success:
                print(f"\n✅ Detection successful!")
                print(f"   Processing time: {result.processing_time:.2f}s")
                print(f"   Detections: {len(result.detections)}")
                
                for i, detection in enumerate(result.detections):
                    print(f"\n   Detection {i+1}:")
                    print(f"   - Species: {detection.get('common_name', 'Unknown')}")
                    print(f"   - Scientific: {detection.get('scientific_name', 'N/A')}")
                    print(f"   - Confidence: {detection.get('confidence', 0):.3f}")
                    print(f"   - Category: {detection.get('category', 'N/A')}")
                    
                # Save results if output directory specified
                if output:
                    from utils.csv_exporter import CSVExporter
                    output_path = Path(output)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    exporter = CSVExporter(str(output_path))
                    files = exporter.export_all([result])
                    print(f"\n📄 Results saved to: {output}")
                    
            else:
                print(f"\n❌ Detection failed: {result.error_message}")
                
        except Exception as e:
            logger.error(f"CLI processing error: {e}")
            print(f"❌ Error: {e}")
            sys.exit(1)
        
    elif batch:
        # Batch processing (CLI mode)
        try:
            from core.batch_processor import BatchProcessor
            from core.config import ConfigManager
            from utils.file_manager import FileManager
            from utils.csv_exporter import CSVExporter
            
            logger.info(f"Processing batch: {batch}")
            
            # Load configuration
            config_manager = ConfigManager(config)
            app_config = config_manager.get_config()
            app_config.confidence_threshold = confidence
            
            # Get image files
            file_manager = FileManager()
            image_files = file_manager.get_image_files(batch)
            
            if not image_files:
                print(f"❌ No image files found in: {batch}")
                sys.exit(1)
                
            print(f"📁 Found {len(image_files)} image files")
            
            # Create batch processor
            processor_config = {
                'max_workers': app_config.max_workers,
                'batch_size': app_config.batch_size,
                'use_gpu': app_config.use_gpu,
                'confidence_threshold': confidence,
                'country_code': app_config.country_code,
                'timeout': app_config.timeout,
                'max_image_size_mb': app_config.max_image_size_mb
            }
            
            processor = BatchProcessor(processor_config)
            
            # Initialize processor
            if not processor.initialize():
                print("❌ Failed to initialize processor")
                sys.exit(1)
                
            # Process batch with progress callback
            def progress_callback(current, total, status, filename):
                percentage = (current / total * 100) if total > 0 else 0
                print(f"\r⏳ {status}: {current}/{total} ({percentage:.1f}%) - {filename}", end='', flush=True)
            
            print("\n🔄 Processing images...")
            results = processor.process_batch([str(f) for f in image_files], progress_callback)
            stats = processor.get_statistics()
            
            # Display results
            stats_dict = stats.to_dict()
            print(f"\n\n✅ Processing complete!")
            print(f"   Total images: {stats_dict['total_images']}")
            print(f"   Processed: {stats_dict['processed_images']}")
            print(f"   Successful: {stats_dict['successful_detections']}")
            print(f"   Total detections: {stats_dict['total_detections']}")
            print(f"   Processing time: {stats_dict['processing_time']:.2f}s")
            print(f"   Average time/image: {stats_dict['average_time_per_image']:.3f}s")
            
            # Species summary
            if stats_dict['species_counts']:
                print("\n📊 Species detected:")
                for species, count in sorted(stats_dict['species_counts'].items(), 
                                           key=lambda x: x[1], reverse=True):
                    print(f"   - {species}: {count}")
            
            # Save results
            if output:
                output_path = Path(output)
                output_path.mkdir(parents=True, exist_ok=True)
                
                exporter = CSVExporter(str(output_path))
                files = exporter.export_all(results, stats)
                print(f"\n📄 Results saved to: {output}")
                for file_type, file_path in files.items():
                    print(f"   - {Path(file_path).name}")
            
            # Cleanup
            processor.cleanup()
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            print(f"\n❌ Error: {e}")
            sys.exit(1)
        
    else:
        # Show help if no valid options
        ctx = click.get_current_context()
        click.echo(ctx.get_help())


if __name__ == "__main__":
    main()
