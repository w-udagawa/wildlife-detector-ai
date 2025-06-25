@echo off
echo =====================================
echo Wildlife Detector AI - Bird Test Suite
echo =====================================
echo.

echo [1/4] Testing crow image...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_crow.JPG --predictions_json output/crow_result.json --country JPN --batch_size 1

echo.
echo [2/4] Testing duck image...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_duck.JPG --predictions_json output/duck_result.json --country JPN --batch_size 1

echo.
echo [3/4] Testing heron image...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_heron.JPG --predictions_json output/heron_result.json --country JPN --batch_size 1

echo.
echo [4/4] Testing kingfisher image...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_kilingfisher.JPG --predictions_json output/kingfisher_result.json --country JPN --batch_size 1

echo.
echo =====================================
echo All tests complete!
echo Check the output folder for results:
echo - output/crow_result.json
echo - output/duck_result.json
echo - output/heron_result.json
echo - output/kingfisher_result.json
echo =====================================
pause
