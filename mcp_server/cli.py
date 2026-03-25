import argparse
import sys
import shutil
import json
import os
from pathlib import Path

# Try to find default agent file location relative to package
# This assumes the package structure allows finding the file in the root
PACKAGE_ROOT = Path(__file__).parent.parent
DEFAULT_AGENT_PATH = PACKAGE_ROOT / "DEVHIVE_AGENT.md"

def get_default_agent_content():
    """Reads the DEVHIVE_AGENT.md content from the package source."""
    if DEFAULT_AGENT_PATH.exists():
        return DEFAULT_AGENT_PATH.read_text()
    
    # Fallback content if file is totally missing (should not happen in proper install)
    return """# DevHive Agent System Prompt

You are the DevHive Agent, an autonomous software development orchestrator.
Your goal is to manage the full software development lifecycle using the DevHive MCP server tools.

## Core Workflow

1.  **Start/Resume Project**:
    - Use `devhive_start_pipeline(project_name, requirements)` to initialize a project or get the next task.
    - If the project already exists, this will resume from the last state.

2.  **Execute Task**:
    - The output of `devhive_start_pipeline` (or `devhive_submit_result`) provides a `next_task` object containing:
        - `agent`: The sub-agent role (e.g., Explorer, Developer).
        - `system_prompt`: The specific instructions for this sub-agent.
        - `user_prompt`: The context and requirements for the task.
    - You must execute this task. 
      - **OpenCode**: Use the `Task` tool with the provided prompts.
      - **Copilot**: Act as the sub-agent directly using the prompts.

3.  **Submit Result**:
    - Once the sub-agent task is complete, use `devhive_submit_result(project_name, agent_name, llm_response)` to save the work.
    - This tool will return the *next* task in the pipeline.
    - Repeat step 2 with the new task.

## Available Tools

- `devhive_start_pipeline`: Initialize project and get first task.
- `devhive_submit_result`: Save task result and get next task.
- `devhive_search_memory`: Retrieve context from previous steps.
- `devhive_get_memory_stats`: Check project memory usage.
- `devhive_get_recent_memories`: See recent project activity.

## Important Instructions

- Always follow the strict sequential pipeline: Explorer -> Proposal -> Architect -> TaskPlanner -> Developer -> QA -> Auditor -> Archivist.
- Do not skip steps unless the pipeline explicitly skips them.
- Use the prompts provided by the tools exactly as given.
"""

def configure():
    print("DevHive CLI Configuration")
    print("-------------------------")

    # 1. Ask user for client type
    while True:
        choice = input("Do you use OpenCode, Copilot, or both? [opencode/copilot/both]: ").lower().strip()
        if choice in ["opencode", "copilot", "both"]:
            break
        print("Invalid choice. Please type 'opencode', 'copilot', or 'both'.")

    # 2. Locate source file
    cwd_agent = Path("DEVHIVE_AGENT.md").resolve()
    pkg_agent = DEFAULT_AGENT_PATH.resolve()
    
    source_to_use = None
    
    if cwd_agent.exists():
        print(f"[+] Found agent file in current directory: {cwd_agent}")
        source_to_use = cwd_agent
    elif pkg_agent.exists():
        print(f"[+] Found agent file in package: {pkg_agent}")
        source_to_use = pkg_agent
    else:
        print("[-] DEVHIVE_AGENT.md not found.")
        print("[*] Using embedded default agent prompt.")
        temp_path = Path("DEVHIVE_AGENT.md").resolve()
        try:
            with open(temp_path, "w") as f:
                f.write(get_default_agent_content())
            print(f"[+] Created temporary source file at: {temp_path}")
            source_to_use = temp_path
        except Exception as e:
            print(f"[-] Failed to create source file: {e}")
            return

    # 3. Configure OpenCode
    if choice in ["opencode", "both"]:
        dest_dir = Path.home() / ".config" / "opencode" / "agents"
        dest_file = dest_dir / "DevHive.md"
        _copy_agent_file(source_to_use, dest_dir, dest_file, "OpenCode Agent")
        _configure_mcp_server()

    # 4. Configure Copilot
    if choice in ["copilot", "both"]:
        dest_dir = Path.home() / ".copilot" / "agents"
        dest_file = dest_dir / "DevHive.md"
        _copy_agent_file(source_to_use, dest_dir, dest_file, "Copilot Agent")
        _configure_vscode_copilot(dest_file)

    print("\nConfiguration complete!")

def _copy_agent_file(source, dest_dir, dest_file, client_name):
    print(f"\n--- Configuring {client_name} ---")
    try:
        if not dest_dir.exists():
            print(f"[*] Creating directory: {dest_dir}")
            dest_dir.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source, dest_file)
        print(f"[+] Successfully installed agent to: {dest_file}")
    except Exception as e:
        print(f"[-] Failed to configure {client_name}: {e}")

def _configure_vscode_copilot(agent_file_path):
    print("\n--- Configuring VS Code Copilot ---")
    confirm = input("Do you want to add DevHive instructions to VS Code global settings? [y/N]: ").lower().strip()
    if confirm != 'y':
        return

    # Standard VS Code settings path on Linux/Mac
    settings_path = Path.home() / ".config" / "Code" / "User" / "settings.json"
    
    if not settings_path.exists():
        # Try macOS path if Linux path fails
        settings_path_mac = Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"
        if settings_path_mac.exists():
            settings_path = settings_path_mac
        else:
            print(f"[-] VS Code settings not found at standard locations.")
            return

    try:
        with open(settings_path, "r") as f:
            # Handle comments in json if present (VS Code allows comments, generic json parser doesn't)
            # Simple approach: try standard load, fail if comments
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print("[-] Failed to parse settings.json (might contain comments). Skipping automatic update.")
                print(f"[*] Please manually add 'github.copilot.chat.codeGeneration.instructions' pointing to: {agent_file_path}")
                return

        key = "github.copilot.chat.codeGeneration.instructions"
        
        # Prepare instruction object
        instruction_entry = {"file": str(agent_file_path)}
        
        if key not in config:
            config[key] = [instruction_entry]
        else:
            # If it's a list, append if not exists
            if isinstance(config[key], list):
                # Check for duplicates
                exists = False
                for item in config[key]:
                    if isinstance(item, dict) and item.get("file") == str(agent_file_path):
                        exists = True
                        break
                if not exists:
                    config[key].append(instruction_entry)
            else:
                # If it's weird (legacy string?), convert to list
                print(f"[*] converting existing '{key}' to list format")
                config[key] = [instruction_entry]

        # Backup first
        shutil.copy2(settings_path, str(settings_path) + ".bak")
        print(f"[*] Backed up settings to: {str(settings_path)}.bak")

        with open(settings_path, "w") as f:
            json.dump(config, f, indent=4)
            
        print(f"[+] Updated VS Code settings at: {settings_path}")
        
    except Exception as e:
        print(f"[-] Failed to update VS Code settings: {e}")

def _configure_mcp_server():
    print("\n--- Configuring MCP Server Connection ---")
    confirm = input("Do you want to add the DevHive MCP server to OpenCode config? [y/N]: ").lower().strip()
    if confirm != 'y':
        return

    # Default locations to check
    possible_paths = [
        Path.home() / ".config" / "opencode" / "opencode.json",
        Path.home() / ".config" / "opencode" / "config.json"
    ]
    
    default_config = possible_paths[0]
    for p in possible_paths:
        if p.exists():
            default_config = p
            break

    config_path_str = input(f"Enter path to OpenCode config [{default_config}]: ").strip()
    
    if not config_path_str:
        config_path = default_config
    else:
        config_path = Path(config_path_str).expanduser().resolve()

    if not config_path.exists():
        print(f"[-] Config file not found at: {config_path}")
        create = input("Create new config file? [y/N]: ").lower().strip()
        if create == 'y':
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w") as f:
                    json.dump({"mcp": {}}, f, indent=2)
                print(f"[+] Created new config file.")
            except Exception as e:
                print(f"[-] Failed to create config: {e}")
                return
        else:
            return

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        if "mcp" not in config:
            config["mcp"] = {}

        # Detect Python Interpreter
        python_cmd = sys.executable
        
        # Check for .venv in current directory
        venv_python = Path.cwd() / ".venv" / "bin" / "python"
        if venv_python.exists():
            print(f"[*] Found virtual environment at: {venv_python}")
            use_venv = input(f"Use this virtual environment for the server? [Y/n]: ").lower().strip()
            if use_venv in ['', 'y', 'yes']:
                python_cmd = str(venv_python)
        
        # Construct command
        server_command = [python_cmd, "-m", "mcp_server.server"]
        
        config["mcp"]["devhive"] = {
            "type": "local",
            "command": server_command,
            "enabled": True,
            "env": {
                "PYTHONUNBUFFERED": "1"
            }
        }
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            
        print(f"[+] Updated MCP config at: {config_path}")
        print(f"    Server command: {' '.join(server_command)}")
        
    except Exception as e:
        print(f"[-] Failed to update MCP config: {e}")

def start():
    """Starts the MCP server."""
    try:
        from mcp_server.server import main as server_main
        print(f"[*] Starting DevHive MCP Server (PID {os.getpid()})...")
        server_main()
    except ImportError:
        # Check for venv and restart
        venv_python = Path.cwd() / ".venv" / "bin" / "python"
        if venv_python.exists() and sys.executable != str(venv_python):
            print(f"[*] 'mcp' not found in current environment.")
            print(f"[*] Switching to virtual environment at: {venv_python}")
            # Re-execute using venv python
            os.execv(str(venv_python), [str(venv_python)] + sys.argv)
        else:
            print("[-] Error: Could not import mcp_server.server")
            print("[-] Ensure dependencies are installed or activate your virtual environment.")
            return
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user.")
    except Exception as e:
        print(f"[-] Server error: {e}")

def main():
    parser = argparse.ArgumentParser(description="DevHive CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Configure command
    configure_parser = subparsers.add_parser("configure", help="Configure DevHive agent for OpenCode/Copilot")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start the MCP server locally")

    # If no arguments, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.command == "configure":
        configure()
    elif args.command == "start":
        start()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
