"""
Wildlife Detector Debug Script
GUI問題のデバッグ用スクリプト
"""

import sys
import json
import logging
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.species_detector import SpeciesDetector, DetectionMode, create_detector

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_detector():
    """Detectorの直接テスト"""
    print("=== Wildlife Detector Debug Test ===\n")
    
    # テスト画像のパス
    test_image = project_root / "tests" / "test_data" / "images" / "test_crow.JPG"
    
    if not test_image.exists():
        print(f"エラー: テスト画像が見つかりません: {test_image}")
        return
    
    print(f"テスト画像: {test_image}\n")
    
    # 1. 利用可能なモードの確認
    print("1. 利用可能な検出モードを確認...")
    temp_detector = SpeciesDetector(mode=DetectionMode.MOCK)
    available_modes = temp_detector.available_modes()
    for mode in available_modes:
        print(f"   - {mode.value}")
    print()
    
    # 2. MOCKモードでのテスト
    print("2. MOCKモードでテスト...")
    mock_detector = SpeciesDetector(mode=DetectionMode.MOCK)
    mock_result = mock_detector.detect_single(test_image)
    
    print(f"   成功: {mock_result.success}")
    print(f"   検出数: {len(mock_result.detections)}")
    if mock_result.detections:
        det = mock_result.detections[0]
        print(f"   種名: {det['common_name']}")
        print(f"   信頼度: {det['confidence']:.3f}")
    print()
    
    # 3. SpeciesNetモードでのテスト（利用可能な場合）
    if DetectionMode.SPECIESNET in available_modes:
        print("3. SpeciesNetモードでテスト...")
        
        config = {
            'country_code': 'JPN',
            'timeout': 300
        }
        
        speciesnet_detector = SpeciesDetector(mode=DetectionMode.SPECIESNET, config=config)
        
        try:
            result = speciesnet_detector.detect_single(test_image)
            
            print(f"   成功: {result.success}")
            print(f"   処理時間: {result.processing_time:.2f}秒")
            
            if result.success:
                print(f"   検出数: {len(result.detections)}")
                
                if result.detections:
                    for i, det in enumerate(result.detections):
                        print(f"\n   検出 {i+1}:")
                        print(f"     種名（日本語）: {det['common_name']}")
                        print(f"     種名（英語）: {det.get('english_name', 'N/A')}")
                        print(f"     学名: {det.get('scientific_name', 'N/A')}")
                        print(f"     カテゴリ: {det['category']}")
                        print(f"     信頼度: {det['confidence']:.3f}")
                        print(f"     バウンディングボックス: {det.get('bbox', [])}")
                else:
                    print("   検出なし（信頼度が閾値未満の可能性）")
            else:
                print(f"   エラー: {result.error_message}")
                
        except Exception as e:
            print(f"   例外発生: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("3. SpeciesNetモードは利用できません")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_detector()
