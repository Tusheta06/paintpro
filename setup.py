"""
PaintPro Inventory Management System
=====================================
Setup Script

Provides automated project setup: creates required directories,
validates the Python version, and runs the database migration.
"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_version():
    """Ensure Python 3.11+ is being used."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required.")
        print(f"   You are running Python {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected.")


def create_directories():
    """Create all required directories if they don't exist."""
    directories = [
        "assets/images/products",
        "assets/css",
        "assets/icons",
        "assets/fonts",
        "reports",
        ".streamlit",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure verified.")


def install_requirements():
    """Install Python dependencies from requirements.txt."""
    print("📦 Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=False,
        check=False,
    )
    if result.returncode == 0:
        print("✅ Dependencies installed successfully.")
    else:
        print("❌ Failed to install some dependencies. Check the output above.")


def setup_env():
    """Copy .env.example to .env if .env doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env file created from .env.example")
        print("   ⚠️  Please edit .env with your database credentials!")
    elif env_file.exists():
        print("✅ .env file already exists.")
    else:
        print("⚠️  .env.example not found. Please create .env manually.")


def run_migrations():
    """Run database schema migrations."""
    try:
        print("🗄️  Running database migrations...")
        result = subprocess.run(
            [sys.executable, "database/migrations.py"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("✅ Database migrations completed.")
        else:
            print("⚠️  Migration had issues:")
            print(result.stderr)
            print("   Ensure MySQL is running and .env credentials are correct.")
    except FileNotFoundError:
        print("⚠️  migrations.py not found. Run manually after setup.")


def main():
    """Main setup entry point."""
    print("\n" + "=" * 60)
    print("   🎨 PaintPro IMS - Project Setup")
    print("=" * 60 + "\n")

    check_python_version()
    create_directories()
    setup_env()

    if "--no-install" not in sys.argv:
        install_requirements()

    if "--no-db" not in sys.argv:
        run_migrations()

    print("\n" + "=" * 60)
    print("   ✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Edit .env with your MySQL credentials")
    print("  2. Run: streamlit run app.py")
    print("  3. Open http://localhost:8501")
    print("  4. Login: admin@paintpro.com / Admin@123\n")


if __name__ == "__main__":
    main()
