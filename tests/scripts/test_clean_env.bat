@echo off
echo Testing SpeciesNet with clean environment...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

call venv\Scripts\activate

python test_clean_env.py

pause
