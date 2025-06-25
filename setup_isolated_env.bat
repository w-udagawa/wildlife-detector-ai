@echo off
chcp 65001 >nul
title Wildlife Detector AI セットアップ（独立環境版）

echo =====================================
echo Wildlife Detector AI v2.0
echo 社内配布用セットアップ（独立環境版）
echo =====================================
echo.
echo このセットアップは会社のPython環境に
echo 一切影響を与えません。
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

:: アプリケーション専用Pythonの確認
echo [1/6] 専用Python環境の確認...
if not exist python-portable (
    echo.
    echo Python環境が見つかりません。
    echo IT部門から提供された「python-portable」フォルダが
    echo このフォルダ内にあることを確認してください。
    echo.
    pause
    exit /b 1
)

:: 専用Pythonの動作確認
echo [2/6] Python環境の動作確認...
python-portable\python.exe --version >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo エラー: Python環境の起動に失敗しました。
    echo IT部門にお問い合わせください。
    echo.
    pause
    exit /b 1
)

:: 仮想環境の作成（専用Pythonを使用）
echo [3/6] アプリケーション環境の作成...
if exist app-env (
    echo 既存の環境を削除しています...
    rmdir /s /q app-env
)
python-portable\python.exe -m venv app-env
if %errorLevel% neq 0 (
    echo.
    echo エラー: 環境の作成に失敗しました。
    echo IT部門にお問い合わせください。
    echo.
    pause
    exit /b 1
)

:: 依存関係のインストール
echo [4/6] 必要なコンポーネントをインストール中...
echo （この処理には5-10分かかります）
echo.
call app-env\Scripts\activate.bat
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
echo [5/6] フォルダ構成の準備...
if not exist output mkdir output
if not exist logs mkdir logs
if not exist temp mkdir temp
if not exist cache mkdir cache

:: デスクトップショートカットの作成
echo [6/6] ショートカットの作成...
set "desktop=%USERPROFILE%\Desktop"
set "app_dir=%cd%"

:: アプリケーション起動用バッチファイル（独立環境版）
echo @echo off > "%desktop%\Wildlife Detector.bat"
echo cd /d "%app_dir%" >> "%desktop%\Wildlife Detector.bat"
echo call app-env\Scripts\activate.bat >> "%desktop%\Wildlife Detector.bat"
echo start python main.py >> "%desktop%\Wildlife Detector.bat"
echo exit >> "%desktop%\Wildlife Detector.bat"

:: アプリ内起動スクリプト（システムPythonに依存しない）
echo @echo off > "start_app.bat"
echo cd /d "%app_dir%" >> "start_app.bat"
echo call app-env\Scripts\activate.bat >> "start_app.bat"
echo python main.py >> "start_app.bat"
echo pause >> "start_app.bat"

:: 出力フォルダへのショートカット
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktop%\Wildlife Detector Output.lnk'); $Shortcut.TargetPath = '%app_dir%\output'; $Shortcut.Save()"

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
echo このアプリケーションは独立したPython環境で
echo 動作するため、会社のPython環境には
echo 一切影響を与えません。
echo.
echo デスクトップに以下のアイコンが作成されました：
echo - Wildlife Detector (アプリケーション起動用)
echo - Wildlife Detector Output (結果の保存先)
echo.
echo アプリケーションを起動するには、
echo デスクトップの「Wildlife Detector」をダブルクリックしてください。
echo.
pause
