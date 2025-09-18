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

def prepare_ffmpeg_for_bundle():
    """Download ffmpeg for bundling with the executable"""
    try:
        print("📥 Preparing ffmpeg for bundling...")

        # Create temp directory for ffmpeg
        ffmpeg_temp = Path("temp_ffmpeg")
        ffmpeg_temp.mkdir(exist_ok=True)

        # Try a smaller, more reliable ffmpeg download
        import urllib.request
        import urllib.error

        # Use a direct link to a smaller ffmpeg binary
        ffmpeg_urls = [
            "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        ]

        for ffmpeg_url in ffmpeg_urls:
            try:
                zip_path = ffmpeg_temp / "ffmpeg.zip"
                print(f"   Trying download from: {ffmpeg_url}")

                # Add headers to avoid blocking
                req = urllib.request.Request(ffmpeg_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

                with urllib.request.urlopen(req, timeout=60) as response:
                    with open(zip_path, 'wb') as f:
                        f.write(response.read())

                print("   Download successful, extracting...")

                # Extract
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(ffmpeg_temp)

                # Find ffmpeg.exe
                for item in ffmpeg_temp.rglob("ffmpeg.exe"):
                    print(f"   ✅ Found ffmpeg: {item}")
                    return str(item)

            except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
                print(f"   Failed: {e}")
                continue

        print("   ⚠️  All download attempts failed")
        return None

    except Exception as e:
        print(f"⚠️  Could not prepare ffmpeg: {e}")
        return None

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

    # Download and prepare ffmpeg
    ffmpeg_path = prepare_ffmpeg_for_bundle()

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

    # Add ffmpeg to bundle if available
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        if platform.system() == "Windows":
            cmd.extend(["--add-binary", f"{ffmpeg_path};."])
        else:
            cmd.extend(["--add-binary", f"{ffmpeg_path}:."])
        print(f"✅ Including ffmpeg in bundle: {ffmpeg_path}")
    else:
        print("❌ CRITICAL: ffmpeg not found - build will fail!")
        return False

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

REM Try different Python commands
set PYTHON_CMD=
echo Debug: Trying python command...
python --version >nul 2>&1
if !errorlevel!==0 (
    set PYTHON_CMD=python
    echo ✅ Python found: python
    goto :install_streamlink
)

echo Debug: Trying py command...
py --version >nul 2>&1
if !errorlevel!==0 (
    set PYTHON_CMD=py
    echo ✅ Python found: py
    goto :install_streamlink
)

echo Debug: Trying python3 command...
python3 --version >nul 2>&1
if !errorlevel!==0 (
    set PYTHON_CMD=python3
    echo ✅ Python found: python3
    goto :install_streamlink
)

echo ❌ Python not found!
echo.
echo Downloading and installing Python automatically...
echo Please wait, this may take a few minutes...
echo.

echo Debug: Attempting to download Python...
REM Try to download Python installer
powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe' -UserAgent 'Mozilla/5.0' } catch { Write-Host 'Download failed'; exit 1 }"
if exist "python-installer.exe" (
    echo Debug: Python installer downloaded, installing...
    python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    timeout /t 30 /nobreak >nul
    del python-installer.exe
    echo.
    echo Python installation complete. Checking again...

    REM Check again after installation
    echo Debug: Checking python after install...
    python --version >nul 2>&1
    if !errorlevel!==0 (
        set PYTHON_CMD=python
        echo ✅ Python now available
        goto :install_streamlink
    )

    echo Debug: Checking py after install...
    py --version >nul 2>&1
    if !errorlevel!==0 (
        set PYTHON_CMD=py
        echo ✅ Python now available
        goto :install_streamlink
    )
) else (
    echo Debug: Python installer download failed
)

echo ❌ Failed to install Python automatically
echo.
echo Please install Python manually from: https://python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo Then run this setup script again.
echo.
echo ❌ Setup Failed!
echo Press Enter to continue...
pause
exit /b 1

:install_streamlink
echo.
echo Installing streamlink...
echo Debug: Using Python command: !PYTHON_CMD!

echo Debug: Trying pip install streamlink...
!PYTHON_CMD! -m pip install streamlink
if !errorlevel!==0 (
    echo ✅ streamlink installed
    goto :check_ffmpeg
)

echo Debug: Method 1 failed, trying user install...
!PYTHON_CMD! -m pip install --user streamlink
if !errorlevel!==0 (
    echo ✅ streamlink installed (user directory)
    goto :check_ffmpeg
)

echo Debug: Method 2 failed, trying system override...
!PYTHON_CMD! -m pip install --break-system-packages streamlink
if !errorlevel!==0 (
    echo ✅ streamlink installed (system override)
    goto :check_ffmpeg
)

echo Debug: Method 3 failed, trying pipx...
pipx install streamlink
if !errorlevel!==0 (
    echo ✅ streamlink installed (via pipx)
    goto :check_ffmpeg
)

echo ❌ Automatic streamlink installation failed
echo.
echo Please install streamlink manually using one of these methods:
echo   Method 1 (pipx): pipx install streamlink
echo   Method 2 (user): pip install --user streamlink
echo   Method 3 (system): pip install --break-system-packages streamlink
echo   Method 4 (chocolatey): choco install streamlink
echo.
echo After installing streamlink, you can run TikTok-Live-Watcher.exe
echo.
echo ❌ Setup Failed!
echo Press Enter to continue...
pause
exit /b 1

:check_ffmpeg

echo.
echo Debug: Reached ffmpeg check section
echo Checking for ffmpeg...
echo Debug: Testing ffmpeg command...
ffmpeg -version >nul 2>&1
echo Debug: ffmpeg test result: !errorlevel!
if !errorlevel! neq 0 (
    echo ⚠️  ffmpeg not found!
    echo.
    echo Note: streamlink can work without ffmpeg for basic functionality
    echo Attempting to download and install ffmpeg automatically...
    echo Please wait, this may take a few minutes...
    echo.

    echo Debug: Creating temp directory...
    REM Create temporary directory for download
    set TEMP_DIR=!TEMP!\\ffmpeg_install
    echo Debug: Temp dir will be: !TEMP_DIR!
    if exist "!TEMP_DIR!" rmdir /s /q "!TEMP_DIR!"
    mkdir "!TEMP_DIR!"
    cd /d "!TEMP_DIR!"
    echo Debug: Changed to temp directory

    echo Downloading ffmpeg...
    echo Debug: Starting download...
    powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip' -UserAgent 'Mozilla/5.0'; Write-Host 'Download completed' } catch { Write-Host 'Download failed:' $_.Exception.Message }" 2>nul
    echo Debug: PowerShell download command finished

    if exist "ffmpeg.zip" (
        echo Download successful, extracting...
        powershell -Command "try { Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force } catch { exit 1 }"

        REM Create ffmpeg directory
        if not exist "C:\\ffmpeg" mkdir "C:\\ffmpeg"
        if not exist "C:\\ffmpeg\\bin" mkdir "C:\\ffmpeg\\bin"

        REM Find extracted folder and copy files
        for /d %%i in (ffmpeg-*) do (
            echo Copying ffmpeg files...
            copy "%%i\\bin\\ffmpeg.exe" "C:\\ffmpeg\\bin\\" >nul 2>&1
            copy "%%i\\bin\\ffprobe.exe" "C:\\ffmpeg\\bin\\" >nul 2>&1
            copy "%%i\\bin\\ffplay.exe" "C:\\ffmpeg\\bin\\" >nul 2>&1
        )

        REM Clean up temp files
        cd /d "%~dp0"
        rmdir /s /q "%TEMP_DIR%" >nul 2>&1

        REM Test if ffmpeg was copied successfully
        if exist "C:\\ffmpeg\\bin\\ffmpeg.exe" (
            echo ✅ ffmpeg files copied successfully

            REM Add to system PATH permanently
            echo Adding ffmpeg to PATH...
            for /f "tokens=2*" %%A in ('reg query "HKCU\\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%B"
            if not defined CURRENT_PATH set "CURRENT_PATH="
            echo %CURRENT_PATH% | find /i "C:\\ffmpeg\\bin" >nul
            if errorlevel 1 (
                reg add "HKCU\\Environment" /v PATH /d "%CURRENT_PATH%;C:\\ffmpeg\\bin" /f >nul 2>&1
                echo ✅ Added ffmpeg to PATH
            ) else (
                echo ✅ ffmpeg already in PATH
            )

            REM Test if ffmpeg works
            "C:\\ffmpeg\\bin\\ffmpeg.exe" -version >nul 2>&1
            if %errorlevel%==0 (
                echo ✅ ffmpeg is working correctly
            ) else (
                echo ⚠️  ffmpeg installed but may need to restart for PATH changes
            )
        ) else (
            echo ❌ Failed to copy ffmpeg files
            goto :ffmpeg_failed
        )
    ) else (
        echo ❌ Failed to download ffmpeg
        goto :ffmpeg_failed
    )

    goto :ffmpeg_done

    :ffmpeg_failed
    echo.
    echo ⚠️  ffmpeg installation failed, but streamlink is working!
    echo.
    echo Manual ffmpeg installation (optional):
    echo 1. Download from: https://ffmpeg.org/download.html#build-windows
    echo 2. Extract to C:\\ffmpeg\\
    echo 3. Add C:\\ffmpeg\\bin to your PATH
    echo.
    echo ✅ Setup completed successfully!
    echo streamlink is ready for recording (ffmpeg optional)
    echo.
    echo Press Enter to continue...
    pause
    exit /b 0

    :ffmpeg_done
) else (
    echo ✅ ffmpeg found
)

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo All dependencies installed successfully!
echo You can now run TikTok-Live-Watcher.exe
echo.
echo Press Enter to continue...
pause

REM This should never be reached, but just in case
echo.
echo Debug: Script reached end unexpectedly
echo Press Enter to close...
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