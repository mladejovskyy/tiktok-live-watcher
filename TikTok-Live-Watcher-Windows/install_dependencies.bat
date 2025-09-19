@echo off
echo Installing TikTok Live Watcher dependencies...

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip not found. Please install Python first.
    echo Download Python from: https://python.org/
    pause
    exit /b 1
)

REM Install streamlink
echo Installing streamlink...
pip install streamlink

REM Check for ffmpeg in current directory first
if exist "ffmpeg.exe" (
    echo ffmpeg is already installed locally
    goto :complete
)

REM Check for ffmpeg in PATH
ffmpeg -version >nul 2>&1
if not errorlevel 1 (
    echo ffmpeg is already installed in PATH
    goto :complete
)

echo ffmpeg not found, downloading and installing...

REM Download ffmpeg using curl (more reliable than PowerShell)
echo Downloading ffmpeg... please wait
curl -L -o ffmpeg.zip "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

if not exist "ffmpeg.zip" (
    echo Failed to download ffmpeg. Please check your internet connection.
    echo You can manually download ffmpeg from https://ffmpeg.org/
    goto :complete
)

REM Extract using PowerShell
echo Extracting ffmpeg...
powershell -command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'temp_ffmpeg' -Force"

REM Copy ffmpeg.exe from the extracted folder
for /d %%i in (temp_ffmpeg\ffmpeg-*) do (
    if exist "%%i\bin\ffmpeg.exe" (
        copy "%%i\bin\ffmpeg.exe" "ffmpeg.exe"
        echo ffmpeg installed successfully!
    )
)

REM Clean up
if exist "ffmpeg.zip" del "ffmpeg.zip"
if exist "temp_ffmpeg" rmdir /s /q "temp_ffmpeg"

:complete
echo.
echo Setup complete!
echo You can now run TikTok-Live-Watcher.exe
pause