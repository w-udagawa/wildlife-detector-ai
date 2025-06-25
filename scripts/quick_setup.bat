@echo off
REM Wildlife Detector AI - Quick Setup for Windows
REM This script helps you set up the development environment

echo ========================================
echo Wildlife Detector AI v2.0 - Quick Setup
echo ========================================
echo.

REM Check if venv exists
if exist venv\ (
    echo Virtual environment found.
) else (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing wheel first (helps with package installation)...
pip install wheel

echo.
echo Installing core dependencies...
pip install numpy pandas pillow opencv-python pyyaml click structlog

echo.
echo Installing GUI dependencies...
pip install PySide6

echo.
echo Installing testing dependencies...
pip install pytest pytest-cov

echo.
echo ========================================
echo Basic setup complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Install SpeciesNet (when you have internet connection):
echo    pip install git+https://github.com/microsoft/SpeciesNet.git
echo.
echo 2. Or install remaining dependencies:
echo    pip install -r requirements.txt
echo.
echo 3. Test the installation:
echo    python main.py --help
echo.
pause
