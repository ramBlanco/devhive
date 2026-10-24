import json
import os
import shutil
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
LOCAL_PLUGINS_DIR = CLI_DIR / "plugins"
OPENCODE_CONFIG_DIR = Path.home() / ".config" / "opencode"
TARGET_DIR = OPENCODE_CONFIG_DIR / "skills"
TARGET_AGENTS_DIR = OPENCODE_CONFIG_DIR / "agents"
TARGET_PLUGINS_DIR = OPENCODE_CONFIG_DIR / "plugins"
TARGET_CONFIG_FILE = OPENCODE_CONFIG_DIR / "opencode.json"
DEVHIVE_SKILL_PATTERNS = (
    "devhive-*",
    "architecture-patterns",
    "backend-architect",
    "backend-security-coder",
    "docker-expert",
    "frontend-design",
    "frontend-developer",
    "theme-factory",
    "opencode",
    "report",
    "customize-opencode",
)
EXTERNAL_SKILL_NAMES = {"shadcn", "prd"}

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

def remove_obsolete_skills():
    """Delete obsolete skill directories from older DevHive versions."""
    if not TARGET_DIR.exists():
        return

    for obsolete_name in LEGACY_SKILL_DIRS:
        obsolete_path = TARGET_DIR / obsolete_name
        if obsolete_path.is_symlink():
            obsolete_path.unlink()
            click.secho(f"Removed obsolete skill link: {obsolete_name}", fg="yellow")
        elif obsolete_path.exists() and obsolete_path.is_dir():
            shutil.rmtree(obsolete_path)
            click.secho(f"Removed obsolete skill: {obsolete_name}", fg="yellow")


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
            if not skill_path.is_dir():
                continue
            if not (skill_path / "SKILL.md").exists():
                click.secho(
                    f"Skipped invalid skill directory (missing SKILL.md): {skill_path.name}",
                    fg="yellow",
                )
                continue

            target_skill_path = TARGET_DIR / skill_path.name
            if target_skill_path.exists():
                if target_skill_path.is_symlink():
                    target_skill_path.unlink()
                elif target_skill_path.is_dir():
                    shutil.rmtree(target_skill_path)
                else:
                    target_skill_path.unlink()
                if clean:
                    click.secho(f"Cleaned existing: {skill_path.name}", fg="yellow")

            shutil.copytree(skill_path, target_skill_path)
            click.secho(f"Installed: {skill_path.name}", fg="green")

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


def sync_local_plugins():
    """Install DevHive's plugin that exposes only bundled DevHive skills."""
    if not TARGET_PLUGINS_DIR.exists():
        TARGET_PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

    if not LOCAL_PLUGINS_DIR.exists():
        click.secho(f"Warning: Source directory {LOCAL_PLUGINS_DIR} not found.", fg="yellow")
        return

    click.secho(f"\nSyncing plugins from {LOCAL_PLUGINS_DIR.name}...", fg="cyan", bold=True)
    for plugin_file in LOCAL_PLUGINS_DIR.glob("*.ts"):
        target_file = TARGET_PLUGINS_DIR / plugin_file.name
        shutil.copy2(plugin_file, target_file)
        click.secho(f"Installed plugin: {plugin_file.name}", fg="green")

    package_file = LOCAL_PLUGINS_DIR / "package.json"
    if package_file.exists():
        shutil.copy2(package_file, TARGET_PLUGINS_DIR / package_file.name)
        click.secho("Installed plugin package metadata", fg="green")

    stale_node_modules = TARGET_PLUGINS_DIR / "node_modules" / "@opencode" / "plugin"
    if stale_node_modules.is_symlink():
        stale_node_modules.unlink()
        click.secho("Removed stale DevHive plugin dependency link", fg="yellow")
    elif stale_node_modules.exists() and stale_node_modules.is_dir():
        shutil.rmtree(stale_node_modules)
        click.secho("Removed stale DevHive plugin dependency", fg="yellow")


def configure_devhive_skill_permissions():
    """Restrict DevHive agents to DevHive's bundled skills."""
    config = {}
    if TARGET_CONFIG_FILE.exists():
        try:
            config = json.loads(TARGET_CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            click.secho(
                f"Warning: Could not update {TARGET_CONFIG_FILE}: {exc}. "
                "The file was left unchanged.",
                fg="yellow",
            )
            return

    agents = config.setdefault("agents", {})
    if not isinstance(agents, dict):
        agents = {}
        config["agents"] = agents
    if "agent" in config and isinstance(config["agent"], dict):
        legacy_agent = config.pop("agent")
        for agent_name, agent in legacy_agent.items():
            if agent_name not in agents:
                agents[agent_name] = agent
    legacy_permission = config.get("permission")
    if isinstance(legacy_permission, dict):
        migrated_permissions = config.setdefault("permissions", [])
        for action, value in legacy_permission.items():
            if isinstance(value, str):
                migrated_permissions.append(
                    {"action": action, "resource": "*", "effect": value}
                )
            elif isinstance(value, dict):
                for resource, effect in value.items():
                    migrated_permissions.append(
                        {"action": action, "resource": resource, "effect": effect}
                    )
        config.pop("permission", None)

    for agent_name in ("devhive", "devhive-pm"):
        agent = agents.setdefault(agent_name, {})
        if not isinstance(agent, dict):
            agent = {}
            agents[agent_name] = agent
        agent_permissions = agent.setdefault("permissions", [])
        if not isinstance(agent_permissions, list):
            agent_permissions = []
            agent["permissions"] = agent_permissions
        agent_permissions[:] = [
            rule for rule in agent_permissions
            if not (
                isinstance(rule, dict)
                and rule.get("action") == "skill"
                and rule.get("resource") in {"*", *DEVHIVE_SKILL_PATTERNS}
            )
        ]
        agent_permissions.insert(0, {"action": "skill", "resource": "*", "effect": "deny"})
        for skill_pattern in DEVHIVE_SKILL_PATTERNS:
            agent_permissions.append(
                {"action": "skill", "resource": skill_pattern, "effect": "allow"}
            )

    TARGET_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    TARGET_CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    click.secho("Configured DevHive agents to use only DevHive skills", fg="green")


def remove_obsolete_external_skills():
    """Remove external skills and remote skill sources from OpenCode."""
    skill_roots = [
        TARGET_DIR,
        OPENCODE_CONFIG_DIR / "skill",
        Path.home() / ".claude" / "skills",
        Path.home() / ".agents" / "skills",
        Path.cwd() / ".opencode" / "skills",
        Path.cwd() / ".opencode" / "skill",
        Path.cwd() / ".claude" / "skills",
        Path.cwd() / ".agents" / "skills",
        Path.cwd() / "skills",
    ]

    for root in skill_roots:
        for name in EXTERNAL_SKILL_NAMES:
            skill_path = root / name
            if skill_path.is_symlink():
                skill_path.unlink()
                click.secho(f"Removed external skill link: {skill_path}", fg="yellow")
            elif skill_path.exists() and skill_path.is_dir():
                shutil.rmtree(skill_path)
                click.secho(f"Removed external skill: {skill_path}", fg="yellow")

    remove_remote_skill_sources()


def remove_remote_skill_sources():
    """Remove HTTP skill catalogs from the global OpenCode configuration."""
    if not TARGET_CONFIG_FILE.exists():
        return

    try:
        config = json.loads(TARGET_CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        click.secho(
            f"Warning: Could not update {TARGET_CONFIG_FILE}: {exc}. "
            "The file was left unchanged.",
            fg="yellow",
        )
        return

    changed = False
    sources = config.get("skills")
    if isinstance(sources, list):
        retained = []
        for source in sources:
            value = source.get("package", "") if isinstance(source, dict) else str(source)
            if value.startswith(("http://", "https://")):
                changed = True
                continue
            retained.append(source)
        config["skills"] = retained

    legacy_skill_config = config.get("skill")
    if isinstance(legacy_skill_config, dict):
        legacy_paths = legacy_skill_config.get("paths")
        legacy_urls = legacy_skill_config.get("urls")
        if isinstance(legacy_paths, list):
            retained_paths = [
                path
                for path in legacy_paths
                if not str(path).startswith(("http://", "https://"))
            ]
            legacy_skill_config["paths"] = retained_paths
            changed = changed or len(retained_paths) != len(legacy_paths)
        if isinstance(legacy_urls, list):
            legacy_skill_config["urls"] = []
            changed = changed or bool(legacy_urls)

    if changed:
        TARGET_CONFIG_FILE.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        click.secho("Removed remote skill sources from OpenCode configuration", fg="yellow")

@cli.command()
def install():
    """Install DevHive's bundled skills and agents only."""
    click.secho("Starting DevHive Skills Installation...", fg="green", bold=True)
    remove_obsolete_skills()
    remove_obsolete_external_skills()
    sync_local_skills(clean=False)
    sync_local_agents()
    sync_local_plugins()
    configure_devhive_skill_permissions()
    click.secho("\nInstallation Complete! 🎉", fg="green", bold=True)

@cli.command()
def update_skill():
    """Update DevHive's bundled skills and agents only."""
    click.secho("Updating DevHive Skills...", fg="blue", bold=True)
    remove_obsolete_skills()
    remove_obsolete_external_skills()
    sync_local_skills(clean=True)
    sync_local_agents()
    sync_local_plugins()
    configure_devhive_skill_permissions()
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


@memory.command(name="list")
def list_entries():
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
