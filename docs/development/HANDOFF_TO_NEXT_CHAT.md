# Wildlife Detector AI v2.0 - チャット引継ぎ資料

## 🚀 プロジェクト概要

Wildlife Detector AI v2.0は、Google SpeciesNetを使用した野生生物検出デスクトップアプリケーションです。現在、フェーズ3（GUI実装）まで完了し、基本機能は正常に動作しています。

## 📊 現在の状況（2025年6月25日）

### ✅ 完了済みタスク

#### フェーズ1: 基盤構築
- Python 3.12環境構築
- SpeciesNet統合・テスト成功
- 基本モジュール実装

#### フェーズ2: コア機能
- `core/species_detector.py` - 拡張版検出モジュール
- `core/batch_processor.py` - バッチ処理エンジン
- `utils/csv_exporter.py` - CSV出力機能
- 日本語名マッピング（SpeciesNameMapper）

#### フェーズ3: GUI実装
- `gui/main_window.py` - PySide6ベースのGUI
- 画像選択・バッチ処理機能
- 進捗表示・結果表示
- CSV出力・ファイル振り分け機能

### 🔧 解決済み問題
- Python環境の混在問題（venv vs miniforge3）
- SpeciesNetの出力ファイル処理問題
- GUI統合後の動物検出機能不全

## ✅ 解決済み課題（2025年6月25日更新）

### 1. 表記の統一性問題 → 解決済み

**修正内容**:
1. **CSVエクスポートの英語化完了**
   - すべてのCSVヘッダーを英語に統一
   - 出力内容も英語化（No detection, Error, Unknown等）

2. **SpeciesNameMapperの無効化完了**
   - クラスを[DEPRECATED]として明確化
   - 日本語マッピング機能を無効化
   - 後方互換性のためクラス自体は保持

**現在の出力形式**:
```
Species Name: Corvus macrorhynchos
Scientific Name: Corvus macrorhynchos
Common Name: Large-billed crow
Category: bird
```

### 2. ファイル振り分け機能の改善 → 解決済み

**修正内容**:
1. **ファイル移動機能実装**
   - コピーではなく移動に変更
   - 元ファイルは削除される

2. **検出後の振り分け機能**
   - CSVファイルから検出結果を読み込み
   - 過去の結果でも振り分け可能

## 🛠️ 修正が必要なコード

### 1. SpeciesNameMapper の無効化または修正

**ファイル**: `core/species_detector.py`

**現在のコード（問題箇所）**:
```python
class SpeciesNameMapper:
    """Maps scientific names to Japanese common names"""
    
    SPECIES_MAP = {
        'corvidae': 'カラス科',
        'ardea': 'サギ属',
        # ... 他の日本語マッピング
    }
```

**修正案**:
1. 日本語マッピングを無効化
2. 英語の一般名マッピングに変更
3. または、言語設定を追加して切り替え可能にする

### 2. _parse_speciesnet_results メソッドの修正

**現在のコード**:
```python
# Map to Japanese name
japanese_name = self.name_mapper.get_japanese_name(scientific_name)
```

**修正案**:
```python
# Use English name directly
english_name = common_name if common_name else scientific_name
```

## 📁 プロジェクト構造

```
wildlife-detector/
├── core/
│   ├── species_detector.py  # ← 修正必要
│   ├── batch_processor.py
│   └── config.py
├── gui/
│   └── main_window.py
├── utils/
│   ├── csv_exporter.py
│   ├── file_manager.py
│   └── logger.py
├── tests/
│   └── test_data/images/
├── output/
├── config.yaml
└── main.py
```

## 🔄 今後の作業手順

1. **テスト実行と検証**
   ```bash
   # CLIモードでテスト
   python test_cli.bat
   
   # GUIモードでテスト
   python main.py
   ```

2. **CSV出力の検証**
   - ヘッダーが英語になっているか確認
   - 出力内容が英語で統一されているか確認

3. **ユーザーマニュアルの作成**
   - 英語出力仕様の説明を追加
   - CSVフォーマットの説明を更新

4. **リリース準備**
   - バージョン番号の更新
   - リリースノートの作成

## 💡 技術的な注意点

1. **SpeciesNet出力形式**
   - `prediction`: "id;kingdom;order;family;genus;species;common_name"
   - セミコロン区切りで7つのフィールド

2. **カテゴリ判定**
   - kingdom = "aves" → bird
   - kingdom = "mammalia" → mammal

3. **信頼度の扱い**
   - `prediction_score`が実際の信頼度
   - rollupやensemble処理が入ることがある

## 📋 動作確認済み環境

- Python 3.12.10
- Windows 11
- SpeciesNet 5.0.0
- PySide6 6.9.1

## 🎯 期待される成果

英語表記統一後の出力例：
```
Great egret - 79.0%
Bird (unknown species) - 83.1%
Ardeidae family - 69.1%
Corvidae family - 82.3%
Carnivorous mammal - 89.5%
```

## 📞 関連ファイル

- `CLAUDE.md` - 開発ガイド（更新済み）
- `GUI_ISSUE_HANDOFF.md` - GUI問題の解決記録
- `SPECIESNET_GUIDE.md` - SpeciesNet使用ガイド
- `config.yaml` - アプリケーション設定

## 🚀 次のステップ

1. ✅ ~~表記統一の実装~~ （完了）
2. ユーザーマニュアルの作成
3. リリース準備

## 📝 関連資料（新規追加）

- `ENGLISH_UPDATE_SUMMARY.md` - 英語化修正の詳細記録
- `FILE_ORGANIZATION_UPDATE.md` - ファイル振り分け機能の更新記録

---

**作成日**: 2025年6月25日  
**更新日**: 2025年6月25日（英語化完了）  
**作成者**: Claude  
**チャット容量**: 修正完了後に余裕あり
