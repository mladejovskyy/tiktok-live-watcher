# Manual Setup Guide for TikTok Live Watcher

If the automatic setup script fails, you can install dependencies manually.

## 📋 Required Dependencies

1. **streamlink** - For downloading TikTok streams
2. **ffmpeg** - For video processing

## 🛠️ Installation Methods

### Option 1: Homebrew (macOS - Recommended)
```bash
# Install streamlink and ffmpeg together
brew install streamlink

# Streamlink will automatically pull in ffmpeg as a dependency
```

### Option 2: pipx (Cross-platform)
```bash
# Install pipx first
pip install --user pipx
# or: brew install pipx

# Install streamlink via pipx
pipx install streamlink

# Install ffmpeg separately
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/
```

### Option 3: User Installation (Python pip)
```bash
# Install streamlink in user directory
pip install --user streamlink

# Add to PATH if needed
export PATH=$PATH:~/.local/bin

# Install ffmpeg separately (see Option 2)
```

### Option 4: System Installation (Advanced)
```bash
# Override externally-managed-environment (use carefully)
pip install --break-system-packages streamlink

# Install ffmpeg separately (see Option 2)
```

## 🧪 Testing Installation

After installation, test that everything works:

```bash
# Test streamlink
streamlink --version
# Should show: streamlink 7.x.x

# Test ffmpeg
ffmpeg -version
# Should show: ffmpeg version 8.x.x

# Test TikTok stream access
streamlink "https://www.tiktok.com/@someuser/live"
# Should show available streams or "No streams found"
```

## 🚀 Running the App

Once dependencies are installed:

```bash
# macOS/Linux
./TikTok-Live-Watcher

# Windows
TikTok-Live-Watcher.exe
```

## 🔧 Troubleshooting

### "Command not found: streamlink"
- **pipx**: Run `pipx ensurepath` and restart terminal
- **user install**: Add `~/.local/bin` to PATH
- **homebrew**: Run `brew link streamlink`

### "Command not found: ffmpeg"
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/ and add to PATH

### Recording not working
1. Verify both tools work: `streamlink --version` and `ffmpeg -version`
2. Test manual download: `streamlink "https://www.tiktok.com/@user/live" best`
3. Check app logs for specific error messages

### Python environment issues
If you get "externally-managed-environment" errors:
- Use homebrew: `brew install streamlink` (recommended)
- Use pipx: `pipx install streamlink`
- Create virtual environment: `python -m venv myenv && source myenv/bin/activate`

## 📱 Platform-Specific Notes

### macOS
- Homebrew is the easiest method
- May need to allow executable in Security settings

### Windows
- Use Windows Terminal or PowerShell
- May need to allow executable in Windows Defender
- Download ffmpeg from official site and add to PATH

### Linux
- Package managers usually have older versions
- pip/pipx recommended for latest streamlink
- Install ffmpeg via system package manager