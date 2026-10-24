import os
import shutil
import subprocess
from pathlib import Path
import click
from devhive_cli.templates_backend import generate_backend_agents_md
from devhive_cli.memory import MemoryCLI, get_memory_cli, ensure_memory_dir

# Paths configuration
CLI_DIR = Path(__file__).resolve().parent
LOCAL_SKILLS_DIR = CLI_DIR / "skills"
COMMUNITY_SKILLS_DIR = CLI_DIR / "community_skills"
TEMPLATES_DIR = CLI_DIR / "templates"
LOCAL_AGENTS_DIR = CLI_DIR / "agents"
TARGET_DIR = Path.home() / ".config" / "opencode" / "skills"
TARGET_AGENTS_DIR = Path.home() / ".config" / "opencode" / "agents"

def handle_existing_agents_md(dest_path: Path) -> bool:
    """
    Handles the case where AGENTS.md already exists.

    DevHive never modifies a pre-existing guidance file. If AGENTS.md is already
    present the command refuses to run and leaves the file untouched.

    Returns True if the caller should proceed to write the file, False otherwise.
    """
    click.secho(
        f"⚠️ {dest_path.name} already exists. It was left untouched.",
        fg="yellow",
    )
    click.secho(
        "DevHive will not overwrite or inject content into an existing guidance file.\n"
        "Delete or rename it manually if you want to generate a fresh template.",
        fg="yellow",
    )
    return False

@click.group()
def cli():
    """DevHive CLI for managing AI agent skills."""
    pass

# Legacy skill directory names that used underscores. OpenCode derives the skill ID
# from the directory path, so `devhive_prd/` was loadable as "devhive_prd" only.
# The skills were renamed to hyphens (e.g. `devhive-prd/`) to match the `name`
# declared in each SKILL.md. These legacy directories are removed on install so
# stale duplicates do not linger in the target skills directory.
LEGACY_SKILL_DIRS = [
    "devhive_analyzer", "devhive_architect", "devhive_auditor", "devhive_backender",
    "devhive_dba", "devhive_designer", "devhive_devops", "devhive_explorer",
    "devhive_frontender", "devhive_orchestrator", "devhive_perf", "devhive_prd",
    "devhive_proposal", "devhive_qa", "devhive_reflection", "devhive_releaser",
    "devhive_sast", "devhive_taskplanner", "devhive_techwriter",
    "backend-arthitect",
]


def remove_legacy_skill_dirs():
    """Delete skill directories from older DevHive versions that used legacy names."""
    if not TARGET_DIR.exists():
        return

    for legacy_name in LEGACY_SKILL_DIRS:
        legacy_path = TARGET_DIR / legacy_name
        if legacy_path.exists() and legacy_path.is_dir():
            shutil.rmtree(legacy_path)
            click.secho(f"Removed legacy skill: {legacy_name}", fg="yellow")


def sync_local_skills(clean=False):
    if not TARGET_DIR.exists():
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        click.secho(f"Created target directory: {TARGET_DIR}", fg="green")
    
    for src_dir in [LOCAL_SKILLS_DIR, COMMUNITY_SKILLS_DIR]:
        if not src_dir.exists():
            click.secho(f"Warning: Source directory {src_dir} not found.", fg="yellow")
            continue
        
        click.secho(f"\nSyncing from {src_dir.name}...", fg="cyan", bold=True)
        for skill_path in src_dir.iterdir():
            if skill_path.is_dir():
                target_skill_path = TARGET_DIR / skill_path.name
                
                # If cleaning, remove existing before copying
                if clean and target_skill_path.exists():
                    shutil.rmtree(target_skill_path)
                    click.secho(f"Cleaned existing: {skill_path.name}", fg="yellow")
                
                if not target_skill_path.exists():
                    shutil.copytree(skill_path, target_skill_path)
                    click.secho(f"Installed: {skill_path.name}", fg="green")
                else:
                    # Update existing (removing first to avoid partial overrides)
                    shutil.rmtree(target_skill_path)
                    shutil.copytree(skill_path, target_skill_path)
                    click.secho(f"Updated: {skill_path.name}", fg="blue")

def sync_local_agents():
    if not TARGET_AGENTS_DIR.exists():
        TARGET_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not LOCAL_AGENTS_DIR.exists():
        click.secho(f"Warning: Source directory {LOCAL_AGENTS_DIR} not found.", fg="yellow")
        return
        
    click.secho(f"\nSyncing agents from {LOCAL_AGENTS_DIR.name}...", fg="cyan", bold=True)
    for agent_file in LOCAL_AGENTS_DIR.glob("*.md"):
        target_file = TARGET_AGENTS_DIR / agent_file.name
        shutil.copy2(agent_file, target_file)
        click.secho(f"Installed agent: {agent_file.name}", fg="green")

def install_remote_skills():
    click.secho("\nInstalling official remote skills via npx...", fg="cyan", bold=True)
    commands = [
        ["npx", "--yes", "skills", "add", "https://github.com/shadcn/ui", "--skill", "shadcn", "-y", "--global"],
        ["npx", "--yes", "skills", "add", "https://github.com/github/awesome-copilot", "--skill", "prd", "-y", "--global"]
    ]
    
    for cmd in commands:
        click.secho(f"Running: {' '.join(cmd)}", fg="magenta")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            click.secho(f"Error installing remote skill: {e}", fg="red")

@cli.command()
def install():
    """Install all devhive and community skills."""
    click.secho("Starting DevHive Skills Installation...", fg="green", bold=True)
    remove_legacy_skill_dirs()
    sync_local_skills(clean=False)
    sync_local_agents()
    install_remote_skills()
    click.secho("\nInstallation Complete! 🎉", fg="green", bold=True)

@cli.command()
def update_skill():
    """Update all skills (cleans existing ones and reinstalls)."""
    click.secho("Updating DevHive Skills...", fg="blue", bold=True)
    remove_legacy_skill_dirs()
    sync_local_skills(clean=True)
    sync_local_agents()
    install_remote_skills()
    click.secho("\nUpdate Complete! 🚀", fg="green", bold=True)

@cli.command()
def init_frontend():
    """Initialize a modern frontend AGENTS.md template in the current directory."""
    template_path = TEMPLATES_DIR / "AGENTS.frontend.md"
    dest_path = Path.cwd() / "AGENTS.md"
    
    if not template_path.exists():
        click.secho("Error: Frontend template not found in the devhive package.", fg="red")
        return
        
    if dest_path.exists():
        if not handle_existing_agents_md(dest_path):
            return
        
    shutil.copy2(template_path, dest_path)
    click.secho("✅ Successfully created AGENTS.md with modern Next.js/React frontend guidelines!", fg="green", bold=True)

@cli.command()
def init_backend():
    """Initialize a modern backend AGENTS.md template with Hexagonal Architecture."""
    dest_path = Path.cwd() / "AGENTS.md"
    
    if dest_path.exists():
        if not handle_existing_agents_md(dest_path):
            return

    language = click.prompt("Which backend language?", type=click.Choice(['python', 'node']))
    
    use_di = False
    if language == 'python':
        framework = click.prompt("Which framework?", type=click.Choice(['fastapi', 'django', 'none']))
    else:
        framework = click.prompt("Which framework?", type=click.Choice(['express', 'nestjs', 'none']))
        if framework != 'nestjs':
            use_di = click.confirm("Do you want to use InversifyJS for Dependency Injection?")
    
    iac = click.prompt("Which IaC tool are you using?", type=click.Choice(['cdk', 'terraform', 'serverless']))
    
    template_path = TEMPLATES_DIR / "AGENTS.backend.md"
    if not template_path.exists():
        click.secho("Error: Backend template not found in the devhive package.", fg="red")
        return

    md_content = generate_backend_agents_md(template_path, language, framework, iac, use_di)
    
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    click.secho("✅ Successfully created AGENTS.md with Hexagonal Architecture guidelines!", fg="green", bold=True)


@cli.group()
def memory():
    """Manage DevHive persistent memory."""
    pass


@memory.command()
def list():
    """List all memory entries."""
    cli_instance = get_memory_cli()
    cli_instance.list_entries()


@memory.command()
def show():
    """Show all entries of a specific memory type."""
    click.echo("Available types: semantic, episodic, anti_patterns")
    entry_type = click.prompt("Memory type", type=click.Choice(['semantic', 'episodic', 'anti_patterns']))
    cli_instance = get_memory_cli()
    cli_instance.list_entries(entry_type)


@memory.command()
@click.argument("query")
@click.option("--type", "entry_type", default=None, help="Filter by type (semantic, episodic, anti_patterns)")
def search(query, entry_type):
    """Search memory entries by query."""
    cli_instance = get_memory_cli()
    cli_instance.search_entries(query, entry_type)


@memory.command()
@click.argument("entry_id")
def info(entry_id):
    """Show detailed info for a memory entry."""
    cli_instance = get_memory_cli()
    cli_instance.show_entry(entry_id)


@memory.command()
@click.argument("entry_id")
def delete(entry_id):
    """Delete a memory entry by ID."""
    cli_instance = get_memory_cli()
    if click.confirm(f"Delete entry '{entry_id}'?"):
        cli_instance.delete_entry(entry_id)


@memory.command()
def stats():
    """Show memory statistics."""
    cli_instance = get_memory_cli()
    cli_instance.show_stats()


@memory.command()
@click.option("--type", "entry_type", default=None, help="Export specific type")
@click.option("--output", "-o", "output_file", default=None, help="Output file path")
def export(entry_type, output_file):
    """Export memory entries to JSON."""
    cli_instance = get_memory_cli()
    cli_instance.export_memory(entry_type, output_file)


@memory.command()
@click.argument("input_file")
def import_mem(input_file):
    """Import memory entries from JSON file."""
    cli_instance = get_memory_cli()
    cli_instance.import_memory(input_file)


@memory.command()
@click.option("--threshold", default=0.5, help="Score threshold for garbage collection")
def gc(threshold):
    """Garbage collect memory entries below threshold."""
    cli_instance = get_memory_cli()
    cli_instance.garbage_collect(float(threshold))


if __name__ == "__main__":
    cli()
