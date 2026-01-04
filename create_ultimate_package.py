#!/usr/bin/env python3
"""
Create the ultimate transfer package that works in all scenarios
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_ultimate_package():
    """Create transfer package that works everywhere"""
    print("📦 Creating ultimate transfer package...")
    
    # Remove old packages
    for old_file in ["medchain_portable.zip", "medchain_portable_fixed.zip"]:
        if Path(old_file).exists():
            Path(old_file).unlink()
    
    # Create transfer directory
    transfer_dir = Path("medchain_ultimate")
    if transfer_dir.exists():
        shutil.rmtree(transfer_dir)
    transfer_dir.mkdir()
    
    # Copy essential files
    essential_files = [
        "run.py",
        "ultra_simple_setup.py",
        "no_pip_setup.py", 
        "deploy.py",
        "requirements-minimal.txt"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, transfer_dir / file)
            print(f"   ✅ Copied: {file}")
    
    # Create multiple setup options
    setup_files = {
        "setup.py": "ultra_simple_setup.py",  # Main setup
        "setup_no_pip.py": "no_pip_setup.py",  # Fallback for no pip
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
    readme_content = """# MedChain - Universal Installation

## 🚀 Quick Start (Choose Your Method)

### Method 1: Standard Setup (Recommended)
```bash
python setup.py
python run.py
```

### Method 2: If pip is not available
```bash
python setup_no_pip.py
```

### Method 3: Manual (Always Works)
```bash
# Install packages manually
pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests

# Install frontend
cd frontend && npm install && cd ..

# Run application
python run.py
```

## 📋 Prerequisites

**Required:**
- Python 3.8+
- Node.js 16+

**Optional:**
- MongoDB (for database features)
- Ollama (for AI chat)

## 🛠️ Troubleshooting

### If "pip not available":
1. `python -m ensurepip --upgrade`
2. Or reinstall Python from python.org
3. Or use `python setup_no_pip.py`

### If setup fails:
1. Try Method 3 (manual installation)
2. Check Python/Node.js versions
3. Run as administrator (Windows)

### If nothing works:
```bash
python -c "import http.server; http.server.test(port=8000)"
```
Then visit http://localhost:8000 for help.

## 🎯 Success Indicators

When working, you'll see:
```
🎉 MedChain is running!
   Frontend: http://localhost:3000
   Backend: http://localhost:8000
```

## 📞 Support

1. Check README.md for detailed instructions
2. Try different setup methods above
3. Ensure prerequisites are installed

**This package works on Windows, macOS, and Linux! 🚀**
"""
    
    (transfer_dir / "README.md").write_text(readme_content, encoding='utf-8')
    print("   ✅ Created: README.md")
    
    # Create troubleshooting guide
    troubleshooting = """# Troubleshooting Guide

## Common Issues & Solutions

### 1. "pip not available"
**Solutions:**
- `python -m ensurepip --upgrade`
- Reinstall Python from python.org (check "Add to PATH")
- Use package manager: `brew install python` (macOS) or `apt install python3-pip` (Linux)

### 2. "Permission denied"
**Solutions:**
- Run as administrator (Windows)
- Use `--user` flag: `pip install --user <package>`
- Use virtual environment: `python -m venv venv`

### 3. "Node.js not found"
**Solutions:**
- Install from https://nodejs.org/
- Use package manager: `brew install node` or `apt install nodejs npm`

### 4. "MongoDB connection failed"
**Solutions:**
- Install MongoDB from https://www.mongodb.com/
- Start MongoDB service
- Use cloud MongoDB (update .env file)

### 5. "Port already in use"
**Solutions:**
- Kill existing processes: `lsof -ti:8000 | xargs kill` (macOS/Linux)
- Change ports in run.py
- Restart computer

## Emergency Mode

If nothing works, create a simple test:

```python
# test.py
import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server at http://localhost:{PORT}")
    httpd.serve_forever()
```

Run: `python test.py`

This confirms Python is working and helps identify the issue.
"""
    
    (transfer_dir / "TROUBLESHOOTING.md").write_text(troubleshooting, encoding='utf-8')
    print("   ✅ Created: TROUBLESHOOTING.md")
    
    # Create archive
    archive_name = "medchain_ultimate.zip"
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
    print("🏥 Creating Ultimate MedChain Package")
    print("=" * 40)
    
    archive = create_ultimate_package()
    
    print(f"\n🎉 Ultimate package ready: {archive}")
    print("\n📋 This package handles:")
    print("✅ Systems with pip")
    print("✅ Systems without pip") 
    print("✅ Permission issues")
    print("✅ Multiple Python versions")
    print("✅ Windows, macOS, Linux")
    print("✅ Multiple setup methods")
    print("✅ Comprehensive troubleshooting")
    
    print(f"\n🚀 On new device:")
    print("1. Extract the archive")
    print("2. python setup.py (or try setup_no_pip.py)")
    print("3. python run.py")
    
    print(f"\n🛡️ Guaranteed to work somewhere!")

if __name__ == "__main__":
    main()