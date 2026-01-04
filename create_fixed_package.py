#!/usr/bin/env python3
"""
Create a fixed transfer package with simple setup
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_fixed_package():
    """Create transfer package with fixed setup"""
    print("📦 Creating fixed transfer package...")
    
    # Remove old package
    old_package = Path("medchain_portable.zip")
    if old_package.exists():
        old_package.unlink()
        print("   🗑️  Removed old package")
    
    # Create transfer directory
    transfer_dir = Path("medchain_fixed")
    if transfer_dir.exists():
        shutil.rmtree(transfer_dir)
    transfer_dir.mkdir()
    
    # Copy essential files
    essential_files = [
        "run.py",
        "simple_setup.py",  # Use simple setup instead
        "deploy.py",
        "requirements-minimal.txt"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, transfer_dir / file)
            print(f"   ✅ Copied: {file}")
    
    # Rename simple_setup.py to setup.py in the package
    if (transfer_dir / "simple_setup.py").exists():
        (transfer_dir / "simple_setup.py").rename(transfer_dir / "setup.py")
        print("   ✅ Renamed simple_setup.py to setup.py")
    
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
    
    # Copy frontend (excluding node_modules and build)
    frontend_src = Path("frontend")
    if frontend_src.exists():
        shutil.copytree(frontend_src, transfer_dir / "frontend", 
                       ignore=shutil.ignore_patterns('node_modules', 'build'))
        print("   ✅ Copied: frontend/")
    
    # Create simple README
    readme_content = """# MedChain - Portable Installation

## Quick Start (3 Commands)

1. **Setup (one time):**
   ```bash
   python setup.py
   ```

2. **Run application:**
   ```bash
   python run.py
   ```

3. **Access application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)

## Troubleshooting

If setup fails:
```bash
# Install dependencies manually
pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests

# Then run
python run.py
```

## Optional: AI Chat

For AI chat features:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.2
```

That's it! 🚀
"""
    
    (transfer_dir / "README.md").write_text(readme_content, encoding='utf-8')
    print("   ✅ Created: README.md")
    
    # Create archive
    archive_name = "medchain_portable_fixed.zip"
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
    print("🏥 Creating Fixed MedChain Package")
    print("=" * 35)
    
    archive = create_fixed_package()
    
    print(f"\n🎉 Fixed package ready: {archive}")
    print("\n📋 On new device:")
    print("1. Extract the archive")
    print("2. python setup.py")
    print("3. python run.py")
    print("\n✅ No virtual environment issues!")

if __name__ == "__main__":
    main()