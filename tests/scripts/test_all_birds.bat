@echo off
echo Testing all bird images with SpeciesNet...
python -m speciesnet.scripts.run_model --folders tests/test_data/images --predictions_json output/all_birds_result.json --country JPN --batch_size 4
echo Done! Check output/all_birds_result.json for results.
pause
