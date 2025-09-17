#!/usr/bin/env python3
"""
TikTok Live Watcher with Recording Support

How to run:
pip install TikTokLive
python main.py
"""

import asyncio
import signal
import sys
from datetime import datetime

from managers.username_manager import UsernameManager
from managers.settings_manager import SettingsManager
from checkers.tiktok_checker import TikTokLiveChecker
from recorders.stream_recorder import StreamRecorder
from ui.menu import (
    display_menu, get_user_choice, add_username_flow,
    remove_username_flow, select_username_flow, toggle_recording_flow, check_dependencies_flow
)


class TikTokLiveWatcher:
    """Main application class."""

    def __init__(self):
        self.username_manager = UsernameManager()
        self.settings_manager = SettingsManager()
        self.checker = TikTokLiveChecker()
        self.recorder = StreamRecorder()
        self.last_status = None
        self.recording_disabled_shown = False

    async def monitor_user(self, username: str, interval: int = 60) -> None:
        """Monitor user live status with recording support."""
        print(f"\nMonitoring @{username} (Press Ctrl+C to stop)")

        self.last_status = None
        self.recording_disabled_shown = False

        try:
            while True:
                current_status = await self.checker.is_user_live(username)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Handle status changes and recording
                await self._handle_status_change(username, current_status, timestamp)

                # Log status every check
                if current_status is True:
                    print(f"\033[32m🔴 [{timestamp}] @{username} is LIVE\033[0m")
                elif current_status is False:
                    print(f"\033[31m⚫ [{timestamp}] @{username} is OFFLINE\033[0m")
                else:
                    print(f"❓ [{timestamp}] @{username} status UNKNOWN (network error)")

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print(f"\nStopped monitoring @{username}")
            self.recorder.stop_recording()

    async def _handle_status_change(self, username: str, current_status, timestamp: str) -> None:
        """Handle status changes and recording logic."""
        recording_enabled = self.settings_manager.get_recording_enabled()

        # First time detection or status change from OFFLINE to LIVE
        if (self.last_status is None and current_status is True) or (self.last_status is False and current_status is True):
            if self.last_status is None:
                print(f"🔄 Initial detection: @{username} is LIVE")
            else:
                print(f"🔄 Status change: @{username} went LIVE")

            if recording_enabled and not self.recorder.is_recording():
                print(f"📹 Recording enabled - attempting to start recording...")
                stream_url = await self.checker.get_stream_url(username)
                if stream_url:
                    success = self.recorder.start_recording(username, stream_url)
                    if not success:
                        print(f"❌ Failed to start recording for @{username}")
                else:
                    print(f"⚠️  Could not get stream URL for recording @{username}")
            else:
                if not recording_enabled and not self.recording_disabled_shown:
                    print("📹 Recording disabled (toggle in menu: 4)")
                    self.recording_disabled_shown = True

        # Status change from LIVE to OFFLINE
        elif self.last_status is True and current_status is False:
            print(f"🔄 Status change: @{username} went OFFLINE")
            if self.recorder.is_recording():
                print("⏹️  Stopping recording...")
                self.recorder.stop_recording()

        self.last_status = current_status

    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for clean exit."""
        def signal_handler(signum, frame):
            print("\nReceived interrupt signal. Cleaning up...")
            self.recorder.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def run(self) -> None:
        """Main application loop."""
        self.setup_signal_handlers()

        try:
            while True:
                display_menu(self.username_manager, self.settings_manager)
                choice = get_user_choice(5)

                if choice == 0:
                    print("Goodbye!")
                    break
                elif choice == 1:
                    add_username_flow(self.username_manager)
                elif choice == 2:
                    remove_username_flow(self.username_manager)
                elif choice == 3:
                    selected_username = select_username_flow(self.username_manager)
                    if selected_username:
                        await self.monitor_user(selected_username)
                elif choice == 4:
                    toggle_recording_flow(self.settings_manager)
                elif choice == 5:
                    check_dependencies_flow()

        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            self.recorder.cleanup()


async def main() -> None:
    """Entry point."""
    app = TikTokLiveWatcher()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())