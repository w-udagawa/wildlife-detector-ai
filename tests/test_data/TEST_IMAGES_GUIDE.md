# Wildlife Detector AI - テスト画像配置ガイド

## 📸 テスト画像の保存場所

### 1. メインのテスト画像ディレクトリ
```
C:\Users\AU3009\Claudeworks\projects\wildlife-detector\tests\test_data\images\
```

このディレクトリに以下の種類の画像を配置してください：

### 2. 推奨画像構成

#### 基本テスト用（必須）
- `test_tiger.jpg` - トラの画像
- `test_elephant.jpg` - 象の画像
- `test_deer.jpg` - 鹿の画像
- `test_empty.jpg` - 動物がいない風景画像

#### 追加テスト用（オプション）
- `test_multiple.jpg` - 複数の動物が写っている画像
- `test_small.jpg` - 小さな動物（鳥など）の画像
- `test_night.jpg` - 夜間撮影の画像
- `test_blurry.jpg` - ぼやけた画像

### 3. 画像形式の要件
- **対応形式**: JPG, JPEG, PNG, BMP, TIFF, TIF
- **推奨サイズ**: 1920x1080 以上
- **最小サイズ**: 224x224 ピクセル

### 4. フォルダ構造（複数カテゴリでテストする場合）

```
tests/test_data/images/
├── mammals/           # 哺乳類
│   ├── tiger.jpg
│   ├── elephant.jpg
│   └── deer.jpg
├── birds/            # 鳥類
│   ├── peacock.jpg
│   └── eagle.jpg
├── empty/            # 動物なし
│   └── landscape.jpg
└── challenging/      # 難しいケース
    ├── night.jpg
    ├── blurry.jpg
    └── multiple.jpg
```

### 5. テスト実行用のサンプル画像

すぐにテストを開始したい場合は、以下のコマンドで単純なテスト画像を生成できます：

```python
from PIL import Image
import numpy as np

# 単色画像（緑）
img = Image.new('RGB', (640, 480), color='green')
img.save('tests/test_data/images/test_green.jpg')

# ノイズ画像
noise = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
img_noise = Image.fromarray(noise)
img_noise.save('tests/test_data/images/test_noise.jpg')

# グラデーション画像
gradient = np.zeros((480, 640, 3), dtype=np.uint8)
for i in range(480):
    gradient[i, :] = [i//2, 100, 255-i//2]
img_gradient = Image.fromarray(gradient)
img_gradient.save('tests/test_data/images/test_gradient.jpg')

print("テスト画像を生成しました！")
```

## 🚀 画像配置後のテストコマンド

```bash
# 1. 単一画像でSpeciesNetテスト
python -m speciesnet.scripts.run_model \
  --filepaths tests/test_data/images/test_tiger.jpg \
  --predictions_json output/test_single.json \
  --country JPN

# 2. フォルダ全体でテスト
python -m speciesnet.scripts.run_model \
  --folders tests/test_data/images \
  --predictions_json output/test_folder.json \
  --country JPN

# 3. Pythonスクリプトでテスト
python -c "from core.detector import create_detector; d = create_detector(); print(d.detect_single('tests/test_data/images/test_tiger.jpg'))"
```

## 📝 注意事項

- ファイル名に日本語を使用しないでください
- スペースを含むファイル名は避けてください
- 画像は著作権フリーのものを使用してください
