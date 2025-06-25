@echo off
echo Testing direct SpeciesNet command...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

echo Current directory: %CD%
echo.

call venv\Scripts\activate

echo Python location:
where python
echo.

echo Running SpeciesNet directly...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_crow.JPG --predictions_json output/test_direct.json --country JPN --batch_size 1

echo.
echo Exit code: %ERRORLEVEL%
echo.

if exist output\test_direct.json (
    echo Output file created successfully
    type output\test_direct.json
) else (
    echo Output file was NOT created
)

pause
