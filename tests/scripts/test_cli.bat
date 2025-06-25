@echo off
echo Wildlife Detector AI - CLI Test
echo ===============================
echo.

cd /d "%~dp0\..\.."

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Testing with crow image in CLI mode...
echo.

python main.py --image tests/test_data/images/test_crow.JPG --debug

echo.
echo ===============================
echo Test completed. Check the output above.
echo.

pause
