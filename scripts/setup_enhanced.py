"""
Wildlife Detector AI v2.0 Setup Script (Enhanced)
Automates the initial setup process with better error handling
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import time


class SetupManager:
    """Manages the setup process for Wildlife Detector AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
    def check_python_version(self):
        """Verify Python 3.12 is being used"""
        print(f"🐍 Checking Python version...")
        print(f"   Current version: {self.python_version}")
        
        if self.python_version != "3.12":
            print("❌ ERROR: Python 3.12 is required for SpeciesNet compatibility!")
            print("   Please install Python 3.12 and run this script again.")
            return False
            
        print("✅ Python 3.12 detected")
        return True
        
    def create_virtual_environment(self):
        """Create a virtual environment"""
        print("\n📦 Creating virtual environment...")
        
        if self.venv_path.exists():
            print("   Virtual environment already exists")
            return True
            
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], 
                         check=True, cwd=self.project_root)
            print("✅ Virtual environment created")
            
            # Wait a moment for venv to be fully created
            time.sleep(2)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
            
    def get_python_executable(self):
        """Get the correct python executable for the virtual environment"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
            
    def get_pip_command(self):
        """Get the correct pip command for the virtual environment"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
            
    def upgrade_pip(self):
        """Upgrade pip to the latest version"""
        print("\n🔧 Upgrading pip...")
        python_exe = self.get_python_executable()
        
        try:
            # Method 1: Use python -m pip
            print("   Attempting upgrade method 1...")
            subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, cwd=self.project_root)
            print("✅ Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError:
            print("   Method 1 failed, trying alternative method...")
            
        try:
            # Method 2: Direct pip command
            pip_cmd = self.get_pip_command()
            if Path(pip_cmd).exists():
                subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                             check=True, cwd=self.project_root)
                print("✅ Pip upgraded successfully (method 2)")
                return True
        except subprocess.CalledProcessError:
            pass
            
        # If both methods fail, continue anyway
        print("⚠️  Warning: Could not upgrade pip, but continuing with setup...")
        print("   You can manually upgrade pip later with: python -m pip install --upgrade pip")
        return True
            
    def install_dependencies(self):
        """Install project dependencies"""
        print("\n📚 Installing dependencies...")
        python_exe = self.get_python_executable()
        
        try:
            # Install main dependencies using python -m pip
            print("   Installing from requirements.txt...")
            result = subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                print(f"⚠️  Some packages failed to install:")
                print(result.stderr)
                print("\n   Continuing with partial installation...")
            else:
                print("✅ Dependencies installed")
            
            # Note about SpeciesNet
            print("\n⚠️  Note: SpeciesNet must be installed separately:")
            print("   Activate the virtual environment and run:")
            print("   pip install git+https://github.com/microsoft/SpeciesNet.git")
            
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating project directories...")
        
        directories = [
            "logs",
            "temp",
            "cache",
            "output",
            "tests/test_data/images"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("✅ Directories created")
        return True
        
    def create_env_file(self):
        """Create .env file for environment variables"""
        print("\n🔐 Creating environment file...")
        
        env_path = self.project_root / ".env"
        if not env_path.exists():
            env_content = """# Wildlife Detector AI Environment Variables

# Debug mode
DEBUG=false

# Logging level
LOG_LEVEL=INFO

# SpeciesNet settings
SPECIESNET_COUNTRY=JPN
SPECIESNET_BATCH_SIZE=1

# Performance settings
MAX_WORKERS=4
ENABLE_GPU=auto
"""
            env_path.write_text(env_content)
            print("✅ .env file created")
        else:
            print("   .env file already exists")
            
        return True
        
    def create_gitignore(self):
        """Create or update .gitignore file"""
        print("\n📝 Creating .gitignore...")
        
        gitignore_path = self.project_root / ".gitignore"
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
logs/
temp/
cache/
output/
*.log
.env
*.db

# OS
.DS_Store
Thumbs.db

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Profiling
profiles/
*.prof
"""
        gitignore_path.write_text(gitignore_content)
        print("✅ .gitignore created")
        return True
        
    def create_manual_setup_script(self):
        """Create a manual setup script for fallback"""
        print("\n📄 Creating manual setup script...")
        
        script_content = """@echo off
echo Wildlife Detector AI - Manual Setup
echo ====================================
echo.

echo Activating virtual environment...
call venv\\Scripts\\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! 
echo.
echo Next steps:
echo 1. Install SpeciesNet:
echo    pip install git+https://github.com/microsoft/SpeciesNet.git
echo 2. Verify installation:
echo    python -c "import speciesnet; print('SpeciesNet OK')"
echo.
pause
"""
        
        manual_script_path = self.project_root / "manual_setup.bat"
        manual_script_path.write_text(script_content)
        print("✅ manual_setup.bat created")
        return True
        
    def display_next_steps(self):
        """Display next steps for the user"""
        print("\n" + "="*50)
        print("🎉 Setup completed!")
        print("="*50)
        
        print("\n📋 Next steps:")
        print("\n1. Activate the virtual environment:")
        if platform.system() == "Windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
            
        print("\n2. (Optional) Upgrade pip manually if needed:")
        print("   python -m pip install --upgrade pip")
            
        print("\n3. Install SpeciesNet:")
        print("   pip install git+https://github.com/microsoft/SpeciesNet.git")
        
        print("\n4. Verify SpeciesNet installation:")
        print("   python -c \"import speciesnet; print('SpeciesNet installed successfully!')\"")
        
        print("\n5. Run the test suite:")
        print("   pytest tests/")
        
        print("\n6. Start development:")
        print("   python main.py")
        
        print("\n💡 Tip: If you encounter issues, try running manual_setup.bat")
        print("\n📚 For more information, see DEVELOPMENT_PLAN.md")
        print("\n" + "="*50)
        
    def run(self):
        """Run the complete setup process"""
        print("🚀 Wildlife Detector AI v2.0 Setup")
        print("="*50)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Upgrading pip", self.upgrade_pip),
            ("Installing dependencies", self.install_dependencies),
            ("Creating directories", self.create_directories),
            ("Creating environment file", self.create_env_file),
            ("Creating .gitignore", self.create_gitignore),
            ("Creating manual setup script", self.create_manual_setup_script),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n⚠️  Setup encountered an issue at: {step_name}")
                print("   But continuing with remaining steps...")
                
        self.display_next_steps()
        return True


if __name__ == "__main__":
    setup = SetupManager()
    success = setup.run()
    sys.exit(0 if success else 1)
