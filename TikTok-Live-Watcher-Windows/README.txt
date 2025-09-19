# TikTok Live Watcher - Windows Distribution

## Quick Start

1. **Install dependencies** (required for recording):
   - Install Python 3.11+ from https://python.org
   - Open Command Prompt and run: `pip install streamlink`
   - Download ffmpeg from https://ffmpeg.org/ and add to PATH

2. **Run the application**:
   - Double-click `TikTok-Live-Watcher.exe` or run from command prompt

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