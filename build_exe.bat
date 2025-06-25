@echo off
chcp 65001 >nul
title Wildlife Detector AI - EXEビルド

echo =====================================
echo Wildlife Detector AI v2.0
echo 実行ファイル（EXE）作成ツール
echo =====================================
echo.
echo システムPythonに一切影響を与えない
echo 単独実行可能ファイルを作成します。
echo =====================================
echo.

:: 仮想環境の確認
if not exist venv (
    echo エラー: 仮想環境が見つかりません。
    echo 先に quick_setup.bat を実行してください。
    pause
    exit /b 1
)

:: 仮想環境のアクティベート
call venv\Scripts\activate.bat

:: PyInstallerのインストール確認
echo [1/5] PyInstallerの確認...
pip show pyinstaller >nul 2>&1
if %errorLevel% neq 0 (
    echo PyInstallerをインストールしています...
    pip install pyinstaller
)

:: specファイルの作成
echo [2/5] ビルド設定ファイルを作成中...
echo # -*- mode: python ; coding: utf-8 -*- > wildlife_detector.spec
echo.>> wildlife_detector.spec
echo block_cipher = None >> wildlife_detector.spec
echo.>> wildlife_detector.spec
echo a = Analysis( >> wildlife_detector.spec
echo     ['main.py'], >> wildlife_detector.spec
echo     pathex=[], >> wildlife_detector.spec
echo     binaries=[], >> wildlife_detector.spec
echo     datas=[ >> wildlife_detector.spec
echo         ('config.yaml', '.'), >> wildlife_detector.spec
echo         ('core', 'core'), >> wildlife_detector.spec
echo         ('gui', 'gui'), >> wildlife_detector.spec
echo         ('utils', 'utils'), >> wildlife_detector.spec
echo         ('docs/START_GUIDE_JP.md', 'docs'), >> wildlife_detector.spec
echo         ('QUICK_START.md', '.'), >> wildlife_detector.spec
echo     ], >> wildlife_detector.spec
echo     hiddenimports=[ >> wildlife_detector.spec
echo         'PySide6', >> wildlife_detector.spec
echo         'speciesnet', >> wildlife_detector.spec
echo         'pandas', >> wildlife_detector.spec
echo         'PIL', >> wildlife_detector.spec
echo         'numpy', >> wildlife_detector.spec
echo     ], >> wildlife_detector.spec
echo     hookspath=[], >> wildlife_detector.spec
echo     hooksconfig={}, >> wildlife_detector.spec
echo     runtime_hooks=[], >> wildlife_detector.spec
echo     excludes=[], >> wildlife_detector.spec
echo     win_no_prefer_redirects=False, >> wildlife_detector.spec
echo     win_private_assemblies=False, >> wildlife_detector.spec
echo     cipher=block_cipher, >> wildlife_detector.spec
echo     noarchive=False, >> wildlife_detector.spec
echo ) >> wildlife_detector.spec
echo.>> wildlife_detector.spec
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher) >> wildlife_detector.spec
echo.>> wildlife_detector.spec
echo exe = EXE( >> wildlife_detector.spec
echo     pyz, >> wildlife_detector.spec
echo     a.scripts, >> wildlife_detector.spec
echo     a.binaries, >> wildlife_detector.spec
echo     a.zipfiles, >> wildlife_detector.spec
echo     a.datas, >> wildlife_detector.spec
echo     [], >> wildlife_detector.spec
echo     name='WildlifeDetector', >> wildlife_detector.spec
echo     debug=False, >> wildlife_detector.spec
echo     bootloader_ignore_signals=False, >> wildlife_detector.spec
echo     strip=False, >> wildlife_detector.spec
echo     upx=True, >> wildlife_detector.spec
echo     upx_exclude=[], >> wildlife_detector.spec
echo     runtime_tmpdir=None, >> wildlife_detector.spec
echo     console=False, >> wildlife_detector.spec
echo     disable_windowed_traceback=False, >> wildlife_detector.spec
echo     argv_emulation=False, >> wildlife_detector.spec
echo     target_arch=None, >> wildlife_detector.spec
echo     codesign_identity=None, >> wildlife_detector.spec
echo     entitlements_file=None, >> wildlife_detector.spec
echo     icon='gui/resources/icon.ico' >> wildlife_detector.spec
echo ) >> wildlife_detector.spec

:: アイコンファイルの確認
echo [3/5] アイコンファイルの準備...
if not exist gui\resources\icon.ico (
    echo 警告: アイコンファイルが見つかりません。
    echo デフォルトアイコンを使用します。
)

:: EXEのビルド
echo [4/5] 実行ファイルをビルド中...
echo （この処理には10-20分かかる場合があります）
echo.
pyinstaller --clean wildlife_detector.spec

if %errorLevel% neq 0 (
    echo.
    echo エラー: ビルドに失敗しました。
    echo ログを確認してください。
    pause
    exit /b 1
)

:: 配布フォルダの作成
echo [5/5] 配布フォルダを作成中...
set dist_folder=WildlifeDetector_Standalone
if exist %dist_folder% rmdir /s /q %dist_folder%
mkdir %dist_folder%

:: 必要なファイルをコピー
copy dist\WildlifeDetector.exe %dist_folder%\
copy QUICK_START.md %dist_folder%\
copy docs\START_GUIDE_JP.md %dist_folder%\

:: 出力フォルダを作成
mkdir %dist_folder%\output
mkdir %dist_folder%\logs
mkdir %dist_folder%\temp

:: 簡易起動バッチを作成
echo @echo off > %dist_folder%\WildlifeDetector起動.bat
echo start WildlifeDetector.exe >> %dist_folder%\WildlifeDetector起動.bat

:: READMEを作成
echo ===================================== > %dist_folder%\README.txt
echo Wildlife Detector AI v2.0 >> %dist_folder%\README.txt
echo スタンドアロン版 >> %dist_folder%\README.txt
echo ===================================== >> %dist_folder%\README.txt
echo. >> %dist_folder%\README.txt
echo このフォルダをお好きな場所に配置して >> %dist_folder%\README.txt
echo 「WildlifeDetector.exe」を >> %dist_folder%\README.txt
echo ダブルクリックで起動してください。 >> %dist_folder%\README.txt
echo. >> %dist_folder%\README.txt
echo ■ 特徴 >> %dist_folder%\README.txt
echo - Pythonのインストール不要 >> %dist_folder%\README.txt
echo - システムに影響を与えません >> %dist_folder%\README.txt
echo - USBメモリからも実行可能 >> %dist_folder%\README.txt
echo. >> %dist_folder%\README.txt
echo ■ 初回起動時の注意 >> %dist_folder%\README.txt
echo Windowsセキュリティの警告が出た場合： >> %dist_folder%\README.txt
echo 「詳細情報」→「実行」をクリック >> %dist_folder%\README.txt
echo ===================================== >> %dist_folder%\README.txt

:: ZIP作成
echo.
echo 配布用ZIPファイルを作成中...
powershell -Command "Compress-Archive -Path '%dist_folder%' -DestinationPath 'WildlifeDetector_v2.0_Standalone.zip' -Force"

echo.
echo =====================================
echo ✅ EXEビルドが完了しました！
echo =====================================
echo.
echo 作成されたファイル:
echo - WildlifeDetector.exe (実行ファイル)
echo - WildlifeDetector_v2.0_Standalone.zip (配布用)
echo.
echo このZIPファイルを配布すれば、
echo Pythonがインストールされていない
echo PCでも動作します。
echo.
pause
