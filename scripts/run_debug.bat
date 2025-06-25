@echo off
echo Wildlife Detector AI - Debug Mode
echo ================================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Wildlife Detector in debug mode...
echo.

python main.py --debug

pause
