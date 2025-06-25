"""
List SpeciesNet module parameters
"""
import sys
import subprocess
from pathlib import Path

# Get venv python
venv_python = Path.cwd() / "venv" / "Scripts" / "python.exe"

# Try to get help
cmd = [str(venv_python), '-m', 'speciesnet.scripts.run_model', '--help']

print("Running: " + ' '.join(cmd))
print("=" * 80)

result = subprocess.run(cmd, capture_output=True, text=True)

if result.stdout:
    print(result.stdout)
    
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)
