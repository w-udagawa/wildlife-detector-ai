"""
Configuration management for Wildlife Detector AI
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    """Application configuration data class"""
    # Application settings
    app_name: str = "Wildlife Detector AI"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Detection settings
    model_name: str = "speciesnet"
    model_version: str = "5.0"
    country_code: str = "JPN"
    confidence_threshold: float = 0.5
    batch_size: int = 1
    timeout: int = 300
    max_detections_per_image: int = 10
    
    # Processing settings
    max_workers: int = 4
    chunk_size: int = 10
    use_gpu: bool = False
    memory_limit_gb: float = 4.0
    max_image_size_mb: float = 50.0
    resize_large_images: bool = True
    
    # Output settings
    default_output_directory: str = "output"
    csv_delimiter: str = ","
    csv_encoding: str = "utf-8-sig"
    generate_html_report: bool = True
    include_thumbnails: bool = True
    auto_save_results: bool = True
    
    # GUI settings
    window_title: str = "Wildlife Detector - 野生生物検出アプリケーション"
    window_width: int = 1200
    window_height: int = 800
    min_width: int = 1000
    min_height: int = 700
    theme: str = "light"
    language: str = "ja"
    
    # Paths
    temp_directory: str = "temp"
    cache_directory: str = "cache"
    logs_directory: str = "logs"
    
    # Advanced settings
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_cache: bool = True
    cache_size_mb: int = 500
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """Create AppConfig from dictionary"""
        app_config = cls()
        
        # Flatten nested dictionary
        flat_dict = cls._flatten_dict(config_dict)
        
        # Update attributes
        for key, value in flat_dict.items():
            if hasattr(app_config, key):
                setattr(app_config, key, value)
                
        return app_config
    
    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(AppConfig._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'app': {
                'name': self.app_name,
                'version': self.app_version,
                'debug': self.debug
            },
            'detection': {
                'model_name': self.model_name,
                'model_version': self.model_version,
                'country_code': self.country_code,
                'confidence_threshold': self.confidence_threshold,
                'batch_size': self.batch_size,
                'timeout': self.timeout,
                'max_detections_per_image': self.max_detections_per_image
            },
            'processing': {
                'max_workers': self.max_workers,
                'chunk_size': self.chunk_size,
                'use_gpu': self.use_gpu,
                'memory_limit_gb': self.memory_limit_gb,
                'max_image_size_mb': self.max_image_size_mb,
                'resize_large_images': self.resize_large_images
            },
            'output': {
                'default_output_directory': self.default_output_directory,
                'csv_delimiter': self.csv_delimiter,
                'csv_encoding': self.csv_encoding,
                'generate_html_report': self.generate_html_report,
                'include_thumbnails': self.include_thumbnails,
                'auto_save_results': self.auto_save_results
            },
            'gui': {
                'window_title': self.window_title,
                'window_width': self.window_width,
                'window_height': self.window_height,
                'min_width': self.min_width,
                'min_height': self.min_height,
                'theme': self.theme,
                'language': self.language
            },
            'paths': {
                'temp_directory': self.temp_directory,
                'cache_directory': self.cache_directory,
                'logs_directory': self.logs_directory
            },
            'logging': {
                'enable': self.enable_logging,
                'level': self.log_level
            },
            'cache': {
                'enable': self.enable_cache,
                'size_mb': self.cache_size_mb
            }
        }


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.config_dict = self.load_config()
        self.config = AppConfig.from_dict(self.config_dict)
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        path = Path(self.config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            path = Path(self.config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config.to_dict(), f, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         sort_keys=False)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """Get AppConfig instance"""
        return self.config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config_dict
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def reset_to_default(self) -> bool:
        """Reset configuration to default values"""
        self.config = AppConfig()
        self.config_dict = self.config.to_dict()
        return self.save_config()
