# Wildlife Detector AI - システムPythonに影響を与えない配布方法

## 📋 概要

会社のPython環境を変更せずに、Wildlife Detector AIを動作させるための独立環境構築ガイドです。

## 🎯 方針

- **システムPythonの変更なし** - 既存のPython環境には一切触れません
- **完全独立環境** - アプリケーション専用のPython環境を提供
- **ポータブル実行** - Python未インストールPCでも動作可能

---

## 🔧 IT部門向け：配布パッケージ準備手順

### 方法1: Python Embeddable Package使用（推奨）

#### 1. Python Embeddable Packageのダウンロード

1. https://www.python.org/downloads/windows/ にアクセス
2. Python 3.12.x の「Windows embeddable package (64-bit)」をダウンロード
   - ファイル名例: `python-3.12.10-embed-amd64.zip`

#### 2. 配布パッケージの構築

```batch
wildlife-detector-complete/
├── python-portable/          # Embeddable Python展開先
│   ├── python.exe
│   ├── python312.dll
│   ├── python312.zip
│   └── ...
├── core/                     # アプリケーションファイル
├── gui/
├── utils/
├── scripts/
├── docs/
├── main.py
├── config.yaml
├── requirements.txt
├── setup_isolated_env.bat    # 独立環境用セットアップ
└── README_ISOLATED.txt       # 独立環境版説明書
```

#### 3. Embeddable Pythonの設定

`python-portable`フォルダ内に`python312._pth`ファイルを編集：

```
python312.zip
.
../app-env/Lib/site-packages

# Uncomment to run site.main() automatically
import site
```

#### 4. pipのインストール（Embeddable Python用）

```batch
:: get-pip.pyをダウンロード
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

:: pipをインストール
python-portable\python.exe get-pip.py

:: 確認
python-portable\python.exe -m pip --version
```

### 方法2: WinPython使用（より簡単）

1. https://winpython.github.io/ からWinPython 3.12をダウンロード
2. 必要なファイルだけを抽出して配布

### 方法3: Miniconda使用（高機能）

1. Miniconda3をダウンロード
2. 独立した環境として設定
3. 必要なパッケージを事前インストール

---

## 📦 配布パッケージ作成スクリプト

### create_isolated_package.bat

```batch
@echo off
chcp 65001 >nul
title Wildlife Detector AI - 独立環境パッケージ作成

echo =====================================
echo 独立環境版パッケージを作成します
echo =====================================
echo.

:: 作業フォルダ作成
set package_name=wildlife-detector-isolated
if exist %package_name% rmdir /s /q %package_name%
mkdir %package_name%

:: Python Embeddableをコピー
echo [1/4] Python環境をコピー中...
xcopy /s /e /q python-portable %package_name%\python-portable\

:: アプリケーションファイルをコピー
echo [2/4] アプリケーションファイルをコピー中...
xcopy /s /q core %package_name%\core\
xcopy /s /q gui %package_name%\gui\
xcopy /s /q utils %package_name%\utils\
xcopy /s /q scripts %package_name%\scripts\
xcopy /s /q docs %package_name%\docs\

:: 必要なファイルをコピー
copy main.py %package_name%\
copy config.yaml %package_name%\
copy requirements.txt %package_name%\
copy setup_isolated_env.bat %package_name%\
copy README_ISOLATED.txt %package_name%\

:: 依存関係を事前インストール（オプション）
echo [3/4] 依存関係を事前インストール中...
cd %package_name%
python-portable\python.exe -m venv app-env
call app-env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

:: ZIP作成
echo [4/4] ZIPファイルを作成中...
powershell -Command "Compress-Archive -Path '%package_name%' -DestinationPath '%package_name%.zip' -Force"

echo.
echo ✅ 完了: %package_name%.zip
pause
```

---

## 📝 ユーザー向け説明の更新

### README_ISOLATED.txt

```
=====================================
Wildlife Detector AI v2.0
独立環境版（システムPython変更なし）
=====================================

この版は会社のPython環境に一切影響を与えません。
アプリケーション専用のPython環境で動作します。

■ インストール方法

1. このフォルダをCドライブ直下に配置
   推奨: C:\wildlife-detector

2. 「setup_isolated_env.bat」を右クリック
   →「管理者として実行」

3. セットアップ完了後、デスクトップの
   「Wildlife Detector」から起動

■ 特徴
- 会社のPython環境を変更しません
- Python未インストールPCでも動作
- 完全に独立した実行環境

■ サポート
IT部門: 内線 xxxx
=====================================
```

---

## 🔄 配布方法の比較

| 方法 | メリット | デメリット | ファイルサイズ |
|------|--------|------------|---------------|
| Embeddable Python | 最小構成、高速 | 初期設定が必要 | 約50MB |
| WinPython | 設定済み、安定 | サイズが大きい | 約500MB |
| Miniconda | 柔軟性が高い | 複雑 | 約100MB |
| 仮想環境のみ | シンプル | Python要インストール | 約10MB |

---

## 🚀 推奨配布フロー

### 1. 小規模配布（10台以下）
- Embeddable Python版を作成
- USBまたは共有フォルダで配布
- 各PCで`setup_isolated_env.bat`実行

### 2. 中規模配布（50台以下）
- 依存関係インストール済みパッケージを作成
- ファイルサーバーに配置
- バッチファイルで自動コピー＆セットアップ

### 3. 大規模配布（50台以上）
- MSIインストーラー作成を検討
- SCCM等の配布ツール活用
- サイレントインストール対応

---

## ⚠️ 注意事項

### セキュリティ
- 実行ファイルのデジタル署名を検討
- ウイルス対策ソフトの除外設定必須
- 配布前のマルウェアスキャン実施

### パス関連
- 日本語パスを避ける（C:\野生動物検出 ×）
- スペースを含むパスも避ける
- 推奨: `C:\wildlife-detector`

### 更新時
- app-envフォルダのみ更新で対応可能
- Python本体の更新は慎重に

---

## 📊 配布前チェックリスト

- [ ] Embeddable Pythonの動作確認
- [ ] 依存パッケージのインストール確認
- [ ] 管理者権限なしでの動作確認
- [ ] ウイルス対策ソフトでの動作確認
- [ ] 異なるWindows版での動作確認
- [ ] ネットワークドライブからの実行確認

---

**作成日**: 2025年6月25日  
**更新者**: Claude/AU3009
