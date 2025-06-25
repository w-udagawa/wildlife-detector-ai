@echo off
chcp 65001 >nul
title Wildlife Detector AI セットアップ

echo =====================================
echo Wildlife Detector AI v2.0
echo 社内配布用セットアップ
echo =====================================
echo.

:: 管理者権限チェック
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo エラー: このセットアップは管理者権限が必要です。
    echo.
    echo 以下の手順で再実行してください：
    echo 1. このファイルを右クリック
    echo 2. 「管理者として実行」を選択
    echo.
    pause
    exit /b 1
)

echo セットアップを開始します...
echo.

:: Python 3.12のチェック
echo [1/5] Python環境の確認...
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo Python 3.12のインストールが必要です。
    echo IT部門にお問い合わせください。
    echo.
    pause
    exit /b 1
)

:: 仮想環境の作成
echo [2/5] アプリケーション環境の作成...
if exist venv (
    echo 既存の環境を削除しています...
    rmdir /s /q venv
)
python -m venv venv
if %errorLevel% neq 0 (
    echo.
    echo エラー: 環境の作成に失敗しました。
    echo IT部門にお問い合わせください。
    echo.
    pause
    exit /b 1
)

:: 依存関係のインストール
echo [3/5] 必要なコンポーネントをインストール中...
echo （この処理には5-10分かかります）
echo.
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo.
    echo エラー: コンポーネントのインストールに失敗しました。
    echo ネットワーク接続を確認してください。
    echo.
    pause
    exit /b 1
)

:: 必要なフォルダの作成
echo [4/5] フォルダ構成の準備...
if not exist output mkdir output
if not exist logs mkdir logs
if not exist temp mkdir temp
if not exist cache mkdir cache

:: デスクトップショートカットの作成
echo [5/5] ショートカットの作成...
set "desktop=%USERPROFILE%\Desktop"

:: アプリケーション起動用バッチファイル
echo @echo off > "%desktop%\Wildlife Detector.bat"
echo cd /d "%cd%" >> "%desktop%\Wildlife Detector.bat"
echo call venv\Scripts\activate.bat >> "%desktop%\Wildlife Detector.bat"
echo start python main.py >> "%desktop%\Wildlife Detector.bat"
echo exit >> "%desktop%\Wildlife Detector.bat"

:: 出力フォルダへのショートカット（PowerShell使用）
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Wildlife Detector Output.lnk'); $Shortcut.TargetPath = '%cd%\output'; $Shortcut.Save()"

:: 設定ファイルの確認
if not exist config.yaml (
    echo.
    echo 警告: 設定ファイルが見つかりません。
    echo デフォルト設定で動作します。
)

echo.
echo =====================================
echo ✅ セットアップが完了しました！
echo =====================================
echo.
echo デスクトップに以下のアイコンが作成されました：
echo - Wildlife Detector (アプリケーション起動用)
echo - Wildlife Detector Output (結果の保存先)
echo.
echo アプリケーションを起動するには、
echo デスクトップの「Wildlife Detector」をダブルクリックしてください。
echo.
pause
