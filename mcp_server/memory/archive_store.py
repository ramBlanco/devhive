import json
import os
from typing import Dict, Any

ARCHIVE_FILE = "feature_archive.json"

class ArchiveStore:
    def __init__(self, file_path: str = ARCHIVE_FILE):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def save(self, feature_id: str, data: Dict[str, Any]):
        """Saves a feature artifact to the archive store."""
        try:
            with open(self.file_path, 'r') as f:
                archive = json.load(f)
        except json.JSONDecodeError:
            archive = {}
            
        archive[feature_id] = data
        
        with open(self.file_path, 'w') as f:
            json.dump(archive, f, indent=2)

    def get(self, feature_id: str) -> Dict[str, Any]:
        """Retrieves a feature artifact from the archive store."""
        try:
            with open(self.file_path, 'r') as f:
                archive = json.load(f)
            return archive.get(feature_id, {})
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def list_all(self) -> Dict[str, Any]:
        """Lists all archived features."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
