import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from devhive.utils.filesystem import write_file, read_file, get_safe_path
import logging

class ArtifactManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.artifacts_dir = f"./.devhive/artifacts"
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
        Also generates a summary artifact and an OpenSpec markdown file.
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
        
        # Generate OpenSpec markdown for human readability and tf-idf memory
        md_content = self._generate_markdown_artifact(step_name, content)
        md_path = f"{self.artifacts_dir}/{artifact_id}.md"
        write_file(md_path, md_content)
        
        return artifact_id

    def _generate_markdown_artifact(self, step_name: str, content: Dict[str, Any]) -> str:
        """
        Converts the JSON envelope into a readable Markdown artifact.
        """
        md = [f"# {step_name.capitalize()} Phase\n"]
        
        # Envelope fields
        if "status" in content:
            md.append(f"**Status**: {content.get('status')}")
        if "executive_summary" in content:
            md.append(f"**Summary**: {content.get('executive_summary')}")
        
        risks = content.get("risks", [])
        if isinstance(risks, list) and risks:
            md.append(f"**Risks**: {', '.join(risks)}")
        elif risks:
            md.append(f"**Risks**: {risks}")
             
        artifacts = content.get("artifacts_produced", [])
        if isinstance(artifacts, list) and artifacts:
            md.append(f"**Artifacts**: {', '.join(artifacts)}")
        elif artifacts:
            md.append(f"**Artifacts**: {artifacts}")
            
        md.append("\n## Phase Data\n")
        
        phase_data = content.get("phase_data", content) # Fallback if envelope is missing
        
        for k, v in phase_data.items():
            if k in ["status", "executive_summary", "risks", "artifacts_produced"] and "phase_data" not in content:
                continue # Skip envelope keys if they are at the top level
                
            k_title = k.replace('_', ' ').capitalize()
            md.append(f"### {k_title}")
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    # List of objects
                    for item in v:
                        md.append(f"- **{item.get('name', item.get('path', 'Item'))}**: {item.get('description', '')}")
                        if 'content' in item:
                            md.append(f"  ```\n  {str(item['content'])[:100]}...\n  ```")
                else:
                    # Simple list
                    for item in v:
                        md.append(f"- {item}")
            elif isinstance(v, str):
                if '\n' in v or len(v) > 80:
                    md.append(f"\n{v}\n")
                else:
                    md.append(v)
            elif isinstance(v, dict):
                md.append(json.dumps(v, indent=2))
            else:
                md.append(str(v))
            md.append("\n")
            
        return "\n".join(md)

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
