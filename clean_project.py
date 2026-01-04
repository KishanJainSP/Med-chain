#!/usr/bin/env python3
"""
MedChain Project Cleaner
Removes unnecessary files and creates a clean production-ready version
"""

import os
import shutil
from pathlib import Path

# Files and directories to remove
REMOVE_PATTERNS = [
    # Documentation and analysis files
    "*.md",
    "ANALYSIS_*",
    "CORS_*", 
    "ENHANCED_*",
    "FINAL_*",
    "INSTITUTIONS_*",
    "LOCAL_*",
    "LOGIN_*",
    "OLLAMA_*",
    "WALLET_*",
    "CHAT_*",
    
    # Test and debug files
    "backend/test_*.py",
    "backend/debug_*.py",
    "backend/check_*.py",
    "backend/fix_*.py",
    "backend/setup_*.py",
    "backend/start_*.py",
    "backend/switch_*.py",
    "backend/quick_*.py",
    "backend/install_*.py",
    "backend/fallback.py",
    
    # Batch files
    "*.bat",
    
    # Backup files
    "*_backup_*",
    "*_original_*",
    
    # Training files (keep structure but remove large files)
    "backend/training/data/",
    "backend/training/models/",
    "backend/training/checkpoints/",
    
    # Cache and temp files
    "backend/__pycache__/",
    "backend/**/__pycache__/",
    "frontend/node_modules/",
    "frontend/build/",
    ".emergent/",
    ".vscode/",
    
    # Git files (optional - keep if you want version control)
    # ".git/",
    # ".gitignore",
    # ".gitconfig",
]

# Essential files to keep
KEEP_FILES = [
    "backend/server.py",
    "backend/database.py", 
    "backend/ollama_assistant.py",
    "backend/ai_models.py",
    "backend/ai_models_finetuned.py",
    "backend/requirements.txt",
    "backend/.env",
    "backend/routes/",
    "backend/uploads/",
    "frontend/",
    "run.py",
    "setup.py",
    "requirements-minimal.txt",
    "README.md",  # Keep main README
]

def should_keep_file(file_path):
    """Check if a file should be kept"""
    file_str = str(file_path)
    
    # Always keep essential files
    for keep_pattern in KEEP_FILES:
        if keep_pattern in file_str:
            return True
    
    # Check if file matches removal patterns
    for pattern in REMOVE_PATTERNS:
        if pattern.startswith("*") and pattern.endswith("*"):
            # Contains pattern
            if pattern[1:-1] in file_path.name:
                return False
        elif pattern.startswith("*"):
            # Ends with pattern
            if file_path.name.endswith(pattern[1:]):
                return False
        elif pattern.endswith("*"):
            # Starts with pattern
            if file_path.name.startswith(pattern[:-1]):
                return False
        elif pattern == file_str or pattern in file_str:
            return False
    
    return True

def clean_project():
    """Clean the project directory"""
    print("🧹 Cleaning MedChain project...")
    
    removed_count = 0
    kept_count = 0
    
    # Walk through all files
    for root, dirs, files in os.walk("."):
        root_path = Path(root)
        
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        
        for file in files:
            file_path = root_path / file
            
            if should_keep_file(file_path):
                kept_count += 1
                print(f"   ✅ Keeping: {file_path}")
            else:
                try:
                    file_path.unlink()
                    removed_count += 1
                    print(f"   🗑️  Removed: {file_path}")
                except Exception as e:
                    print(f"   ❌ Error removing {file_path}: {e}")
    
    # Remove empty directories
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):  # Directory is empty
                    dir_path.rmdir()
                    print(f"   🗑️  Removed empty directory: {dir_path}")
            except:
                pass  # Directory not empty or other error
    
    print(f"\n📊 Cleanup complete:")
    print(f"   Files kept: {kept_count}")
    print(f"   Files removed: {removed_count}")

def create_clean_readme():
    """Create a clean README for the production version"""
    readme_content = """# MedChain - Medical Records Management System

A blockchain-based medical records management system with AI-powered analysis and chat features.

## Features

- 🏥 **Institution Management** - Register and manage medical institutions
- 👨‍⚕️ **Doctor Registration** - Healthcare provider onboarding
- 👤 **Patient Records** - Secure medical record storage
- 🤖 **AI Analysis** - Medical image and text analysis
- 💬 **AI Chat** - Intelligent medical assistant
- 🔒 **Consent Management** - Patient consent tracking
- 📱 **Modern UI** - React-based responsive interface

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- (Optional) Ollama for AI chat features

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd medchain
   python setup.py
   ```

2. **Start the application:**
   ```bash
   python run.py
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

**Using Docker:**
```bash
docker-compose up -d
```

**Manual deployment:**
```bash
# Install minimal dependencies
pip install -r requirements-minimal.txt

# Build frontend
cd frontend && npm run build

# Start backend
python -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=medchain_local
HOST=0.0.0.0
PORT=8000
```

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Optional: Ollama Setup

For AI chat features:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3.2
```

## API Endpoints

- `POST /api/institutions` - Register institution
- `POST /api/doctors` - Register doctor
- `POST /api/patients` - Register patient
- `POST /api/records` - Upload medical record
- `POST /api/chat` - AI chat interface
- `GET /api/chat/sessions` - Chat session management

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- MongoDB (Database)
- Motor (Async MongoDB driver)
- Ollama (AI chat integration)

**Frontend:**
- React 19
- Tailwind CSS
- Radix UI components
- Axios (HTTP client)

## File Structure

```
medchain/
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── database.py        # MongoDB connection manager
│   ├── ollama_assistant.py # AI chat integration
│   ├── ai_models.py       # Medical AI models
│   └── uploads/           # File storage
├── frontend/
│   ├── src/               # React application
│   └── public/            # Static assets
├── run.py                 # Application launcher
├── setup.py               # Setup script
└── requirements-minimal.txt # Production dependencies
```

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository.
"""
    
    Path("README.md").write_text(readme_content)
    print("   ✅ Created production README.md")

def main():
    """Main cleanup function"""
    print("🏥 MedChain Project Cleaner")
    print("=" * 35)
    
    response = input("This will remove test files, documentation, and debug scripts. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    clean_project()
    create_clean_readme()
    
    print("\n🎉 Project cleaned successfully!")
    print("\nYour project is now production-ready with:")
    print("- Essential files only")
    print("- Single command launcher (run.py)")
    print("- Production deployment files")
    print("- Clean documentation")
    
    print("\nTo run your clean project:")
    print("1. python setup.py  (first time setup)")
    print("2. python run.py    (start application)")

if __name__ == "__main__":
    main()