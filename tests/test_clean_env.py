"""
Test SpeciesNet with clean environment
"""
import os
import subprocess
import sys
from pathlib import Path

def test_speciesnet_clean():
    print("=== Testing SpeciesNet with clean environment ===\n")
    
    # Set up paths
    project_root = Path.cwd()
    venv_python = project_root / "venv" / "Scripts" / "python.exe"
    test_image = project_root / "tests" / "test_data" / "images" / "test_crow.JPG"
    output_file = project_root / "output" / "test_clean_env.json"
    
    print(f"Project root: {project_root}")
    print(f"Venv Python: {venv_python}")
    print(f"Test image: {test_image}")
    print(f"Output file: {output_file}\n")
    
    # Check files exist
    if not venv_python.exists():
        print(f"ERROR: Venv Python not found at {venv_python}")
        return
        
    if not test_image.exists():
        print(f"ERROR: Test image not found at {test_image}")
        return
    
    # Build command
    cmd = [
        str(venv_python), '-m', 'speciesnet.scripts.run_model',
        '--filepaths', str(test_image),
        '--predictions_json', str(output_file),
        '--country', 'JPN',
        '--batch_size', '1'
    ]
    
    print("Command:")
    print(' '.join(cmd))
    print()
    
    # Create clean environment
    env = os.environ.copy()
    
    # Remove miniforge3 from PATH
    path_parts = env.get('PATH', '').split(os.pathsep)
    filtered_path = [p for p in path_parts if 'miniforge3' not in p.lower()]
    
    # Ensure venv Scripts is at the beginning
    venv_scripts = str(project_root / "venv" / "Scripts")
    if venv_scripts not in filtered_path:
        filtered_path.insert(0, venv_scripts)
    
    env['PATH'] = os.pathsep.join(filtered_path)
    env['VIRTUAL_ENV'] = str(project_root / "venv")
    
    # Remove any Python-related environment variables
    for key in ['PYTHONHOME', 'PYTHONPATH']:
        env.pop(key, None)
    
    print("Environment PATH (first 5 entries):")
    for i, p in enumerate(filtered_path[:5]):
        print(f"  {i+1}. {p}")
    print()
    
    # Run command
    print("Running SpeciesNet...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(project_root)
    )
    
    print(f"Return code: {result.returncode}")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    # Check output file
    if output_file.exists():
        print(f"\nOutput file created successfully!")
        with open(output_file, 'r') as f:
            import json
            data = json.load(f)
            print(json.dumps(data, indent=2))
    else:
        print(f"\nERROR: Output file not created")

if __name__ == "__main__":
    test_speciesnet_clean()
