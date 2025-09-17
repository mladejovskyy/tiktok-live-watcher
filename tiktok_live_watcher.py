#!/usr/bin/env python3
"""
How to run:
pip install TikTokLive
python tiktok_live_watcher.py
"""

import asyncio
import json
import os
import random
import subprocess
import time
from datetime import datetime
from typing import List, Optional

from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel


class UsernameManager:
    """Manages usernames with local JSON persistence."""

    def __init__(self, filename: str = "usernames.json"):
        self.filename = filename
        self.usernames = self._load_usernames()

    def _load_usernames(self) -> List[str]:
        """Load usernames from JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('usernames', [])
            return []
        except (json.JSONDecodeError, IOError, KeyError):
            return []

    def _save_usernames(self) -> None:
        """Save usernames to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({'usernames': self.usernames}, f, indent=2)
        except IOError:
            print("Error: Failed to save usernames to file")

    def add_username(self, username: str) -> bool:
        """Add username (validated, trimmed, lowercase, deduplicated)."""
        username = username.strip().lower()
        if not username:
            return False
        if username in self.usernames:
            return False

        self.usernames.append(username)
        self._save_usernames()
        return True

    def remove_username(self, username: str) -> bool:
        """Remove username if it exists."""
        username = username.strip().lower()
        if username in self.usernames:
            self.usernames.remove(username)
            self._save_usernames()
            return True
        return False

    def get_usernames(self) -> List[str]:
        """Get copy of usernames list."""
        return self.usernames.copy()


class TikTokLiveChecker:
    """Checks TikTok live status using TikTokLive library."""

    def __init__(self):
        # Disable logging for cleaner output
        import logging
        logging.getLogger('TikTokLive').setLevel(logging.CRITICAL)

    async def is_user_live(self, username: str) -> Optional[bool]:
        """
        Check if user is live with retry logic.
        Returns True if live, False if offline, None if unknown.
        """
        for attempt in range(3):
            try:
                # Create client for this username
                client = TikTokLiveClient(unique_id=f"@{username}")
                client.logger.setLevel(LogLevel.CRITICAL.value)

                # Check live status
                is_live = await client.is_live()
                return is_live

            except Exception:
                if attempt < 2:  # Only wait if not the last attempt
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)

        return None  # Unknown status after all retries


def display_menu(username_manager: UsernameManager) -> None:
    """Display the main menu."""
    print("\nTikTok Live Watcher")
    print("=" * 20)
    print("1) Add a new username")
    print("2) Remove existing username")
    print("3) Show available usernames")
    print("\n0) Exit")


def get_user_choice(max_choice: int) -> int:
    """Get validated user input."""
    while True:
        try:
            choice = int(input(f"\nEnter choice (0-{max_choice}): "))
            if 0 <= choice <= max_choice:
                return choice
            print(f"Please enter a number between 0 and {max_choice}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0


def add_username_flow(username_manager: UsernameManager) -> None:
    """Handle adding a new username."""
    while True:
        try:
            print("\nAdd Username")
            print("-" * 12)
            print("1) Return to main menu")
            username = input("Enter TikTok username (without @): ").strip()

            if username == "1":
                return

            if not username:
                print("Error: Username cannot be empty")
                continue

            if username_manager.add_username(username):
                print(f"Added username: {username}")
                return
            else:
                print(f"Username '{username}' already exists or is invalid")
        except KeyboardInterrupt:
            print("\nCancelled")
            return


def remove_username_flow(username_manager: UsernameManager) -> None:
    """Handle removing an existing username."""
    while True:
        usernames = username_manager.get_usernames()
        if not usernames:
            print("No usernames to remove")
            return

        print("\nRemove Username")
        print("-" * 15)
        print("1) Return to main menu")
        for i, username in enumerate(usernames, 2):
            print(f"{i}) {username}")

        try:
            choice = int(input(f"\nEnter choice (1-{len(usernames) + 1}): "))
            if choice == 1:
                return
            elif 2 <= choice <= len(usernames) + 1:
                username = usernames[choice - 2]
                if username_manager.remove_username(username):
                    print(f"Removed username: {username}")
                    return
            else:
                print("Invalid choice")
        except (ValueError, KeyboardInterrupt):
            print("Cancelled")
            return


async def monitor_user(username: str, checker: TikTokLiveChecker, interval: int = 60) -> None:
    """Monitor user live status every 60 seconds."""
    print(f"\nMonitoring @{username} (Press Ctrl+C to stop)")

    try:
        while True:
            current_status = await checker.is_user_live(username)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


def select_username_flow(username_manager: UsernameManager) -> Optional[str]:
    """Handle username selection submenu."""
    while True:
        usernames = username_manager.get_usernames()
        if not usernames:
            print("No usernames available. Add some usernames first.")
            return None

        print("\nSelect Username to Monitor")
        print("-" * 25)
        print("1) Return to main menu")
        for i, username in enumerate(usernames, 2):
            if i > 9:  # Limit to options 2-9
                break
            print(f"{i}) {username}")

        try:
            max_choice = min(len(usernames) + 1, 9)
            choice = int(input(f"\nEnter choice (1-{max_choice}): "))

            if choice == 1:
                return None
            elif 2 <= choice <= max_choice:
                return usernames[choice - 2]
            else:
                print("Invalid choice")
        except (ValueError, KeyboardInterrupt):
            print("Cancelled")
            return None


async def main() -> None:
    """Main application loop."""
    username_manager = UsernameManager()
    checker = TikTokLiveChecker()

    try:
        while True:
            display_menu(username_manager)
            choice = get_user_choice(3)

            if choice == 0:
                print("Goodbye!")
                break
            elif choice == 1:
                add_username_flow(username_manager)
            elif choice == 2:
                remove_username_flow(username_manager)
            elif choice == 3:
                selected_username = select_username_flow(username_manager)
                if selected_username:
                    await monitor_user(selected_username, checker)

    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    asyncio.run(main())