#!/usr/bin/env python3
"""
MedChain Setup Script
Automated setup for development and production environments
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    if sys.version_info < (3, 8):
        print("   ❌ Python 3.8+ required")
        return False
    print(f"   ✅ Python {sys.version.split()[0]}")
    return True

def check_node():
    """Check Node.js"""
    print("📦 Checking Node.js...")
    success, output = run_command("node --version", check=False)
    if not success:
        print("   ❌ Node.js not found")
        print("   Please install from https://nodejs.org/")
        return False
    print(f"   ✅ Node.js {output.strip()}")
    return True

def setup_backend():
    """Setup backend dependencies"""
    print("🔧 Setting up backend...")
    
    # Check if we should use requirements-minimal.txt or backend/requirements.txt
    if Path("requirements-minimal.txt").exists():
        requirements_file = "requirements-minimal.txt"
        print("   Using minimal requirements for portable deployment...")
    elif Path("backend/requirements.txt").exists():
        requirements_file = "backend/requirements.txt"
        print("   Using full requirements...")
    else:
        print("   ❌ No requirements file found")
        return False
    
    # Install backend dependencies directly (no virtual environment)
    print("   Installing Python packages...")
    success, output = run_command(f"{sys.executable} -m pip install -r {requirements_file}")
    if not success:
        print(f"   ❌ Failed to install Python packages: {output}")
        print("   💡 Trying with --user flag...")
        success, output = run_command(f"{sys.executable} -m pip install --user -r {requirements_file}")
        if not success:
            print(f"   ❌ Failed with --user flag: {output}")
            print("   💡 You may need to run as administrator or use: pip install -r requirements-minimal.txt")
            return False
    
    print("   ✅ Backend setup complete")
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print("🎨 Setting up frontend...")
    
    # Install frontend dependencies
    print("   Installing npm packages...")
    success, _ = run_command("npm install", cwd="frontend")
    if not success:
        print("   ❌ Failed to install npm packages")
        return False
    
    print("   ✅ Frontend setup complete")
    return True

def setup_database():
    """Setup database configuration"""
    print("🗄️  Setting up database...")
    
    # Check if MongoDB is running
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        client.close()
        print("   ✅ MongoDB connection verified")
        return True
    except ImportError:
        print("   ⚠️  pymongo not installed yet, will check after backend setup")
        return True
    except Exception:
        print("   ⚠️  MongoDB not running")
        print("   Please start MongoDB or install it from https://www.mongodb.com/")
        print("   The application will still work with a local MongoDB instance")
        return True

def create_env_files():
    """Create environment configuration files"""
    print("⚙️  Creating configuration files...")
    
    # Backend .env
    backend_env = """# MongoDB Configuration - LOCAL
MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local

# CORS Configuration  
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3002

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    backend_env_path = Path("backend/.env")
    if not backend_env_path.exists():
        backend_env_path.write_text(backend_env)
        print("   ✅ Created backend/.env")
    else:
        print("   ✅ Backend .env already exists")
    
    # Frontend .env
    frontend_env = "REACT_APP_BACKEND_URL=http://localhost:8000\n"
    
    frontend_env_path = Path("frontend/.env")
    if not frontend_env_path.exists():
        frontend_env_path.write_text(frontend_env)
        print("   ✅ Created frontend/.env")
    else:
        print("   ✅ Frontend .env already exists")

def setup_ollama():
    """Check and setup Ollama (optional)"""
    print("🤖 Checking Ollama (optional AI features)...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any("llama3.2" in model.get("name", "") for model in models):
                print("   ✅ Ollama with llama3.2 model ready")
            else:
                print("   ⚠️  Ollama running but llama3.2 model not found")
                print("   Run: ollama pull llama3.2")
        else:
            raise Exception("Not responding")
    except Exception:
        print("   ⚠️  Ollama not available")
        print("   Install from https://ollama.ai/ for full AI chat features")
        print("   The application will work without Ollama (limited chat)")

def create_production_files():
    """Create production deployment files"""
    print("📦 Creating production files...")
    
    # Create requirements-prod.txt with minimal dependencies
    prod_requirements = """fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pymongo==4.5.0
python-dotenv==1.2.1
python-multipart==0.0.21
aiofiles==25.1.0
PyPDF2==3.0.1
requests==2.32.5
pydantic==2.12.5
"""
    
    Path("requirements-prod.txt").write_text(prod_requirements)
    print("   ✅ Created requirements-prod.txt")
    
    # Create Dockerfile
    dockerfile = """FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy backend code
COPY backend/ ./backend/
COPY run.py .

# Copy frontend build
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create uploads directory
RUN mkdir -p backend/uploads

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    Path("Dockerfile").write_text(dockerfile)
    print("   ✅ Created Dockerfile")
    
    # Create docker-compose.yml
    docker_compose = """version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: medchain-mongo
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_DATABASE: medchain_local

  medchain:
    build: .
    container_name: medchain-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=medchain_local
    volumes:
      - ./backend/uploads:/app/backend/uploads

volumes:
  mongodb_data:
"""
    
    Path("docker-compose.yml").write_text(docker_compose)
    print("   ✅ Created docker-compose.yml")

def main():
    """Main setup function"""
    print("🏥 MedChain Setup")
    print("=" * 30)
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    if not check_node():
        sys.exit(1)
    
    # Setup components
    create_env_files()
    
    if not setup_backend():
        sys.exit(1)
    
    if not setup_frontend():
        sys.exit(1)
    
    setup_database()
    setup_ollama()
    create_production_files()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start MongoDB if not running")
    print("2. (Optional) Install Ollama and run: ollama pull llama3.2")
    print("3. Run the application: python run.py")
    print("\nFor production deployment:")
    print("- Use docker-compose up -d")
    print("- Or deploy using the created Dockerfile")

if __name__ == "__main__":
    main()