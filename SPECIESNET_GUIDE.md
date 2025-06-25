# Wildlife Detector AI v2.0 - SpeciesNet インストールガイド

## 🦅 SpeciesNet について

SpeciesNetは実際にはGoogleが開発したAIモデルで、2000種以上の野生動物を識別できます。

## ✅ インストール状況

**すでにSpeciesNetはインストール済みです！**

`verify_environment.py`の実行結果：
```
🦅 SpeciesNet:
   ✅ SpeciesNet: Installed
   ✅ SpeciesNet scripts: Available
```

## 📦 追加のAIバックエンド

### Google CameraTrapAI（インストール済み）

```bash
# Google CameraTrapAIをインストール
pip install git+https://github.com/google/cameratrapai.git
# ✅ インストール成功！
```

### 方法2: PyTorch-Wildlife経由

Microsoft CameraTrapsリポジトリのPyTorch-Wildlifeフレームワークを使用：

```bash
# PyTorch-Wildlifeをインストール
pip install git+https://github.com/microsoft/CameraTraps.git
```

### 方法3: 代替ソリューション（MegaDetector + 独自分類器）

SpeciesNetが利用できない場合、以下の組み合わせを推奨：

1. **MegaDetector v5** - 動物検出用
2. **独自の分類器** - 種の識別用

```bash
# MegaDetectorのインストール
pip install torch torchvision
wget https://github.com/agentmorris/MegaDetector/releases/download/v5.0/md_v5a.0.0.pt
```

## 🔧 SpeciesNetの使用方法

### 基本コマンド

```bash
# 単一画像の処理
python -m speciesnet.scripts.run_model \
  --filepaths "path/to/image.jpg" \
  --predictions_json "output.json" \
  --country "JPN" \
  --batch_size 1

# フォルダ全体の処理
python -m speciesnet.scripts.run_model \
  --folders "path/to/images" \
  --predictions_json "output.json" \
  --country "JPN" \
  --batch_size 8
```

### 重要なオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|------------|
| `--filepaths` | 画像ファイルのリスト（カンマ区切り） | - |
| `--folders` | 画像フォルダのリスト（カンマ区切り） | - |
| `--predictions_json` | 出力JSONファイル | - |
| `--country` | ISO 3166-1 alpha-3国コード | - |
| `--batch_size` | バッチサイズ | 8 |
| `--model` | 使用モデル | kaggle:google/speciesnet/pyTorch/v4.0.1a |
| `--geofence` | ジオフェンシング | true |
| `--detector_only` | 検出のみ | false |
| `--classifier_only` | 分類のみ | false |
| `--ensemble_only` | アンサンブルのみ | false |

## 📝 利用可能なバックエンド

### インストール済み
1. **SpeciesNet** - GoogleのAIモデル（メイン）
2. **Google CameraTrapAI** - 追加のAIバックエンド

### オプション
3. **PyTorch-Wildlife** - Microsoftの統合フレームワーク
4. **MegaDetector** - 動物検出専用モデル
5. **モックモード** - テスト用（実装済み）

## 🔧 モックモード

テスト用のモックモードは`core/detector.py`に実装済みです：

```python
# モックモードでのテスト
from core.detector import WildlifeDetector, DetectionMode

detector = WildlifeDetector(mode=DetectionMode.MOCK)
result = detector.detect_single("test.jpg")
print(result)
```
