import json
from pathlib import Path

class ProjectStateManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.state_file = f"{project_name}/project_state.json"
        
        try:
            from mcp_server.utils.filesystem import get_safe_path, read_file
            try:
                # Attempt to read first
                self.read_state()
            except:
                # If fails, ensure path and init
                get_safe_path(f"{project_name}")
                self.initialize_project()
        except Exception:
            pass # Handle init error?

    def read_state(self):
        from mcp_server.utils.filesystem import read_file
        return json.loads(read_file(self.state_file))

    def write_state(self, state):
        from mcp_server.utils.filesystem import write_file
        write_file(self.state_file, json.dumps(state, indent=2))
        
    def get_state(self):
        return self.read_state()
        
    def update_state(self, state):
        self.write_state(state)
        
    def initialize_project(self):
        state = {
            "project": self.project_name,
            "stage": "initialization",
            "artifacts": {
                "exploration": None,
                "proposal": None,
                "architecture": None,
                "tasks": None,
                "implementation": None,
                "tests": None,
                "verification": None,
                "archive": None
            },
            "files_generated": [],
            "status": "active"
        }
        self.write_state(state)

    def update_artifact(self, step: str, artifact_id: str):
        state = self.get_state()
        state["artifacts"][step] = artifact_id
        self.update_state(state)
        
    def add_files(self, files: list):
        state = self.get_state()
        existing = set(state.get("files_generated", []))
        existing.update(files)
        state["files_generated"] = list(existing)
        self.update_state(state)
