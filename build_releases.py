#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Release builder for TikTok Live Watcher
Creates ready-to-run executables for Windows and macOS users
"""

import os
import shutil
import subprocess
import sys
import platform
import zipfile
from pathlib import Path

# Fix encoding issues on Windows
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error running: {cmd}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
        print(f"✅ Success: {cmd}")
        return True
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False

def clean_build_artifacts():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")

    for item in ["build", "dist", "*.spec"]:
        if item.endswith("*.spec"):
            for spec_file in Path(".").glob("*.spec"):
                spec_file.unlink()
                print(f"   Removed {spec_file}")
        else:
            path = Path(item)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   Removed {path}")

def build_executable(app_name="TikTok-Live-Watcher"):
    """Build the executable using PyInstaller"""
    print(f"🔨 Building {app_name} executable...")

    # Build command for a single executable file
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", app_name,
        "--add-data", "README.md:.",
        "--hidden-import", "managers.username_manager",
        "--hidden-import", "managers.settings_manager",
        "--hidden-import", "checkers.tiktok_checker",
        "--hidden-import", "recorders.stream_recorder",
        "--hidden-import", "ui.menu",
        "--console",
        "main.py"
    ]

    # Activate virtual environment and run PyInstaller
    venv_python = "venv/bin/python" if platform.system() != "Windows" else "venv\\Scripts\\python.exe"
    venv_pip = "venv/bin/pip" if platform.system() != "Windows" else "venv\\Scripts\\pip.exe"

    # Install PyInstaller in venv
    if not run_command(f"{venv_pip} install pyinstaller"):
        return False

    # Run PyInstaller
    full_cmd = f"{venv_python} -m PyInstaller " + " ".join(f'"{arg}"' if " " in arg else arg for arg in cmd[1:])

    if not run_command(full_cmd):
        return False

    return True

def create_user_package(platform_name):
    """Create a complete package for end users"""
    print(f"📦 Creating user package for {platform_name}...")

    # Determine executable extension
    exe_extension = ".exe" if platform_name == "Windows" else ""
    exe_name = f"TikTok-Live-Watcher{exe_extension}"

    # Create package directory
    package_name = f"TikTok-Live-Watcher-{platform_name}"
    package_dir = Path("releases") / package_name
    package_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable
    src_exe = Path("dist") / exe_name
    if not src_exe.exists():
        print(f"❌ Executable not found: {src_exe}")
        return None

    shutil.copy2(src_exe, package_dir / exe_name)
    print(f"   ✅ Copied executable: {exe_name}")

    # Create user-friendly README
    readme_content = f"""# TikTok Live Watcher - {platform_name}

## 🚀 Quick Start

### Step 1: Install Dependencies (One-time setup)
Run the setup script to install required tools:

{"**Windows:** Double-click `setup.bat`" if platform_name == "Windows" else "**macOS/Linux:** Run `./setup.sh` in Terminal"}

### Step 2: Run the App
{"**Windows:** Double-click `TikTok-Live-Watcher.exe`" if platform_name == "Windows" else f"**{platform_name}:** Double-click `TikTok-Live-Watcher` or run `./TikTok-Live-Watcher` in Terminal"}

## 📋 What the Setup Script Does

The setup script installs:
1. **streamlink** - For downloading TikTok live streams
2. **ffmpeg** - For video processing

## 🎮 How to Use

1. **Add usernames** - Add TikTok usernames you want to monitor (without @)
2. **Enable recording** - Toggle recording on/off (menu option 4)
3. **Start monitoring** - Select a username to monitor
4. **Recording** - When enabled, streams are automatically saved to `Recordings/` folder

## 🔧 Troubleshooting

### Recording not working?
- Make sure you ran the setup script successfully
- Check that ffmpeg is installed: `ffmpeg -version`
- Check that streamlink is installed: `streamlink --version`

### Can't find executable?
- Make sure you're running the correct file for your system
- {"On Windows: TikTok-Live-Watcher.exe" if platform_name == "Windows" else f"On {platform_name}: TikTok-Live-Watcher (no extension)"}

## 📁 Files Created

All files are created in the same folder as the executable:

- `Recordings/` - Your recorded live streams (next to the app)
- `usernames.json` - Your saved usernames
- `settings.json` - Your app preferences

**Note**: Recordings are always saved in a `Recordings/` folder next to the executable, regardless of where you run the app from.

## 🆘 Support

For help: https://github.com/mladejovskyy/tiktok-live-watcher/issues
"""

    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Create setup scripts
    if platform_name == "Windows":
        create_windows_setup(package_dir)
    else:
        create_unix_setup(package_dir, platform_name)

    return package_dir

def create_windows_setup(package_dir):
    """Create Windows setup script"""
    setup_script = """@echo off
echo ========================================
echo TikTok Live Watcher - Windows Setup
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python from: https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo Installing streamlink...

REM Try different installation methods
pip install streamlink >nul 2>&1
if %errorlevel%==0 (
    echo ✅ streamlink installed
    goto :check_ffmpeg
)

pip install --user streamlink >nul 2>&1
if %errorlevel%==0 (
    echo ✅ streamlink installed (user directory)
    goto :check_ffmpeg
)

pipx install streamlink >nul 2>&1
if %errorlevel%==0 (
    echo ✅ streamlink installed (via pipx)
    goto :check_ffmpeg
)

echo ⚠️  Automatic streamlink installation failed
echo.
echo Please install streamlink manually using one of these methods:
echo   Method 1 (pipx): pipx install streamlink
echo   Method 2 (user): pip install --user streamlink
echo   Method 3 (system): pip install --break-system-packages streamlink
echo   Method 4 (chocolatey): choco install streamlink
echo.
echo After installing streamlink, you can run TikTok-Live-Watcher.exe
echo.

:check_ffmpeg

echo.
echo Checking for ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  ffmpeg not found!
    echo.
    echo Please install ffmpeg:
    echo 1. Download from: https://ffmpeg.org/download.html#build-windows
    echo 2. Extract to C:\\ffmpeg\\
    echo 3. Add C:\\ffmpeg\\bin to your PATH environment variable
    echo.
    echo Alternative: Use chocolatey (if installed):
    echo   choco install ffmpeg
    echo.
    pause
) else (
    echo ✅ ffmpeg found
)

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo You can now run TikTok-Live-Watcher.exe
echo.
pause
"""

    with open(package_dir / "setup.bat", "w", encoding="utf-8") as f:
        f.write(setup_script)

def create_unix_setup(package_dir, platform_name):
    """Create Unix (macOS/Linux) setup script"""

    if platform_name == "macOS":
        ffmpeg_install = "brew install ffmpeg"
        python_install = "Download from https://python.org or use: brew install python"
    else:  # Linux
        ffmpeg_install = "sudo apt install ffmpeg  # or: sudo yum install ffmpeg"
        python_install = "sudo apt install python3 python3-pip  # or: sudo yum install python3 python3-pip"

    setup_script = f"""#!/bin/bash
echo "========================================"
echo "TikTok Live Watcher - {platform_name} Setup"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    echo
    echo "Please install Python3:"
    echo "  {python_install}"
    echo
    exit 1
fi
echo "✅ Python3 found"

echo
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found!"
    echo "Please install pip3 with Python"
    exit 1
fi
echo "✅ pip3 found"

echo
echo "Installing streamlink..."

# Try different installation methods for externally managed environments
if pip3 install streamlink 2>/dev/null; then
    echo "✅ streamlink installed"
elif pip3 install --user streamlink 2>/dev/null; then
    echo "✅ streamlink installed (user directory)"
elif command -v pipx &> /dev/null && pipx install streamlink 2>/dev/null; then
    echo "✅ streamlink installed (via pipx)"
elif command -v brew &> /dev/null && brew install streamlink 2>/dev/null; then
    echo "✅ streamlink installed (via brew)"
else
    echo "⚠️  Automatic streamlink installation failed"
    echo
    echo "Please install streamlink manually using one of these methods:"
    echo "  Method 1 (Homebrew): brew install streamlink"
    echo "  Method 2 (pipx): pipx install streamlink"
    echo "  Method 3 (user): pip3 install --user streamlink"
    echo "  Method 4 (system): pip3 install --break-system-packages streamlink"
    echo
    echo "After installing streamlink, you can run the TikTok Live Watcher."
    echo
fi

echo
echo "Checking for ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg not found!"
    echo
    echo "Please install ffmpeg:"
    echo "  {ffmpeg_install}"
    echo
    echo "After installing ffmpeg, you can use the app."
else
    echo "✅ ffmpeg found"
fi

echo
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo
echo "You can now run: ./TikTok-Live-Watcher"
echo
"""

    script_path = package_dir / "setup.sh"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(setup_script)

    # Make script executable
    os.chmod(script_path, 0o755)

def create_zip_release(package_dir):
    """Create a zip file for easy distribution"""
    zip_path = f"{package_dir}.zip"

    print(f"📦 Creating zip release: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                # Calculate the path relative to the package directory
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)

    print(f"✅ Created: {zip_path}")
    return zip_path

def main():
    """Main release build process"""
    print("🚀 TikTok Live Watcher Release Builder")
    print("=" * 50)

    # Clean previous builds
    clean_build_artifacts()

    # Create releases directory
    Path("releases").mkdir(exist_ok=True)

    # Detect current platform
    current_platform = platform.system()
    if current_platform == "Darwin":
        platform_name = "macOS"
    elif current_platform == "Windows":
        platform_name = "Windows"
    else:
        platform_name = "Linux"

    print(f"🖥️  Building for: {platform_name}")

    # Build executable
    if not build_executable():
        print("❌ Failed to build executable")
        return 1

    # Create user package
    package_dir = create_user_package(platform_name)
    if not package_dir:
        print("❌ Failed to create user package")
        return 1

    # Create zip release
    zip_path = create_zip_release(package_dir)

    print("\n🎉 RELEASE BUILD COMPLETE!")
    print("=" * 50)
    print(f"📁 Package folder: {package_dir}")
    print(f"📦 Zip release: {zip_path}")
    print("\n📋 For Users:")
    print("1. Download and extract the zip file")
    print("2. Run the setup script (setup.bat on Windows, setup.sh on macOS/Linux)")
    print("3. Run the executable")
    print("\n💡 Cross-platform note:")
    print("- This build only works on the current platform")
    print("- To create Windows releases, run this on Windows")
    print("- To create macOS releases, run this on macOS")

    return 0

if __name__ == "__main__":
    sys.exit(main())