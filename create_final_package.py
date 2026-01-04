#!/usr/bin/env python3
"""
Create the final, bulletproof transfer package
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_final_package():
    """Create the final transfer package"""
    print("📦 Creating final bulletproof package...")
    
    # Remove old packages
    for old_file in ["medchain_portable.zip", "medchain_portable_fixed.zip", "medchain_ultimate.zip"]:
        if Path(old_file).exists():
            Path(old_file).unlink()
    
    # Create transfer directory
    transfer_dir = Path("medchain_final")
    if transfer_dir.exists():
        shutil.rmtree(transfer_dir)
    transfer_dir.mkdir()
    
    # Copy essential files
    essential_files = [
        "run_fixed.py",  # Use the fixed run script
        "ultra_simple_setup.py",
        "no_pip_setup.py", 
        "deploy.py",
        "requirements-minimal.txt"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, transfer_dir / file)
            print(f"   ✅ Copied: {file}")
    
    # Rename run_fixed.py to run.py in the package
    if (transfer_dir / "run_fixed.py").exists():
        (transfer_dir / "run_fixed.py").rename(transfer_dir / "run.py")
        print("   ✅ Renamed run_fixed.py to run.py")
    
    # Create setup files
    setup_files = {
        "setup.py": "ultra_simple_setup.py",
        "setup_no_pip.py": "no_pip_setup.py",
    }
    
    for dest, src in setup_files.items():
        if Path(src).exists():
            shutil.copy2(src, transfer_dir / dest)
            print(f"   ✅ Created: {dest}")
    
    # Copy backend
    backend_src = Path("backend")
    backend_dst = transfer_dir / "backend"
    backend_dst.mkdir()
    
    backend_files = [
        "server.py",
        "database.py", 
        "ollama_assistant.py",
        "ai_models.py",
        "ai_models_finetuned.py",
        "requirements.txt",
        ".env"
    ]
    
    for file in backend_files:
        src_file = backend_src / file
        if src_file.exists():
            shutil.copy2(src_file, backend_dst / file)
            print(f"   ✅ Copied: backend/{file}")
    
    # Copy routes if exists
    routes_src = backend_src / "routes"
    if routes_src.exists():
        shutil.copytree(routes_src, backend_dst / "routes")
        print("   ✅ Copied: backend/routes/")
    
    # Create uploads directory
    (backend_dst / "uploads").mkdir()
    
    # Copy frontend
    frontend_src = Path("frontend")
    if frontend_src.exists():
        shutil.copytree(frontend_src, transfer_dir / "frontend", 
                       ignore=shutil.ignore_patterns('node_modules', 'build'))
        print("   ✅ Copied: frontend/")
    
    # Create comprehensive README
    readme_content = """# MedChain - Bulletproof Installation

## 🚀 Quick Start (Works Everywhere)

### Method 1: Standard (Recommended)
```bash
python setup.py
python run.py
```

### Method 2: If pip issues
```bash
python setup_no_pip.py
python run.py
```

### Method 3: Manual (Always works)
```bash
pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests
cd frontend && npm install && cd ..
python run.py
```

## 🛠️ Windows npm Issues Fixed

This package automatically handles:
- ✅ npm not in PATH
- ✅ Node.js installation variations
- ✅ Windows-specific npm locations
- ✅ Fallback to backend-only mode

## 📋 Prerequisites

**Required:**
- Python 3.8+

**Optional (for full features):**
- Node.js 16+ (for frontend)
- MongoDB (for database)
- Ollama (for AI chat)

## 🎯 What Happens

1. **Setup checks everything** and installs dependencies
2. **Run script finds npm/node** automatically on Windows
3. **Starts backend** (always works if Python deps installed)
4. **Starts frontend** (if Node.js available)
5. **Falls back gracefully** if frontend fails

## 🆘 If Frontend Fails

The app will run in **backend-only mode**:
- ✅ All API endpoints work
- ✅ Database operations work
- ✅ AI features work
- 📖 Access via http://localhost:8000/docs

## 🔧 Troubleshooting

### "npm not found"
1. Install Node.js from https://nodejs.org/
2. Check "Add to PATH" during installation
3. Restart terminal/command prompt

### "pip not available"
1. `python -m ensurepip --upgrade`
2. Or reinstall Python from python.org

### "Permission denied"
1. Run as administrator (Windows)
2. Use `pip install --user <packages>`

## 🎉 Success Indicators

**Full mode:**
```
🎉 MedChain is running!
   Frontend: http://localhost:3000
   Backend: http://localhost:8000
```

**Backend-only mode:**
```
✅ Backend running at http://localhost:8000
💡 Frontend not available - install Node.js for full features
```

Both modes are fully functional! 🚀
"""
    
    (transfer_dir / "README.md").write_text(readme_content, encoding='utf-8')
    print("   ✅ Created: README.md")
    
    # Create quick start guide
    quickstart = """# Quick Start Guide

## 1. Extract Archive
Extract medchain_final.zip to any folder

## 2. Setup (One Time)
```bash
python setup.py
```

## 3. Run Application
```bash
python run.py
```

## 4. Access Application
- **Full mode**: http://localhost:3000 (if Node.js installed)
- **API mode**: http://localhost:8000/docs (always works)

## That's it! 🎉

The setup handles everything automatically:
- Finds Python packages
- Finds npm/Node.js (Windows compatible)
- Creates configuration files
- Falls back gracefully if components missing

## Need Help?
- Check README.md for detailed instructions
- Try `python setup_no_pip.py` if pip issues
- Backend-only mode works even without Node.js
"""
    
    (transfer_dir / "QUICKSTART.md").write_text(quickstart, encoding='utf-8')
    print("   ✅ Created: QUICKSTART.md")
    
    # Create archive
    archive_name = "medchain_final.zip"
    print(f"\n📦 Creating archive: {archive_name}")
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(transfer_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(transfer_dir)
                zipf.write(file_path, arc_path)
    
    # Cleanup
    shutil.rmtree(transfer_dir)
    
    # Get size
    size_mb = Path(archive_name).stat().st_size / (1024 * 1024)
    
    print(f"   ✅ Created: {archive_name} ({size_mb:.1f} MB)")
    
    return archive_name

def main():
    """Main function"""
    print("🏥 Creating Final MedChain Package")
    print("=" * 40)
    
    archive = create_final_package()
    
    print(f"\n🎉 Final package ready: {archive}")
    print("\n📋 This package fixes:")
    print("✅ Windows npm PATH issues")
    print("✅ Node.js detection problems") 
    print("✅ Frontend startup failures")
    print("✅ Graceful fallback to backend-only")
    print("✅ All previous pip/setup issues")
    
    print(f"\n🚀 On new device:")
    print("1. Extract the archive")
    print("2. python setup.py")
    print("3. python run.py")
    
    print(f"\n🛡️ Works even if frontend fails!")

if __name__ == "__main__":
    main()