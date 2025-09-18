import os
import sys
import subprocess
import glob
from datetime import datetime
from typing import Optional


class StreamRecorder:
    """Handles stream recording using streamlink and yt-dlp fallback."""

    def __init__(self):
        self.active_process: Optional[subprocess.Popen] = None

        # Get the directory where the executable is located
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as Python script
            app_dir = os.path.dirname(os.path.abspath(__file__))
            app_dir = os.path.dirname(app_dir)  # Go up one level from recorders/

        self.recordings_dir = os.path.join(app_dir, "Recordings")
        os.makedirs(self.recordings_dir, exist_ok=True)

    def _get_ffmpeg_path(self) -> str:
        """Get path to ffmpeg (bundled or system)."""
        # Check if running as PyInstaller bundle with bundled ffmpeg
        if getattr(sys, 'frozen', False):
            bundle_dir = os.path.dirname(sys.executable)
            bundled_ffmpeg = os.path.join(bundle_dir, "ffmpeg", "ffmpeg.exe")
            if os.path.exists(bundled_ffmpeg):
                return bundled_ffmpeg

        # Check system PATH
        try:
            import shutil
            system_ffmpeg = shutil.which("ffmpeg")
            if system_ffmpeg:
                return system_ffmpeg
        except:
            pass

        return None

    def check_dependencies(self) -> tuple[bool, bool, bool]:
        """Check if streamlink, yt-dlp, and ffmpeg are available."""
        streamlink_available = False
        ytdlp_available = False
        ffmpeg_available = False

        try:
            subprocess.run(['streamlink', '--version'],
                         capture_output=True, check=True)
            streamlink_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        try:
            subprocess.run(['yt-dlp', '--version'],
                         capture_output=True, check=True)
            ytdlp_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Check for ffmpeg (bundled or system)
        ffmpeg_cmd = self._get_ffmpeg_path()
        if ffmpeg_cmd:
            try:
                subprocess.run([ffmpeg_cmd, '-version'],
                             capture_output=True, check=True)
                ffmpeg_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        return streamlink_available, ytdlp_available, ffmpeg_available

    def start_recording(self, username: str, stream_url: str) -> bool:
        """Start recording stream to file using streamlink (preferred) or yt-dlp fallback."""
        if self.active_process:
            self.stop_recording()

        streamlink_available, ytdlp_available, ffmpeg_available = self.check_dependencies()

        if not stream_url:
            print(f"Error: No stream URL available for @{username}")
            return False

        # Try streamlink first (better for TikTok)
        if streamlink_available:
            return self._start_recording_streamlink(username, stream_url)
        elif ytdlp_available:
            print("📹 Streamlink not available, falling back to yt-dlp")
            return self._start_recording_ytdlp(username, stream_url)
        else:
            print("Error: Neither streamlink nor yt-dlp found. Install with: pip install streamlink yt-dlp")
            return False

    def _start_recording_streamlink(self, username: str, stream_url: str) -> bool:
        """Record using streamlink (preferred method)."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{username}_{timestamp}.mp4"
        filepath = os.path.join(self.recordings_dir, filename)

        try:
            cmd = [
                'streamlink',
                '--output', filepath,
                '--loglevel', 'error',
                '--retry-streams', '3',
                '--retry-max', '10',
                '--hls-live-restart',
                stream_url,
                'best'
            ]

            print(f"📹 Starting recording with streamlink: {filename}")
            print(f"🔗 URL: {stream_url}")
            print(f"💾 Output: {filepath}")

            self.active_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Check if streamlink starts successfully
            import time
            time.sleep(3)
            if self.active_process.poll() is not None:
                stdout, stderr = self.active_process.communicate()
                if "error:" in stderr.lower() or "no streams found" in stderr.lower():
                    print(f"❌ Streamlink failed: {stderr.strip()}")
                    self.active_process = None
                    return False

            print(f"✅ Streamlink recording started successfully!")
            return True

        except Exception as e:
            print(f"Error starting streamlink recording: {e}")
            return False

    def _start_recording_ytdlp(self, username: str, stream_url: str) -> bool:
        """Fallback to yt-dlp recording."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{username}_{timestamp}.%(ext)s"
        filepath = os.path.join(self.recordings_dir, filename)

        try:
            cmd = [
                'yt-dlp',
                '--format', 'best[ext=mp4]/best',
                '--output', filepath,
                '--no-playlist',
                '--ignore-errors',
                '--no-warnings',
                stream_url
            ]

            print(f"📹 Starting recording with yt-dlp: {username}_{timestamp}")
            print(f"🔗 URL: {stream_url}")

            self.active_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            return True

        except Exception as e:
            print(f"Error starting yt-dlp recording: {e}")
            return False

    def stop_recording(self) -> None:
        """Stop active recording."""
        if self.active_process:
            recorded_file = None
            try:
                if self.active_process.poll() is None:
                    self.active_process.terminate()
                    self.active_process.wait(timeout=5)
                    print("⏹️  Stopped recording")
                else:
                    stdout, stderr = self.active_process.communicate()
                    if stderr and "error" in stderr.lower():
                        print(f"Recording error: {stderr.strip()}")
                    print("⏹️  Recording finished")

                # Try to fix the recorded file if ffmpeg is available
                self._fix_recorded_files()

            except subprocess.TimeoutExpired:
                self.active_process.kill()
                print("🔴 Force stopped recording")
            except Exception as e:
                print(f"Error stopping recording: {e}")
            finally:
                self.active_process = None

    def get_recording_status(self) -> str:
        """Get detailed recording status for debugging."""
        if not self.active_process:
            return "No active recording"

        if self.active_process.poll() is None:
            return "Recording in progress"
        else:
            try:
                stdout, stderr = self.active_process.communicate(timeout=1)
                if stderr:
                    return f"Recording failed: {stderr.strip()}"
                return "Recording completed"
            except subprocess.TimeoutExpired:
                return "Recording status unknown"

    def is_recording(self) -> bool:
        """Check if currently recording."""
        if self.active_process:
            return self.active_process.poll() is None
        return False

    def _fix_recorded_files(self) -> None:
        """Fix metadata and seekability of recorded files using ffmpeg if available."""
        try:
            # Get ffmpeg path (bundled or system)
            ffmpeg_cmd = self._get_ffmpeg_path()
            if not ffmpeg_cmd:
                return

            # Test ffmpeg
            subprocess.run([ffmpeg_cmd, '-version'], capture_output=True, check=True)

            # Find the most recent .mp4 file in recordings directory
            mp4_files = glob.glob(os.path.join(self.recordings_dir, "*.mp4"))
            if not mp4_files:
                return

            # Get the most recently modified file
            latest_file = max(mp4_files, key=os.path.getmtime)

            # Create fixed filename
            base_name = os.path.splitext(latest_file)[0]
            fixed_file = f"{base_name}_fixed.mp4"

            print("🔧 Fixing video metadata for better playback...")

            # Use ffmpeg to fix the file
            cmd = [
                ffmpeg_cmd, '-i', latest_file,
                '-c', 'copy',  # Don't re-encode, just copy streams
                '-movflags', '+faststart',  # Move metadata to beginning
                '-avoid_negative_ts', 'make_zero',  # Fix timestamp issues
                fixed_file,
                '-y'  # Overwrite if exists
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Replace original file with fixed version
                os.replace(fixed_file, latest_file)
                print("✅ Video fixed - now supports seeking and shows duration")
            else:
                print("⚠️  Could not fix video metadata")
                if os.path.exists(fixed_file):
                    os.remove(fixed_file)

        except (subprocess.CalledProcessError, FileNotFoundError):
            # ffmpeg not available, skip fixing
            pass
        except Exception as e:
            print(f"Error fixing recorded file: {e}")

    def cleanup(self) -> None:
        """Clean up any active recordings."""
        self.stop_recording()