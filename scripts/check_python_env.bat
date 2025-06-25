@echo off
echo Checking Python environment...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

echo Before activation:
where python
python --version
echo.

call venv\Scripts\activate

echo After activation:
where python
python --version
echo.

echo Python executable in script:
python -c "import sys; print(sys.executable)"
echo.

echo Checking if speciesnet is installed:
pip show speciesnet
echo.

echo Python path:
python -c "import sys; print('\n'.join(sys.path))"

pause
