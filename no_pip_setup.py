#!/usr/bin/env python3
"""
No-Pip MedChain Setup
Works even when pip is not available
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    if sys.version_info < (3, 8):
        print(f"   ❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"   ✅ Python {sys.version.split()[0]}")
    return True

def check_existing_packages():
    """Check if required packages are already installed"""
    print("📦 Checking existing packages...")
    
    required_packages = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'motor': 'Async MongoDB driver',
        'pymongo': 'MongoDB driver',
        'pydantic': 'Data validation',
        'starlette': 'Web framework (FastAPI dependency)'
    }
    
    available = []
    missing = []
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            available.append(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package} - {description}")
    
    return available, missing

def create_minimal_server():
    """Create a minimal server that works with basic Python"""
    print("🔧 Creating minimal server...")
    
    minimal_server = '''#!/usr/bin/env python3
"""
Minimal MedChain Server - Works without external dependencies
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class MedChainHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>MedChain - Minimal Mode</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 20px; background: #f0f8ff; border-radius: 8px; }
                    .error { background: #ffe6e6; }
                    .success { background: #e6ffe6; }
                    .warning { background: #fff3cd; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏥 MedChain - Minimal Mode</h1>
                    
                    <div class="status warning">
                        <h3>⚠️ Running in Minimal Mode</h3>
                        <p>MedChain is running with basic Python only. Some features are limited.</p>
                    </div>
                    
                    <h3>📋 To enable full features:</h3>
                    <ol>
                        <li><strong>Install pip:</strong> python -m ensurepip --upgrade</li>
                        <li><strong>Install packages:</strong> pip install fastapi uvicorn motor pymongo python-dotenv</li>
                        <li><strong>Restart:</strong> python run.py</li>
                    </ol>
                    
                    <h3>🔧 Alternative installation methods:</h3>
                    <ul>
                        <li><strong>Windows:</strong> Reinstall Python from python.org (check "Add to PATH")</li>
                        <li><strong>macOS:</strong> brew install python</li>
                        <li><strong>Linux:</strong> apt install python3-pip</li>
                    </ul>
                    
                    <h3>📊 System Information:</h3>
                    <ul>
                        <li>Python Version: ''' + f"{sys.version}" + '''</li>
                        <li>Platform: ''' + f"{sys.platform}" + '''</li>
                        <li>Working Directory: ''' + f"{os.getcwd()}" + '''</li>
                    </ul>
                    
                    <div class="status">
                        <p><strong>Need help?</strong> Check the README.md file for detailed instructions.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        else:
            super().do_GET()

def start_minimal_server():
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), MedChainHandler) as httpd:
        print(f"   ✅ Minimal server running at http://localhost:{PORT}")
        print("   📋 Open your browser to see installation instructions")
        print("   🛑 Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n   🛑 Server stopped")

if __name__ == "__main__":
    start_minimal_server()
'''
    
    Path("minimal_server.py").write_text(minimal_server)
    print("   ✅ Created minimal_server.py")

def create_configs():
    """Create configuration files"""
    print("⚙️  Creating configs...")
    
    # Backend .env
    backend_env = """MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local
HOST=0.0.0.0
PORT=8000
"""
    
    backend_dir = Path("backend")
    backend_dir.mkdir(exist_ok=True)
    (backend_dir / ".env").write_text(backend_env)
    print("   ✅ Created backend/.env")
    
    # Frontend .env
    frontend_env = "REACT_APP_BACKEND_URL=http://localhost:8000\n"
    
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        (frontend_dir / ".env").write_text(frontend_env)
        print("   ✅ Created frontend/.env")

def create_install_guide():
    """Create installation guide"""
    guide = """# MedChain Installation Guide

## 🚨 Pip Not Available

Your system doesn't have pip installed. Here are several ways to fix this:

### Method 1: Enable pip (Recommended)
```bash
python -m ensurepip --upgrade
```

### Method 2: Reinstall Python
1. Download Python from https://python.org
2. During installation, check "Add Python to PATH"
3. Check "Install pip"

### Method 3: Package Manager
**Windows (Chocolatey):**
```bash
choco install python
```

**macOS (Homebrew):**
```bash
brew install python
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3-pip
```

### Method 4: Manual Package Installation
Download packages from https://pypi.org and install manually.

## 🔧 Required Packages
After fixing pip, install these packages:
```bash
pip install fastapi uvicorn motor pymongo python-dotenv python-multipart aiofiles PyPDF2 requests pydantic starlette
```

## 🚀 Then Run
```bash
python run.py
```

## 🆘 Emergency Mode
If nothing works, run the minimal server:
```bash
python minimal_server.py
```

This will show detailed installation instructions in your browser.
"""
    
    Path("INSTALL_GUIDE.md").write_text(guide)
    print("   ✅ Created INSTALL_GUIDE.md")

def main():
    """Main setup function"""
    print("🏥 MedChain No-Pip Setup")
    print("=" * 30)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Create configs
    create_configs()
    
    # Check existing packages
    available, missing = check_existing_packages()
    
    if not missing:
        print("\n🎉 All packages available! Run: python run.py")
        return
    
    # Create fallback options
    create_minimal_server()
    create_install_guide()
    
    print(f"\n📊 Status: {len(available)} available, {len(missing)} missing")
    print("\n💡 Options:")
    print("1. Fix pip and install packages (see INSTALL_GUIDE.md)")
    print("2. Run minimal server: python minimal_server.py")
    print("3. Install packages manually from PyPI")
    
    print(f"\n🔧 Missing packages: {', '.join(missing)}")
    print("\n📋 Quick fix:")
    print("python -m ensurepip --upgrade")
    print("pip install fastapi uvicorn motor pymongo python-dotenv")

if __name__ == "__main__":
    main()