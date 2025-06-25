#!/usr/bin/env python3
"""
Wildlife Detector AI - モジュール統合テスト
すべての基本モジュールが正しく動作することを確認
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all module imports"""
    print("🔍 モジュールインポートテスト...")
    
    try:
        # Core modules
        from core.detector import WildlifeDetector, create_detector
        from core.config import ConfigManager
        print("✅ core モジュール: OK")
        
        # Utils modules
        from utils.logger import setup_logger
        from utils.file_manager import FileManager
        print("✅ utils モジュール: OK")
        
        # External modules
        import speciesnet
        print("✅ SpeciesNet: OK")
        
        try:
            import cameratrapai
            print("✅ CameraTrapAI: OK")
        except ImportError:
            print("⚠️  CameraTrapAI: Not installed (optional)")
        
        return True
        
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_config():
    """Test configuration manager"""
    print("\n📋 設定管理テスト...")
    
    try:
        from core.config import ConfigManager
        
        config = ConfigManager()
        
        # Test getting values
        app_name = config.get('app.name', 'Default')
        print(f"   アプリ名: {app_name}")
        
        batch_size = config.get('detection.batch_size', 1)
        print(f"   バッチサイズ: {batch_size}")
        
        print("✅ 設定管理: OK")
        return True
        
    except Exception as e:
        print(f"❌ 設定管理エラー: {e}")
        return False


def test_logger():
    """Test logger setup"""
    print("\n📝 ログシステムテスト...")
    
    try:
        from utils.logger import setup_logger
        
        logger = setup_logger(log_file="logs/test.log")
        logger.info("テストログメッセージ", component="test", status="ok")
        
        print("✅ ログシステム: OK")
        return True
        
    except Exception as e:
        print(f"❌ ログシステムエラー: {e}")
        return False


def test_file_manager():
    """Test file manager"""
    print("\n📁 ファイル管理テスト...")
    
    try:
        from utils.file_manager import FileManager
        
        fm = FileManager()
        
        # Test directory creation
        test_dir = fm.ensure_directory("temp/test_dir")
        print(f"   ディレクトリ作成: {test_dir}")
        
        # Test image file listing
        images = fm.get_image_files("tests/test_data/images")
        print(f"   画像ファイル数: {len(images)}")
        
        print("✅ ファイル管理: OK")
        return True
        
    except Exception as e:
        print(f"❌ ファイル管理エラー: {e}")
        return False


def test_detector():
    """Test wildlife detector"""
    print("\n🦅 Wildlife Detector テスト...")
    
    try:
        from core.detector import create_detector, DetectionMode
        
        # Create detector
        detector = create_detector()
        print(f"   使用モード: {detector.mode.value}")
        
        # List available modes
        modes = detector.available_modes()
        print(f"   利用可能なモード: {[m.value for m in modes]}")
        
        # Test mock detection
        result = detector.detect_single("dummy.jpg")
        print(f"   モック検出テスト: {'成功' if result else '失敗'}")
        
        print("✅ Wildlife Detector: OK")
        return True
        
    except Exception as e:
        print(f"❌ Wildlife Detector エラー: {e}")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Wildlife Detector AI - 統合テスト")
    print("="*60)
    
    tests = [
        ("インポート", test_imports),
        ("設定管理", test_config),
        ("ログシステム", test_logger),
        ("ファイル管理", test_file_manager),
        ("検出器", test_detector),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*60)
    print("📊 テスト結果サマリー:")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 すべてのテストに合格しました！")
        print("\n次のステップ:")
        print("1. テスト画像を tests/test_data/images/ に配置")
        print("2. python -m pytest tests/ -v でユニットテスト実行")
        print("3. SpeciesNetで実画像テスト")
    else:
        print("⚠️ いくつかのテストが失敗しました。")
        print("エラーを確認して修正してください。")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
