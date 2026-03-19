import os
from pathlib import Path
from typing import Optional

# Use a local workspace directory for safety and portability
WORKSPACE_ROOT = Path("workspace/projects").resolve()

def ensure_workspace():
    """Ensures the workspace directory exists."""
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

def get_safe_path(path: str) -> Path:
    """Resolves a path relative to the workspace root and ensures safety."""
    ensure_workspace()
    
    # Clean the path to remove leading slashes or .
    clean_path = path.lstrip("/").lstrip("\\")
    full_path = (WORKSPACE_ROOT / clean_path).resolve()
    
    # Security check to prevent directory traversal
    try:
        full_path.relative_to(WORKSPACE_ROOT)
    except ValueError:
        raise ValueError(f"Access denied: Path '{path}' is outside the workspace root '{WORKSPACE_ROOT}'.")
        
    return full_path

def create_directory(path: str) -> str:
    """Creates a directory and its parents."""
    full_path = get_safe_path(path)
    full_path.mkdir(parents=True, exist_ok=True)
    return str(full_path)

def write_file(path: str, content: str) -> str:
    """Writes content to a file, overwriting if exists."""
    full_path = get_safe_path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return str(full_path)

def append_file(path: str, content: str) -> str:
    """Appends content to a file."""
    full_path = get_safe_path(path)
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(content)
    return str(full_path)

def read_file(path: str) -> str:
    """Reads content from a file."""
    full_path = get_safe_path(path)
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not full_path.is_file():
        raise IsADirectoryError(f"Path is a directory: {path}")
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def list_files(path: str = ".") -> list[str]:
    """Lists files in a directory recursively."""
    full_path = get_safe_path(path)
    if not full_path.exists():
        return []
    
    files = []
    for p in full_path.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE_ROOT)))
    return files
