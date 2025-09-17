import json
import os


class SettingsManager:
    """Manages settings with local JSON persistence."""

    def __init__(self, filename: str = "settings.json"):
        self.filename = filename
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Load settings from JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"recording_enabled": False}
        except (json.JSONDecodeError, IOError, KeyError):
            return {"recording_enabled": False}

    def _save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            print("Error: Failed to save settings to file")

    def get_recording_enabled(self) -> bool:
        """Get recording enabled status."""
        return self.settings.get("recording_enabled", False)

    def toggle_recording(self) -> bool:
        """Toggle recording setting and return new value."""
        self.settings["recording_enabled"] = not self.settings.get("recording_enabled", False)
        self._save_settings()
        return self.settings["recording_enabled"]