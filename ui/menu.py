from typing import Optional

from managers.username_manager import UsernameManager
from managers.settings_manager import SettingsManager
from recorders.stream_recorder import StreamRecorder


def display_menu(username_manager: UsernameManager, settings_manager: SettingsManager) -> None:
    """Display the main menu."""
    print("\nTikTok Live Watcher")
    print("=" * 20)
    print("1) Add a new username")
    print("2) Remove existing username")
    print("3) Show available usernames")

    # Display recording status with color
    recording_enabled = settings_manager.get_recording_enabled()
    if recording_enabled:
        status_text = "\033[32m\033[1mTrue\033[0m"  # Green bold
    else:
        status_text = "\033[31m\033[1mFalse\033[0m"  # Red bold

    print(f"4) Record stream – {status_text}")
    print("5) Check dependencies")
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


def toggle_recording_flow(settings_manager: SettingsManager) -> None:
    """Handle recording toggle."""
    new_value = settings_manager.toggle_recording()
    status = "enabled" if new_value else "disabled"
    print(f"Recording {status}")


def check_dependencies_flow() -> None:
    """Check and display dependency status."""
    print("\n🔍 Checking Dependencies")
    print("=" * 25)

    recorder = StreamRecorder()
    streamlink_available, ytdlp_available, ffmpeg_available = recorder.check_dependencies()

    # Check streamlink
    if streamlink_available:
        print("✅ streamlink: Available")
    else:
        print("❌ streamlink: Not found")
        print("   Install with: pip install streamlink")

    # Check yt-dlp
    if ytdlp_available:
        print("✅ yt-dlp: Available")
    else:
        print("⚠️  yt-dlp: Not found (optional fallback)")
        print("   Install with: pip install yt-dlp")

    # Check ffmpeg
    if ffmpeg_available:
        print("✅ ffmpeg: Available")
    else:
        print("❌ ffmpeg: Not found")
        print("   Download from: https://ffmpeg.org/")

    print()
    if streamlink_available and ffmpeg_available:
        print("🎉 All dependencies are installed!")
        print("   Recording works + automatic video fixing")
    elif streamlink_available and not ffmpeg_available:
        print("✅ Recording will work!")
        print("   But videos may have seeking/duration issues")
        print("   Install ffmpeg for automatic video fixing")
    elif not streamlink_available:
        print("⚠️  Recording will NOT work - streamlink is missing")
        print("   Run setup.bat again or install manually")

    input("\nPress Enter to continue...")