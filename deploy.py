#!/usr/bin/env python3
"""
MedChain Deployment Script
Simple deployment for production environments
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def deploy_docker():
    """Deploy using Docker Compose"""
    print("🐳 Deploying with Docker...")
    
    # Check if Docker is available
    success, _ = run_command("docker --version")
    if not success:
        print("   ❌ Docker not found")
        return False
    
    success, _ = run_command("docker-compose --version")
    if not success:
        print("   ❌ Docker Compose not found")
        return False
    
    # Build and start services
    print("   Building containers...")
    success, output = run_command("docker-compose build")
    if not success:
        print(f"   ❌ Build failed: {output}")
        return False
    
    print("   Starting services...")
    success, output = run_command("docker-compose up -d")
    if not success:
        print(f"   ❌ Start failed: {output}")
        return False
    
    print("   ✅ Docker deployment complete")
    print("   Application available at: http://localhost:8000")
    return True

def deploy_manual():
    """Manual deployment without Docker"""
    print("⚙️  Manual deployment...")
    
    # Install backend dependencies
    print("   Installing backend dependencies...")
    success, _ = run_command(f"{sys.executable} -m pip install -r requirements-minimal.txt")
    if not success:
        print("   ❌ Failed to install backend dependencies")
        return False
    
    # Build frontend
    print("   Building frontend...")
    success, _ = run_command("npm run build", cwd="frontend")
    if not success:
        print("   ❌ Frontend build failed")
        return False
    
    # Create systemd service file (Linux)
    if os.name == 'posix':
        create_systemd_service()
    
    print("   ✅ Manual deployment prepared")
    print("   Start with: python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000")
    return True

def create_systemd_service():
    """Create systemd service file for Linux"""
    service_content = f"""[Unit]
Description=MedChain Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={Path.cwd()}
Environment=PATH={Path.cwd()}/venv/bin
ExecStart={Path.cwd()}/venv/bin/python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    service_path = Path("medchain.service")
    service_path.write_text(service_content)
    print(f"   ✅ Created systemd service file: {service_path}")
    print("   To install: sudo cp medchain.service /etc/systemd/system/")
    print("   To enable: sudo systemctl enable medchain")
    print("   To start: sudo systemctl start medchain")

def create_nginx_config():
    """Create Nginx configuration"""
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;

    # Frontend static files
    location / {
        root /path/to/medchain/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for development
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
"""
    
    Path("nginx.conf").write_text(nginx_config)
    print("   ✅ Created Nginx configuration: nginx.conf")

def main():
    """Main deployment function"""
    print("🚀 MedChain Deployment")
    print("=" * 25)
    
    print("Choose deployment method:")
    print("1. Docker Compose (recommended)")
    print("2. Manual deployment")
    print("3. Create configuration files only")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        if deploy_docker():
            print("\n🎉 Docker deployment successful!")
            print("Access your application at: http://localhost:8000")
        else:
            print("\n❌ Docker deployment failed")
            sys.exit(1)
    
    elif choice == "2":
        if deploy_manual():
            print("\n🎉 Manual deployment prepared!")
            print("Start the application with:")
            print("python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000")
        else:
            print("\n❌ Manual deployment failed")
            sys.exit(1)
    
    elif choice == "3":
        create_nginx_config()
        if os.name == 'posix':
            create_systemd_service()
        print("\n✅ Configuration files created")
    
    else:
        print("Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()