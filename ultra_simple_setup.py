#!/usr/bin/env python3
"""
Ultra Simple MedChain Setup
Handles systems without pip or with various Python configurations
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"   ✅ Python {sys.version.split()[0]}")
    return True

def find_pip():
    """Find available pip command"""
    print("📦 Finding pip...")
    
    # Try different pip commands
    pip_commands = [
        f"{sys.executable} -m pip",
        "pip3",
        "pip",
        "python -m pip",
        "python3 -m pip"
    ]
    
    for pip_cmd in pip_commands:
        success, output = run_command(f"{pip_cmd} --version")
        if success:
            print(f"   ✅ Found pip: {pip_cmd}")
            return pip_cmd
    
    print("   ❌ No pip found")
    return None

def install_with_pip(pip_cmd):
    """Install dependencies using pip"""
    print(f"🔧 Installing with {pip_cmd}...")
    
    # Try requirements-minimal.txt first
    req_files = ["requirements-minimal.txt", "backend/requirements.txt"]
    
    for req_file in req_files:
        if Path(req_file).exists():
            print(f"   📋 Using {req_file}")
            
            # Try different installation methods
            install_methods = [
                f"{pip_cmd} install -r {req_file}",
                f"{pip_cmd} install --user -r {req_file}",
                f"{pip_cmd} install --break-system-packages -r {req_file}"
            ]
            
            for method in install_methods:
                print(f"   🔄 Trying: {method}")
                success, output = run_command(method)
                if success:
                    print("   ✅ Dependencies installed successfully")
                    return True
                else:
                    print(f"   ⚠️  Failed: {output[:100]}...")
    
    return False

def install_manually():
    """Install dependencies manually without pip"""
    print("🔧 Manual installation (no pip)...")
    
    # Essential packages that can be installed manually
    essential_packages = [
        "fastapi",
        "uvicorn", 
        "motor",
        "pymongo",
        "python-dotenv",
        "python-multipart",
        "aiofiles",
        "PyPDF2",
        "requests",
        "pydantic",
        "starlette"
    ]
    
    print("   📋 Required packages:")
    for pkg in essential_packages:
        print(f"      - {pkg}")
    
    print("\n   💡 Manual installation options:")
    print("   1. Install Python with pip from python.org")
    print("   2. Use package manager:")
    print("      - Windows: choco install python")
    print("      - macOS: brew install python")
    print("      - Linux: apt install python3-pip")
    print("   3. Download packages manually from PyPI")
    
    return False

def check_node():
    """Check Node.js"""
    print("📦 Checking Node.js...")
    success, output = run_command("node --version")
    if not success:
        print("   ❌ Node.js not found")
        print("   💡 Install from https://nodejs.org/")
        return False
    print(f"   ✅ Node.js {output.strip()}")
    return True

def install_frontend():
    """Install frontend dependencies"""
    print("🎨 Installing frontend...")
    
    if not Path("frontend").exists():
        print("   ❌ Frontend directory not found")
        return False
    
    # Try different npm commands
    npm_commands = ["npm install", "yarn install"]
    
    for cmd in npm_commands:
        print(f"   🔄 Trying: {cmd}")
        success, output = run_command(f"cd frontend && {cmd}")
        if success:
            print("   ✅ Frontend dependencies installed")
            return True
        else:
            print(f"   ⚠️  {cmd} failed")
    
    print("   ❌ Frontend installation failed")
    return False

def create_configs():
    """Create configuration files"""
    print("⚙️  Creating configs...")
    
    # Backend .env
    backend_env = """MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local
HOST=0.0.0.0
PORT=8000
"""
    
    backend_env_path = Path("backend/.env")
    backend_env_path.parent.mkdir(exist_ok=True)
    backend_env_path.write_text(backend_env)
    print("   ✅ Created backend/.env")
    
    # Frontend .env
    frontend_env = "REACT_APP_BACKEND_URL=http://localhost:8000\n"
    
    frontend_env_path = Path("frontend/.env")
    if frontend_env_path.parent.exists():
        frontend_env_path.write_text(frontend_env)
        print("   ✅ Created frontend/.env")

def test_installation():
    """Test if installation worked"""
    print("🧪 Testing installation...")
    
    try:
        import fastapi, uvicorn, motor, pymongo
        print("   ✅ Backend dependencies available")
        return True
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False

def show_manual_instructions():
    """Show manual installation instructions"""
    print("\n" + "="*50)
    print("📋 MANUAL INSTALLATION REQUIRED")
    print("="*50)
    
    print("\n🔧 Install Python packages manually:")
    print("pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests pydantic starlette")
    
    print("\n🎨 Install frontend packages:")
    print("cd frontend")
    print("npm install")
    print("cd ..")
    
    print("\n🚀 Then run:")
    print("python run.py")
    
    print("\n💡 If pip is not available:")
    print("1. Reinstall Python from python.org (check 'Add to PATH')")
    print("2. Or use: python -m ensurepip --upgrade")
    print("3. Or install packages from PyPI manually")

def main():
    """Main setup function"""
    print("🏥 MedChain Ultra Simple Setup")
    print("=" * 35)
    
    # Check Python
    if not check_python():
        print("\n❌ Python version too old")
        sys.exit(1)
    
    # Create configs first (always works)
    create_configs()
    
    # Try to install backend dependencies
    pip_cmd = find_pip()
    backend_success = False
    
    if pip_cmd:
        backend_success = install_with_pip(pip_cmd)
    
    if not backend_success:
        print("\n⚠️  Pip installation failed")
        install_manually()
        
        # Test if packages are already available
        if test_installation():
            print("   ✅ Dependencies already available!")
            backend_success = True
    
    # Check Node.js and install frontend
    node_available = check_node()
    frontend_success = False
    
    if node_available:
        frontend_success = install_frontend()
    
    # Final status
    print("\n" + "="*40)
    print("📊 SETUP SUMMARY")
    print("="*40)
    
    if backend_success:
        print("✅ Backend: Ready")
    else:
        print("❌ Backend: Manual installation needed")
    
    if frontend_success:
        print("✅ Frontend: Ready")
    elif node_available:
        print("❌ Frontend: npm install failed")
    else:
        print("❌ Frontend: Node.js not found")
    
    if backend_success and frontend_success:
        print("\n🎉 Setup complete! Run: python run.py")
    elif backend_success:
        print("\n⚠️  Backend ready, frontend needs manual setup")
        print("💡 Try: cd frontend && npm install")
    else:
        show_manual_instructions()

if __name__ == "__main__":
    main()