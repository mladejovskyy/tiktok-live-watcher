# Distribution Guide for TikTok Live Watcher

## 🎯 Creating Releases for Non-Technical Users

### Building Executables

Use the automated release builder to create user-friendly packages:

```bash
python3 build_releases.py
```

This creates:
- **Standalone executable** - No Python installation required
- **Setup scripts** - Automatic dependency installation
- **User documentation** - Clear instructions
- **Zip package** - Easy to share

### 📁 What Gets Created

```
releases/
└── TikTok-Live-Watcher-[Platform].zip
    ├── TikTok-Live-Watcher[.exe]    # The main executable
    ├── setup.sh/.bat                 # Dependency installer
    └── README.txt                    # User instructions
```

## 🖥️ Platform-Specific Builds

### macOS
- **Run on**: macOS machine
- **Creates**: `TikTok-Live-Watcher-macOS.zip`
- **Users get**: Executable + setup.sh script

### Windows
- **Run on**: Windows machine
- **Creates**: `TikTok-Live-Watcher-Windows.zip`
- **Users get**: .exe file + setup.bat script

### Linux
- **Run on**: Linux machine
- **Creates**: `TikTok-Live-Watcher-Linux.zip`
- **Users get**: Executable + setup.sh script

## 👥 User Experience

### Step 1: Download & Extract
Users download the zip file and extract it.

### Step 2: Run Setup (One-time)
- **Windows**: Double-click `setup.bat`
- **macOS/Linux**: Run `./setup.sh` in Terminal

### Step 3: Run App
- **Windows**: Double-click `TikTok-Live-Watcher.exe`
- **macOS/Linux**: Double-click `TikTok-Live-Watcher`

## 🔧 What the Setup Script Does

1. **Checks Python** - Verifies Python is installed
2. **Installs streamlink** - `pip install streamlink`
3. **Checks ffmpeg** - Guides user to install if missing

## 📊 File Sizes

- **Executable**: ~13MB (includes all Python dependencies)
- **Zip package**: ~13MB compressed
- **Total download**: One 13MB file per platform

## 🎯 Dependencies Handled

### ✅ Bundled in Executable
- Python runtime
- TikTokLive library
- All Python packages
- Application code

### ⚙️ User Must Install (via setup script)
- **streamlink** - For TikTok stream access
- **ffmpeg** - For video processing

## 🚀 Publishing Releases

### GitHub Releases
1. Create releases on different platforms
2. Upload the zip files to GitHub Releases
3. Users download platform-specific zip

### Distribution Checklist
- [ ] Test executable on clean machine
- [ ] Verify setup script works
- [ ] Test recording functionality
- [ ] Create release notes

## 🛡️ Security Notes

- Executables are not code-signed
- Users may see security warnings
- Recommend downloading only from official sources

## 📝 Release Notes Template

```markdown
## TikTok Live Watcher v1.0.0

### Downloads
- [Windows](link-to-windows-zip)
- [macOS](link-to-macos-zip)
- [Linux](link-to-linux-zip)

### Installation
1. Download the zip file for your platform
2. Extract the zip file
3. Run the setup script (setup.bat on Windows, setup.sh on macOS/Linux)
4. Run the TikTok Live Watcher executable

### Features
- Monitor TikTok users for live streams
- Automatic recording with streamlink
- Clean CLI interface
- Cross-platform support

### Requirements
- Setup script handles most dependencies
- ffmpeg installation may require manual steps
```

## 🔄 Updating the App

To release updates:
1. Update version in code
2. Run `python3 build_releases.py` on each platform
3. Upload new zip files
4. Update documentation