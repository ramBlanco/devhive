import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from mcp_server.utils.filesystem import write_file, read_file, get_safe_path
import logging

class ArtifactManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.artifacts_dir = f"./{project_name}/artifacts"
        # Ensure dir exists (via filesystem util)
        try:
            get_safe_path(self.artifacts_dir).mkdir(parents=True, exist_ok=True)
            logging.info(f"Saving artifact {self.artifacts_dir}")
        except:
            logging.error(f"Artifact failed {self.artifacts_dir}")
            pass # Might already exist

    def save_artifact(self, step_name: str, content: Dict[str, Any], artifact_id: Optional[str] = None) -> str:
        """
        Saves an artifact and returns its ID.
        Also generates a summary artifact.
        """
        if not artifact_id:
            import time
            timestamp = int(time.time())
            artifact_id = f"{step_name}_{timestamp}"
        
        file_path = f"{self.artifacts_dir}/{artifact_id}.json"
        write_file(file_path, json.dumps(content, indent=2))
        
        # Generate and save summary
        summary = self._summarize_artifact(content)
        summary_path = f"{self.artifacts_dir}/{artifact_id}_summary.json"
        write_file(summary_path, json.dumps(summary, indent=2))
        
        return artifact_id

    def load_artifact(self, artifact_id: str) -> Dict[str, Any]:
        """Loads a full artifact."""
        file_path = f"{self.artifacts_dir}/{artifact_id}.json"
        try:
            content = read_file(file_path)
            return json.loads(content)
        except Exception:
            return {}

    def load_summary(self, artifact_id: str) -> Dict[str, Any]:
        """Loads an artifact summary."""
        file_path = f"{self.artifacts_dir}/{artifact_id}_summary.json"
        try:
            content = read_file(file_path)
            return json.loads(content)
        except Exception:
            # Fallback to full artifact if summary missing
            return self.load_artifact(artifact_id)

    def _summarize_artifact(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a lightweight summary of the artifact.
        Truncates long strings and limits list items.
        """
        summary = {}
        for k, v in content.items():
            if isinstance(v, str):
                if len(v) > 200:
                    summary[k] = v[:200] + "... (truncated)"
                else:
                    summary[k] = v
            elif isinstance(v, list):
                summary[k] = f"List with {len(v)} items"
                if len(v) > 0 and isinstance(v[0], str):
                    summary[k] += f" (e.g., {v[0][:50]}...)"
            elif isinstance(v, dict):
                summary[k] = f"Dict with {len(v)} keys"
            else:
                summary[k] = v
        return summary
