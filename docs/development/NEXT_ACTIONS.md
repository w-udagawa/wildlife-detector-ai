# Wildlife Detector AI v2.0 - 次のアクション

## 🎯 今すぐ実行可能なタスク

### 1. SpeciesNet の動作確認

```bash
# テスト画像を作成（単色の画像でもOK）
python -c "from PIL import Image; img = Image.new('RGB', (224, 224), color='green'); img.save('tests/test_data/images/test_green.jpg')"

# SpeciesNetのヘルプを確認（実行済み）
python -m speciesnet.scripts.run_model --help

# 単一画像でテスト
# --filepaths オプションを使用（--image ではなく）
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_green.jpg --predictions_json test_output.json --country JPN

# フォルダ内の全画像をテスト
 python -m speciesnet.scripts.run_model --folders tests/test_data/images --predictions_json folder_output.json --country JPN
```

### 2. config.py の実装

`core/config.py` を作成：

```python
"""
Configuration management for Wildlife Detector AI
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        path = Path(self.config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
```

### 3. logger.py の実装

`utils/logger.py` を作成：

```python
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
```

### 4. file_manager.py の実装

`utils/file_manager.py` を作成：

```python
"""
File management utilities for Wildlife Detector AI
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional, Union
import hashlib

class FileManager:
    """Handles file operations for the application"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """Ensure a directory exists"""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def get_image_files(self, directory: Union[str, Path], 
                       extensions: Optional[List[str]] = None) -> List[Path]:
        """Get all image files in a directory"""
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
            
        directory = Path(directory)
        image_files = []
        
        for ext in extensions:
            image_files.extend(directory.glob(f'*{ext}'))
            image_files.extend(directory.glob(f'*{ext.upper()}'))
            
        return sorted(image_files)
        
    def copy_with_structure(self, source: Path, dest_base: Path, 
                          preserve_structure: bool = True) -> Path:
        """Copy file preserving directory structure"""
        if preserve_structure:
            relative = source.relative_to(self.base_path)
            dest = dest_base / relative
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
```

### 5. 初期テストの作成

`tests/test_detector.py` を作成：

```python
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
```

## 📋 推奨実行順序

1. **設定モジュールの作成**
   ```bash
   # config.py, logger.py, file_manager.py を作成
   ```

2. **pytestのインストールとテストの実行**
   ```bash
   # pytestのインストール
   pip install pytest pytest-cov
   
   # テストの実行
   pytest tests/test_detector.py -v
   ```

3. **SpeciesNetの動作確認**
   ```bash
   # 実際の野生動物画像を tests/test_data/images/ に配置
   # または、単純なテスト画像で試す
   ```

4. **統合テスト**
   ```bash
   # detectorのモード確認
   python -c "from core.detector import create_detector; d = create_detector(); print(f'Using mode: {d.mode}')"
   
   # CameraTrapAIのインポートテスト
   python -c "import cameratrapai; print('CameraTrapAI imported successfully')"
   ```

## 🎯 本日の目標

1. ✅ 環境セットアップ完了
2. ✅ detector.py 作成
3. ⏳ config.py 実装
4. ⏳ logger.py 実装  
5. ⏳ file_manager.py 実装
6. ⏳ SpeciesNet動作確認
7. ⏳ 基本テスト作成

これらを完了すれば、フェーズ1はほぼ完成です！
