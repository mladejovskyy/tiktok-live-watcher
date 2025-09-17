# TikTok Live Watcher

A Python CLI tool that monitors TikTok users for live streams and automatically records them. Features real-time monitoring, automatic recording with streamlink/yt-dlp, and persistent username/settings management.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
brew install ffmpeg  # macOS (or apt install ffmpeg on Linux)

# Run the app
python main.py
```

## 📋 Requirements

- **Python 3.8+**
- **streamlink** (preferred - bypasses TikTok restrictions)
- **yt-dlp** (fallback stream extraction)
- **ffmpeg** (system dependency for video processing)

### 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/mladejovskyy/tiktok-live-watcher.git
cd tiktok-live-watcher

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Install system dependencies
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

## ✨ Features

- 🔴 **Real-time monitoring** - Checks live status every 60 seconds with colored output
- 📹 **Automatic recording** - Records streams when users go live (toggle on/off)
- 👥 **Username management** - Add/remove TikTok usernames with persistent storage
- 🎨 **Clean CLI interface** - Intuitive menus with colored status messages
- 🔄 **Robust error handling** - Retry logic and graceful error recovery
- 📁 **Organized storage** - Auto-creates timestamped recordings

## 📂 Project Structure

```
tiktok-live-watcher/
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── managers/
│   ├── username_manager.py      # Username persistence
│   └── settings_manager.py      # Settings persistence
├── checkers/
│   └── tiktok_checker.py        # Live status checking
├── recorders/
│   └── stream_recorder.py       # Stream recording with streamlink
├── ui/
│   └── menu.py                  # CLI interface
├── Recordings/                  # Auto-recorded streams
├── usernames.json               # Saved usernames (auto-created)
└── settings.json                # Recording preferences (auto-created)
```

## 🎮 Usage

### Main Menu
1. **Add username** - Add TikTok usernames to monitor (without @)
2. **Remove username** - Remove existing usernames from list
3. **Show usernames** - Select username to start monitoring
4. **Toggle recording** - Enable/disable automatic recording (True/False)
0. **Exit** - Quit application

### 📹 Recording
- When **recording is enabled** and a user goes live, recording starts automatically
- Files saved as: `Recordings/USERNAME_YYYY-MM-DD_HH-MM-SS.mp4`
- Recording stops when user goes offline
- Uses **streamlink** (preferred) with **yt-dlp** fallback

### 🎯 Monitoring Output
```bash
🔴 [2025-09-17 21:33:15] @username is LIVE     # Green text
⚫ [2025-09-17 21:34:15] @username is OFFLINE  # Red text
❓ [2025-09-17 21:35:15] @username status UNKNOWN (network error)
```

## 🔧 Troubleshooting

### Recording Issues
- **Streamlink not found**: `pip install streamlink`
- **FFmpeg not found**: Install via system package manager
- **TikTok restrictions**: App uses streamlink to bypass most restrictions
- **No streams found**: User might not be actually live or have restrictions

### Common Commands
```bash
# Check if streamlink works
streamlink "https://www.tiktok.com/@username/live"

# Test dependencies
streamlink --version
yt-dlp --version
ffmpeg -version
```

## 🛡️ Privacy & Security

- All usernames and settings stored locally
- No data sent to external services
- Recordings saved locally in `Recordings/` folder
- Personal data excluded from git via `.gitignore`

## 📝 Notes

- Monitors every 60 seconds to avoid rate limiting
- Only shows status changes + initial detection
- Graceful handling of network errors and interruptions
- Cross-platform compatible (Windows/macOS/Linux)