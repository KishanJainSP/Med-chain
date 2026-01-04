#!/usr/bin/env python3
"""
Prepare MedChain project for transfer to another device
Creates a clean, minimal version ready for archiving
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_transfer_package():
    """Create a clean package ready for transfer"""
    print("📦 Preparing MedChain for transfer...")
    
    # Create transfer directory
    transfer_dir = Path("medchain_transfer")
    if transfer_dir.exists():
        shutil.rmtree(transfer_dir)
    transfer_dir.mkdir()
    
    print("   📁 Creating clean project structure...")
    
    # Essential files to copy
    essential_files = [
        "run.py",
        "setup.py", 
        "deploy.py",
        "requirements-minimal.txt",
        "README.md"
    ]
    
    # Copy essential root files
    for file in essential_files:
        if Path(file).exists():
            shutil.copy2(file, transfer_dir / file)
            print(f"   ✅ Copied: {file}")
    
    # Copy backend (essential files only)
    backend_src = Path("backend")
    backend_dst = transfer_dir / "backend"
    backend_dst.mkdir()
    
    backend_essential = [
        "server.py",
        "database.py", 
        "ollama_assistant.py",
        "ai_models.py",
        "ai_models_finetuned.py",
        "requirements.txt",
        ".env"
    ]
    
    for file in backend_essential:
        src_file = backend_src / file
        if src_file.exists():
            shutil.copy2(src_file, backend_dst / file)
            print(f"   ✅ Copied: backend/{file}")
    
    # Copy routes directory if it exists
    routes_src = backend_src / "routes"
    if routes_src.exists():
        shutil.copytree(routes_src, backend_dst / "routes")
        print("   ✅ Copied: backend/routes/")
    
    # Create uploads directory
    (backend_dst / "uploads").mkdir()
    print("   ✅ Created: backend/uploads/")
    
    # Copy entire frontend
    frontend_src = Path("frontend")
    if frontend_src.exists():
        # Copy frontend but exclude node_modules and build
        shutil.copytree(frontend_src, transfer_dir / "frontend", 
                       ignore=shutil.ignore_patterns('node_modules', 'build', '.git'))
        print("   ✅ Copied: frontend/ (excluding node_modules)")
    
    # Create installation instructions
    install_instructions = """# MedChain - Quick Setup Instructions

## On the new device:

1. **Extract the archive**
2. **Install prerequisites:**
   - Python 3.8+ 
   - Node.js 16+
   - MongoDB

3. **Run setup (one command):**
   ```bash
   python setup.py
   ```

4. **Start the application:**
   ```bash
   python run.py
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## Optional: AI Chat Features
```bash
# Install Ollama for AI chat
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

## That's it! 🎉

The setup.py script will automatically:
- Install all Python dependencies
- Install Node.js dependencies  
- Create configuration files
- Check system requirements

The run.py script will:
- Start both frontend and backend
- Check dependencies
- Monitor both services
- Handle graceful shutdown
"""
    
    (transfer_dir / "INSTALL.md").write_text(install_instructions, encoding='utf-8')
    print("   ✅ Created: INSTALL.md")
    
    # Create archive
    archive_name = "medchain_portable"
    print(f"\n📦 Creating archive: {archive_name}.zip")
    
    with zipfile.ZipFile(f"{archive_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(transfer_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(transfer_dir)
                zipf.write(file_path, arc_path)
                
    # Get archive size
    archive_size = Path(f"{archive_name}.zip").stat().st_size / (1024 * 1024)
    
    print(f"   ✅ Archive created: {archive_name}.zip ({archive_size:.1f} MB)")
    
    # Cleanup transfer directory
    shutil.rmtree(transfer_dir)
    
    print(f"\n🎉 Transfer package ready!")
    print(f"   📁 Archive: {archive_name}.zip")
    print(f"   📏 Size: {archive_size:.1f} MB")
    print(f"\n📋 On new device:")
    print(f"   1. Extract {archive_name}.zip")
    print(f"   2. cd medchain_portable")
    print(f"   3. python setup.py")
    print(f"   4. python run.py")
    
    return f"{archive_name}.zip"

def verify_transfer_package():
    """Verify the transfer package contains everything needed"""
    print("\n🔍 Verifying transfer package...")
    
    required_files = [
        "run.py",
        "setup.py",
        "backend/server.py",
        "backend/database.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/src",
        "INSTALL.md"
    ]
    
    # Check if archive exists
    archive_path = Path("medchain_portable.zip")
    if not archive_path.exists():
        print("   ❌ Archive not found")
        return False
    
    # Check archive contents
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        archive_files = zipf.namelist()
        
        missing_files = []
        for required in required_files:
            if not any(required in f for f in archive_files):
                missing_files.append(required)
        
        if missing_files:
            print(f"   ❌ Missing files: {missing_files}")
            return False
        
        print("   ✅ All required files present")
        print(f"   📊 Total files in archive: {len(archive_files)}")
        
    return True

def main():
    """Main function"""
    print("🏥 MedChain Transfer Preparation")
    print("=" * 35)
    
    # Create transfer package
    archive_name = create_transfer_package()
    
    # Verify package
    if verify_transfer_package():
        print("\n✅ Transfer package verified and ready!")
        print(f"\n📤 To transfer to another device:")
        print(f"   1. Copy {archive_name} to the new device")
        print(f"   2. Extract the archive")
        print(f"   3. Run: python setup.py")
        print(f"   4. Run: python run.py")
        print(f"\n🔒 The application will work exactly as it does now!")
    else:
        print("\n❌ Transfer package verification failed")

if __name__ == "__main__":
    main()