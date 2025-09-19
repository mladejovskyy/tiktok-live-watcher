#!/usr/bin/env python3
"""
Build script for TikTok Live Watcher executable
Creates a complete distribution with all dependencies
"""

import os
import shutil
import subprocess
import sys
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running: {cmd}")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return False

def download_ffmpeg_binary():
    """Download platform-specific ffmpeg binary"""
    system = platform.system().lower()
    arch = platform.machine().lower()

    print(f"Detected platform: {system} {arch}")

    # Create binaries directory
    bin_dir = Path("dist/binaries")
    bin_dir.mkdir(parents=True, exist_ok=True)

    if system == "darwin":  # macOS
        print("Downloading ffmpeg for macOS...")
        # You would download from https://ffmpeg.org/download.html#build-mac
        print("Please manually download ffmpeg for macOS and place in dist/binaries/")
        print("   Download from: https://evermeet.cx/ffmpeg/")
        return False

    elif system == "windows":
        print("Downloading ffmpeg for Windows...")
        # You would download from https://ffmpeg.org/download.html#build-windows
        print("Please manually download ffmpeg for Windows and place in dist/binaries/")
        return False

    elif system == "linux":
        print("Downloading ffmpeg for Linux...")
        # You would download static build
        print("Please manually download ffmpeg for Linux and place in dist/binaries/")
        return False

    return False

def create_spec_file():
    """Create a custom PyInstaller spec file"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'managers.username_manager',
        'managers.settings_manager',
        'checkers.tiktok_checker',
        'recorders.stream_recorder',
        'ui.menu',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TikTok-Live-Watcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    with open("TikTok-Live-Watcher.spec", "w") as f:
        f.write(spec_content.strip())

    print("Created custom spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")

    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Build with custom spec
    if not run_command("pyinstaller TikTok-Live-Watcher.spec"):
        return False

    print("Executable built successfully")
    return True

def create_distribution_package():
    """Create a complete distribution package"""
    print("Creating distribution package...")

    # Create distribution directory
    dist_name = f"TikTok-Live-Watcher-{platform.system()}-{platform.machine()}"
    dist_dir = Path(f"dist/{dist_name}")
    dist_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable
    exe_name = "TikTok-Live-Watcher"
    if platform.system() == "Windows":
        exe_name += ".exe"

    src_exe = Path(f"dist/{exe_name}")
    if src_exe.exists():
        shutil.copy2(src_exe, dist_dir / exe_name)

    # Create README for distribution
    readme_content = f"""# TikTok Live Watcher - Portable Distribution

## Quick Start

1. **Install ffmpeg** (required for recording):
   - macOS: `brew install ffmpeg`
   - Windows: Download from https://ffmpeg.org/
   - Linux: `sudo apt install ffmpeg`

2. **Install streamlink** (required for recording):
   ```bash
   pip install streamlink
   ```

3. **Run the application**:
   - Double-click `{exe_name}` or run from terminal

## Notes

- This is a portable executable that includes all Python dependencies
- External tools (ffmpeg, streamlink) must be installed separately
- Recordings are saved in a 'Recordings' folder next to the executable
- Settings and usernames are saved as JSON files next to the executable

## Troubleshooting

If recording doesn't work:
1. Verify ffmpeg is installed: `ffmpeg -version`
2. Verify streamlink is installed: `streamlink --version`
3. Make sure both are in your system PATH

## Support

For issues, visit: https://github.com/mladejovskyy/tiktok-live-watcher
"""

    with open(dist_dir / "README.txt", "w") as f:
        f.write(readme_content)

    # Create install script for dependencies
    install_script = """#!/bin/bash
# Install dependencies for TikTok Live Watcher

echo "Installing TikTok Live Watcher dependencies..."

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "Error: pip not found. Please install Python first."
    exit 1
fi

# Install streamlink
echo "Installing streamlink..."
pip install streamlink

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: ffmpeg not found!"
    echo "Please install ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Linux: sudo apt install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
else
    echo "ffmpeg is already installed"
fi

echo "Setup complete!"
echo "You can now run the TikTok Live Watcher executable."
"""

    with open(dist_dir / "install_dependencies.sh", "w") as f:
        f.write(install_script)

    # Make install script executable
    os.chmod(dist_dir / "install_dependencies.sh", 0o755)

    # Create Windows batch file
    install_bat = """@echo off
echo Installing TikTok Live Watcher dependencies...

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip not found. Please install Python first.
    pause
    exit /b 1
)

REM Install streamlink
echo Installing streamlink...
pip install streamlink

REM Check for ffmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: ffmpeg not found!
    echo Please install ffmpeg from https://ffmpeg.org/
) else (
    echo ffmpeg is already installed
)

echo Setup complete!
echo You can now run the TikTok Live Watcher executable.
pause
"""

    with open(dist_dir / "install_dependencies.bat", "w") as f:
        f.write(install_bat)

    print(f"Distribution package created: {dist_dir}")
    return str(dist_dir)

def main():
    """Main build process"""
    print("Building TikTok Live Watcher Executable")
    print("=" * 50)

    # Check if we're in virtual environment
    if not os.path.exists("venv"):
        print("Virtual environment not found!")
        print("Please run from the project directory with venv/ present")
        return 1

    # Activate virtual environment and install pyinstaller
    print("Installing PyInstaller...")
    # PyInstaller is already installed via requirements.txt
    print("PyInstaller already installed")

    # Create spec file
    create_spec_file()

    # Build executable
    # Use Windows-compatible activation
    activation_cmd = "venv\\Scripts\\activate.bat && pyinstaller TikTok-Live-Watcher.spec"
    if platform.system() == "Windows":
        activation_cmd = "venv\\Scripts\\activate.bat && pyinstaller TikTok-Live-Watcher.spec"
    else:
        activation_cmd = "source venv/bin/activate && pyinstaller TikTok-Live-Watcher.spec"

    if not run_command(activation_cmd):
        print("Failed to build executable")
        return 1

    # Create distribution package
    dist_path = create_distribution_package()

    print("\nBUILD COMPLETE!")
    print(f"Distribution package: {dist_path}")
    print("\nNext Steps:")
    print("1. Share the entire distribution folder with users")
    print("2. Users should run install_dependencies script first")
    print("3. Then they can run the executable")

    return 0

if __name__ == "__main__":
    sys.exit(main())