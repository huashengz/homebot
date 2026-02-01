#!/usr/bin/env python3
"""
Setup script for AnyBot project
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version < (3, 10):
        print(f"❌ Python 3.10+ required. Found: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version OK: {version.major}.{version.minor}.{version.micro}")
    return True


def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("\n🐍 Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print("✅ Virtual environment created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("✅ Virtual environment already exists")
        return True


def activate_and_install():
    """Activate virtual environment and install dependencies"""
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install main dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing main dependencies"):
        return False
    
    # Install dev dependencies
    if Path("requirements-dev.txt").exists():
        if not run_command(f"{pip_cmd} install -r requirements-dev.txt", "Installing dev dependencies"):
            return False
    
    return True


def setup_pre_commit():
    """Setup pre-commit hooks"""
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        print("⚠️  Pre-commit setup failed (optional)")
    
    return True


def copy_env_file():
    """Copy .env.example to .env if it doesn't exist"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        try:
            with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file from .env.example")
            print("⚠️  Please edit .env file with your actual configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("⚠️  No .env.example file found")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs", "tests"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
        else:
            print(f"✅ Directory already exists: {directory}")


def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual API keys and configuration")
    print("2. Activate virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the development server:")
    print("   uvicorn app.main:app --reload")
    print("4. Or use VS Code launch configurations:")
    print("   Press F5 and select '🚀 Run FastAPI'")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")


def main():
    """Main setup function"""
    print("🚀 AnyBot Project Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Install dependencies
    if not activate_and_install():
        return 1
    
    # Copy environment file
    copy_env_file()
    
    # Create directories
    create_directories()
    
    # Setup pre-commit hooks
    setup_pre_commit()
    
    # Print next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)