@echo off
echo Checking SpeciesNet run_model help...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

call venv\Scripts\activate

echo Getting help with --help:
venv\Scripts\python -m speciesnet.scripts.run_model --help

echo.
echo ===============================
echo.
echo Getting help with --helpfull:
venv\Scripts\python -m speciesnet.scripts.run_model --helpfull

pause
