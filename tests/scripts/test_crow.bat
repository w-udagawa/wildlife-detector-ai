@echo off
echo Testing crow image with SpeciesNet...
python -m speciesnet.scripts.run_model --filepaths tests/test_data/images/test_crow.JPG --predictions_json output/crow_result.json --country JPN --batch_size 1
echo Done! Check output/crow_result.json for results.
pause
