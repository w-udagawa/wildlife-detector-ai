# Wildlife Detector AI v2.0 - Git/GitHub管理への引継ぎ資料

## 📅 作成日: 2025年6月25日

## 🎯 プロジェクト概要

**Wildlife Detector AI v2.0**は、Google SpeciesNetを使用した野生生物検出デスクトップアプリケーションです。研究者向けに開発され、高精度な種識別と効率的なバッチ処理を提供します。

### 主な特徴
- 94.5%の種レベル分類精度（Google SpeciesNet）
- GUI/CLIデュアルインターフェース
- 大量画像のバッチ処理
- 英語/学名での統一出力（研究用）
- 自動ファイル振り分け機能

## 📊 現在のプロジェクト状態

### ✅ 完了済み作業

1. **コア機能実装**
   - SpeciesNet統合
   - バッチ処理エンジン
   - CSV/レポート出力

2. **GUI実装**
   - PySide6ベースのデスクトップUI
   - 日本語インターフェース
   - リアルタイム進捗表示

3. **リファクタリング**
   - ファイル構造の最適化
   - 英語出力への統一
   - コードクリーンアップ

## 📁 ファイル構造

```
wildlife-detector/
├── core/                    # コア検出モジュール
│   ├── __init__.py
│   ├── species_detector.py  # メイン検出クラス（SpeciesNet統合）
│   ├── batch_processor.py   # バッチ処理エンジン
│   └── config.py           # 設定管理クラス
│
├── gui/                    # GUIコンポーネント
│   ├── __init__.py
│   ├── main_window.py      # メインウィンドウ（PySide6）
│   ├── resources/          # アイコン、画像リソース
│   └── widgets/            # カスタムウィジェット
│
├── utils/                  # ユーティリティモジュール
│   ├── __init__.py
│   ├── csv_exporter.py     # CSV出力（英語ヘッダー）
│   ├── file_manager.py     # ファイル管理・振り分け
│   └── logger.py           # ログ管理
│
├── scripts/                # ユーティリティスクリプト
│   ├── quick_setup.bat     # 環境セットアップ
│   ├── check_python_env.bat
│   └── verify_environment.py
│
├── tests/                  # テストファイル
│   ├── scripts/            # テスト実行スクリプト
│   │   ├── test_cli.bat
│   │   └── test_crow.bat
│   ├── test_data/          # テスト用画像
│   │   └── images/
│   ├── test_clean_env.py
│   └── test_detector_debug.py
│
├── docs/                   # ドキュメント
│   └── development/        # 開発ドキュメント
│       ├── ENGLISH_UPDATE_SUMMARY.md
│       ├── FILE_ORGANIZATION_UPDATE.md
│       └── legacy/         # 旧コード保管
│
├── output/                 # 出力ディレクトリ（.gitignore対象）
├── logs/                   # ログディレクトリ（.gitignore対象）
├── temp/                   # 一時ファイル（.gitignore対象）
├── cache/                  # キャッシュ（.gitignore対象）
├── venv/                   # Python仮想環境（.gitignore対象）
│
├── .env                    # 環境変数（.gitignore対象）
├── .gitignore             # Git除外設定
├── config.yaml            # アプリケーション設定
├── main.py                # エントリーポイント
├── requirements.txt       # Python依存関係
├── setup.py               # パッケージ設定
├── README.md              # プロジェクト説明（英語）
├── CLAUDE.md              # 開発ガイド（日本語）
├── SPECIESNET_GUIDE.md    # SpeciesNet使用ガイド
└── REFACTORING_SUMMARY.md # リファクタリング記録
```

## 🔑 重要ファイルの説明

### コアファイル
- **main.py**: CLIとGUIモードの切り替え、引数処理
- **species_detector.py**: SpeciesNet統合、検出処理の中核
- **batch_processor.py**: 並列処理、進捗管理
- **main_window.py**: GUIの全機能実装

### 設定ファイル
- **config.yaml**: 検出パラメータ、GUI設定、出力設定
- **requirements.txt**: 全依存関係リスト（pip freeze済み）
- **.gitignore**: 適切な除外設定済み

### ドキュメント
- **README.md**: ユーザー向け説明（英語）
- **CLAUDE.md**: 開発者向け詳細ガイド（日本語）

## 🚦 Git管理の準備状況

### ✅ 準備完了項目
1. **.gitignore**設定済み
   - Python標準除外パターン
   - プロジェクト固有の除外（output/, logs/, etc.）
   - 仮想環境、キャッシュの除外

2. **ファイル構造**最適化済み
   - 論理的なディレクトリ構成
   - テストとソースコードの分離
   - ドキュメントの整理

3. **コードクリーンアップ**完了
   - 不要ファイルの削除
   - 重複コードの除去
   - 一貫した命名規則

### ⚠️ 注意事項
- **大容量ファイル**: テスト画像は小さいが、実運用データは要注意
- **機密情報**: .envファイルは既に.gitignore済み
- **依存関係**: requirements.txtは最新状態

## 📋 推奨される次のステップ

### 1. Gitリポジトリの初期化
```bash
# 既存の.gitディレクトリがあるか確認
cd wildlife-detector
git status

# なければ初期化
git init
```

### 2. 初回コミット
```bash
# 全ファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: Wildlife Detector AI v2.0

- Core detection with Google SpeciesNet integration
- GUI application with PySide6
- Batch processing capabilities
- English/scientific name output for research
- Automated file organization features"
```

### 3. ブランチ戦略の提案
```bash
# メインブランチ
main (or master)  # 安定版リリース用

# 開発ブランチ
develop          # 開発統合用

# 機能ブランチ例
feature/multi-language-support
feature/cloud-storage-integration
feature/mobile-app-api
```

### 4. GitHub設定の推奨事項

#### リポジトリ名候補
- `wildlife-detector`
- `wildlife-detector-ai`
- `speciesnet-desktop`

#### リポジトリ説明
```
AI-powered wildlife species detection desktop application using Google SpeciesNet. 
Features batch processing, GUI/CLI interfaces, and automated file organization.
```

#### トピックス（Topics）
- wildlife-detection
- species-identification
- computer-vision
- speciesnet
- desktop-application
- python
- pyside6
- research-tool

#### ライセンス候補
- MIT License（オープンソース推奨）
- Apache License 2.0
- GPL v3（強いコピーレフト）

### 5. README.mdの追加推奨項目
- インストール手順の詳細
- 使用例（スクリーンショット付き）
- コントリビューションガイドライン
- ライセンス情報
- 謝辞（Google SpeciesNetチーム）

## 🔒 セキュリティ考慮事項

1. **APIキー/認証情報**
   - 現在は使用していないが、将来的にクラウド連携時は.envで管理

2. **ユーザーデータ**
   - 検出結果には位置情報なし
   - 画像は処理後も保持（プライバシー考慮）

3. **依存関係**
   - 定期的な脆弱性チェック推奨
   - `pip-audit`の使用を検討

## 📈 今後の開発可能性

1. **機能拡張**
   - 多言語対応（UI/出力）
   - クラウドストレージ連携
   - Web API化
   - モバイルアプリ連携

2. **パフォーマンス改善**
   - GPU活用の最適化
   - メモリ使用量の削減
   - 処理速度の向上

3. **研究機能**
   - 統計分析機能
   - レポート生成の拡張
   - データベース連携

## 💡 開発のヒント

1. **コミットメッセージ**
   - 規約例: `feat:`, `fix:`, `docs:`, `refactor:`
   - 日本語/英語どちらでも可（チーム次第）

2. **Issue管理**
   - バグレポートテンプレート作成推奨
   - 機能要望テンプレート作成推奨

3. **CI/CD**
   - GitHub Actionsでのテスト自動化
   - PyPIへの自動リリース

## 📞 連絡事項

- **Python環境**: 3.12.10（venv使用）
- **主要依存**: PySide6, speciesnet, pandas, Pillow
- **テスト済みOS**: Windows 11
- **開発ツール**: VSCode推奨

---

## ✅ チェックリスト（Git/GitHub管理開始前）

- [ ] .gitignoreの内容確認
- [ ] 機密情報が含まれていないか確認
- [ ] requirements.txtが最新か確認
- [ ] READMEが適切に記述されているか
- [ ] ライセンスの選択
- [ ] 初回コミットメッセージの準備
- [ ] GitHubリポジトリ名の決定
- [ ] 公開/非公開の決定

---

**作成者**: Claude  
**プロジェクトバージョン**: 2.0.0  
**状態**: Git/GitHub管理準備完了  
