#!/usr/bin/env python3
"""
Test the fixed transfer package
"""

import tempfile
import zipfile
from pathlib import Path

def test_fixed_package():
    """Test the fixed package"""
    print("🧪 Testing fixed package...")
    
    archive_path = Path("medchain_portable_fixed.zip")
    if not archive_path.exists():
        print("   ❌ Fixed archive not found")
        return False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract archive
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(temp_path)
        
        # Check files
        required_files = [
            "setup.py",
            "run.py",
            "requirements-minimal.txt",
            "backend/server.py",
            "frontend/package.json"
        ]
        
        for file in required_files:
            if (temp_path / file).exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} missing")
                return False
        
        # Check setup.py content
        setup_content = (temp_path / "setup.py").read_text(encoding='utf-8')
        if "venv" not in setup_content and "install_backend_deps" in setup_content:
            print("   ✅ Setup script is virtual environment free")
        else:
            print("   ❌ Setup script still has virtual environment code")
            return False
    
    print("   ✅ All tests passed!")
    return True

def main():
    """Main test"""
    print("🏥 Testing Fixed Package")
    print("=" * 25)
    
    if test_fixed_package():
        print("\n🎉 Fixed package is ready!")
        print("\n📦 Use: medchain_portable_fixed.zip")
        print("📋 Instructions:")
        print("1. Extract medchain_portable_fixed.zip")
        print("2. python setup.py")
        print("3. python run.py")
        print("\n✅ No virtual environment issues!")
    else:
        print("\n❌ Package test failed")

if __name__ == "__main__":
    main()