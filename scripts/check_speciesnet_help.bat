@echo off
echo Checking SpeciesNet command line options...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

call venv\Scripts\activate

python -m speciesnet.scripts.run_model --help

pause
