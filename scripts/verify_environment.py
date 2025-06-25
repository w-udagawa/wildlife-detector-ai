#!/usr/bin/env python3
"""
Wildlife Detector AI - Environment Verification Script
Checks if all required components are properly installed
"""

import sys
import importlib
import platform
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"🐍 Python Version: {version}")
    
    if sys.version_info.major == 3 and sys.version_info.minor == 12:
        print("   ✅ Python 3.12 detected - Compatible with SpeciesNet")
        return True
    else:
        print("   ❌ Python 3.12 required for SpeciesNet compatibility")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
        
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"   ✅ {package_name}: {version}")
        return True
    except ImportError:
        print(f"   ❌ {package_name}: Not installed")
        return False


def check_core_dependencies():
    """Check core dependencies"""
    print("\n📦 Core Dependencies:")
    packages = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("Pillow", "PIL"),
        ("OpenCV", "cv2"),
        ("PyYAML", "yaml"),
        ("click", "click"),
        ("structlog", "structlog"),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    return all(results)


def check_gui_dependencies():
    """Check GUI dependencies"""
    print("\n🎨 GUI Dependencies:")
    return check_package("PySide6", "PySide6")


def check_speciesnet():
    """Check SpeciesNet installation"""
    print("\n🦅 SpeciesNet:")
    try:
        import speciesnet
        print("   ✅ SpeciesNet: Installed")
        
        # Try to check if the model can be loaded
        try:
            from speciesnet.scripts import run_model
            print("   ✅ SpeciesNet scripts: Available")
            return True
        except ImportError:
            print("   ⚠️  SpeciesNet scripts: Not accessible")
            return False
    except ImportError:
        print("   ❌ SpeciesNet: Not installed")
        print("   💡 Install with: pip install git+https://github.com/microsoft/SpeciesNet.git")
        return False


def check_directories():
    """Check if required directories exist"""
    print("\n📁 Project Directories:")
    
    dirs = ["logs", "temp", "cache", "output", "tests/test_data/images"]
    all_exist = True
    
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (missing)")
            all_exist = False
    
    return all_exist


def check_virtual_environment():
    """Check if running in a virtual environment"""
    print("\n🔧 Environment:")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("   ✅ Running in virtual environment")
        print(f"   📍 Python executable: {sys.executable}")
        return True
    else:
        print("   ⚠️  Not running in virtual environment")
        print("   💡 Activate with: venv\\Scripts\\activate (Windows)")
        return False


def main():
    """Run all checks"""
    print("="*60)
    print("🔍 Wildlife Detector AI - Environment Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Core Dependencies", check_core_dependencies),
        ("GUI Dependencies", check_gui_dependencies),
        ("SpeciesNet", check_speciesnet),
        ("Project Directories", check_directories),
    ]
    
    results = {}
    for check_name, check_func in checks:
        results[check_name] = check_func()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print("="*60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 All checks passed! Environment is ready.")
    else:
        print("⚠️  Some checks failed. Please install missing components.")
        print("\n📋 Quick fixes:")
        print("1. Activate virtual environment: venv\\Scripts\\activate")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Install SpeciesNet: pip install git+https://github.com/microsoft/SpeciesNet.git")
    
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
