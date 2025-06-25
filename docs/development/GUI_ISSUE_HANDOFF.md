# Wildlife Detector AI v2.0 - GUI実装後の問題と引継ぎ資料

## 🚨 発生した問題

**フェーズ3でGUI実装後、動物検出が機能しなくなりました。**

### 問題の症状
- すべての画像で「検出なし」（信頼度0.000）
- 処理時間は約6秒（処理自体は実行されている）
- CLIでは正常に動作していた機能がGUI経由では動作しない

### スクリーンショットの状況
- test_duck.JPG: 検出なし（6.81秒）
- test_crow.JPG: 検出なし（6.83秒）
- test_kilingfisher.JPG: 検出なし（6.85秒）
- test_heron.JPG: 検出なし（6.89秒）

## ✅ 正常動作していた状態（フェーズ1完了時）

### CLIでの動作確認済み
```bash
# これは正常に動作していた
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_crow.JPG --predictions_json output/crow_result.json --country JPN

# 結果: カラス科（Corvidae）82.27%で正しく検出
```

### 実装済みモジュール（正常動作）
- `core/detector.py` - SpeciesNet統合
- `core/config.py` - 設定管理
- `utils/logger.py` - ログシステム
- `utils/file_manager.py` - ファイル操作

## 🔍 考えられる原因

### 1. ファイルパスの問題
- GUIからの相対パス vs 絶対パスの違い
- Windowsのパス区切り文字（\）の扱い

### 2. SpeciesNet呼び出しの問題
- subprocessの作業ディレクトリ設定
- 環境変数の継承
- コマンドライン引数の構築

### 3. 結果パースの問題
- JSONファイルの読み込みエラー
- 一時ファイルの競合
- 非同期処理のタイミング

### 4. GUI特有の問題
- スレッド/プロセス間の通信
- イベントループのブロッキング
- 例外のサイレントキャッチ

## 🛠️ デバッグ手順

### 1. ログの確認
```python
# detector.pyにデバッグログを追加
self.logger.debug(f"Processing image: {image_path}")
self.logger.debug(f"Command: {' '.join(cmd)}")
self.logger.debug(f"Working directory: {os.getcwd()}")
```

### 2. 直接実行テスト
```python
# GUIを介さずdetectorを直接テスト
from core.detector import create_detector
detector = create_detector()
result = detector.detect_single("tests/test_data/images/test_crow.JPG")
print(result)
```

### 3. subprocess出力の確認
```python
# subprocess実行時の標準出力・エラー出力を確認
result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
```

## 💡 推奨される修正アプローチ

### 1. 絶対パスの使用
```python
# 相対パスを絶対パスに変換
image_path = Path(image_path).absolute()
```

### 2. 作業ディレクトリの明示的設定
```python
# プロジェクトルートを作業ディレクトリに設定
project_root = Path(__file__).parent.parent
result = subprocess.run(cmd, cwd=str(project_root))
```

### 3. エラーハンドリングの強化
```python
try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    self.logger.error(f"SpeciesNet error: {e.stderr}")
    # GUIにエラーを通知
```

### 4. モックモードでのテスト
```python
# まずモックモードで動作確認
detector = WildlifeDetector(mode=DetectionMode.MOCK)
```

## 📋 GUI実装で追加された可能性のあるファイル

- `gui/main_window.py` - メインウィンドウ
- `gui/detector_thread.py` - バックグラウンド処理？
- その他のGUIコンポーネント

## 🎯 次のステップ

1. **エラーログの確認**
   - GUIアプリケーション実行時のコンソール出力
   - logsディレクトリのログファイル

2. **最小限の再現コード作成**
   - GUIを介さずに問題を再現できるか確認

3. **段階的デバッグ**
   - モックモード → SpeciesNetモード
   - CLI → 最小GUI → 完全GUI

## 📝 重要な確認事項

- Python仮想環境は有効化されているか？
- GUIはどのように実行されているか？（python gui/main_window.py?）
- エラーメッセージは表示されているか？
- 処理中のプログレスバーは動いているか？

---

**作成日**: 2025年6月25日
**問題発生**: フェーズ3 GUI実装後
**前回の正常動作**: フェーズ1完了時（CLIテスト成功）
