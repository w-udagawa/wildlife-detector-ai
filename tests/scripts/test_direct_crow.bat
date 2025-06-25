@echo off
echo Testing crow image DIRECTLY without any wrappers...
echo ===============================
echo.

cd /d C:\Users\AU3009\Claudeworks\projects\wildlife-detector

echo Deleting old output file if exists...
if exist output\test_direct_crow.json del output\test_direct_crow.json

echo.
echo Activating venv...
call venv\Scripts\activate

echo.
echo Running SpeciesNet...
venv\Scripts\python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_crow.JPG --predictions_json output/test_direct_crow.json --country JPN --batch_size 1

echo.
echo Exit code: %ERRORLEVEL%
echo.

if exist output\test_direct_crow.json (
    echo Output file created!
    echo.
    echo Content:
    type output\test_direct_crow.json
) else (
    echo ERROR: Output file NOT created
)

pause
