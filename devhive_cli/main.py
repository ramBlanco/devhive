import os
import shutil
import subprocess
from pathlib import Path
import click
from devhive_cli.templates_backend import generate_backend_agents_md

# Paths configuration
CLI_DIR = Path(__file__).resolve().parent
LOCAL_SKILLS_DIR = CLI_DIR / "skills"
COMMUNITY_SKILLS_DIR = CLI_DIR / "community_skills"
TEMPLATES_DIR = CLI_DIR / "templates"
LOCAL_AGENTS_DIR = CLI_DIR / "agents"
TARGET_DIR = Path.home() / ".config" / "opencode" / "skills"
TARGET_AGENTS_DIR = Path.home() / ".config" / "opencode" / "agents"

@click.group()
def cli():
    """DevHive CLI for managing AI agent skills."""
    pass

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
    sync_local_skills(clean=False)
    sync_local_agents()
    install_remote_skills()
    click.secho("\nInstallation Complete! 🎉", fg="green", bold=True)

@cli.command()
def update_skill():
    """Update all skills (cleans existing ones and reinstalls)."""
    click.secho("Updating DevHive Skills...", fg="blue", bold=True)
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
        click.secho("AGENTS.md already exists in this directory. Aborting to prevent overwrite.", fg="yellow")
        return
        
    shutil.copy2(template_path, dest_path)
    click.secho("✅ Successfully created AGENTS.md with modern Next.js/React frontend guidelines!", fg="green", bold=True)

@cli.command()
def init_backend():
    """Initialize a modern backend AGENTS.md template with Hexagonal Architecture."""
    dest_path = Path.cwd() / "AGENTS.md"
    
    if dest_path.exists():
        click.secho("AGENTS.md already exists in this directory. Aborting to prevent overwrite.", fg="yellow")
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

if __name__ == "__main__":
    cli()
