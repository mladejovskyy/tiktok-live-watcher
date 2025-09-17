import json
import os
from typing import List


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