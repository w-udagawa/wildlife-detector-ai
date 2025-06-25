@echo off
chcp 65001 >nul
title Wildlife Detector AI - 配布パッケージ作成

echo =====================================
echo Wildlife Detector AI v2.0
echo 配布パッケージ作成ツール
echo =====================================
echo.

:: 日付を取得
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set year=%%a
    set month=%%b
    set day=%%c
)
set today=%year%%month%%day%

:: 配布用フォルダ名
set dist_folder=wildlife-detector-setup
set zip_name=wildlife-detector-setup_%today%.zip

echo 配布パッケージを作成します...
echo.

:: 既存の配布フォルダを削除
if exist %dist_folder% (
    echo 既存の配布フォルダを削除しています...
    rmdir /s /q %dist_folder%
)

:: 配布用フォルダを作成
echo [1/4] フォルダ構造を作成中...
mkdir %dist_folder%
mkdir %dist_folder%\core
mkdir %dist_folder%\gui
mkdir %dist_folder%\utils
mkdir %dist_folder%\scripts
mkdir %dist_folder%\docs
mkdir %dist_folder%\tests\test_data\images

:: 必要なファイルをコピー
echo [2/4] ファイルをコピー中...

:: コアファイル
xcopy /s /q core\*.py %dist_folder%\core\
xcopy /s /q gui\*.py %dist_folder%\gui\
xcopy /s /q utils\*.py %dist_folder%\utils\

:: スクリプト
copy scripts\quick_setup.bat %dist_folder%\scripts\
copy scripts\verify_environment.py %dist_folder%\scripts\

:: メインファイル
copy main.py %dist_folder%\
copy config.yaml %dist_folder%\
copy requirements.txt %dist_folder%\
copy setup.py %dist_folder%\

:: ユーザー向けファイル
copy setup_for_users.bat %dist_folder%\
copy README_FOR_USERS.txt %dist_folder%\
copy QUICK_START.md %dist_folder%\

:: ドキュメント
copy docs\START_GUIDE_JP.md %dist_folder%\docs\

:: テスト画像（サンプル）
copy tests\test_data\images\test_crow.JPG %dist_folder%\tests\test_data\images\

:: 除外ファイルのチェック
echo [3/4] 不要なファイルを除外中...
del /q %dist_folder%\**\__pycache__\*.* 2>nul
del /q %dist_folder%\**\*.pyc 2>nul
del /q %dist_folder%\**\.DS_Store 2>nul

:: ZIP作成（PowerShell使用）
echo [4/4] ZIPファイルを作成中...
powershell -Command "Compress-Archive -Path '%dist_folder%' -DestinationPath '%zip_name%' -Force"

if exist %zip_name% (
    echo.
    echo =====================================
    echo ✅ 配布パッケージの作成が完了しました！
    echo =====================================
    echo.
    echo ファイル名: %zip_name%
    
    :: ファイルサイズを表示
    for %%F in (%zip_name%) do (
        set /a size=%%~zF/1048576
    )
    echo ファイルサイズ: 約%size%MB
    echo.
    echo このZIPファイルを社内ユーザーに配布してください。
) else (
    echo.
    echo ❌ エラー: ZIPファイルの作成に失敗しました。
)

:: 一時フォルダを削除
echo.
echo 一時フォルダを削除しています...
rmdir /s /q %dist_folder%

echo.
pause
