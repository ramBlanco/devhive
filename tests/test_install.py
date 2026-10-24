import json
from pathlib import Path

from devhive_cli import main as devhive_main


def create_skill(path: Path, name: str) -> None:
    skill_dir = path / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Test skill\n---\n\nTest content.\n",
        encoding="utf-8",
    )


def test_install_syncs_only_bundled_skills_and_agents(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    assert "Installing official remote skills" not in result.output
    assert "npx" not in result.output

    skills_dir = isolated_home / ".config" / "opencode" / "skills"
    assert (skills_dir / "devhive-prd" / "SKILL.md").exists()
    assert (skills_dir / "devhive-backlog" / "SKILL.md").exists()
    assert (skills_dir / "devhive-story" / "SKILL.md").exists()
    assert (skills_dir / "frontend-design" / "SKILL.md").exists()
    assert not (skills_dir / "shadcn").exists()
    assert not (skills_dir / "prd").exists()

    agents_dir = isolated_home / ".config" / "opencode" / "agents"
    assert (agents_dir / "devhive.md").exists()
    assert (agents_dir / "devhive-pm.md").exists()

    plugins_dir = isolated_home / ".config" / "opencode" / "plugins"
    assert (plugins_dir / "devhive-skills-only.ts").exists()
    assert (plugins_dir / "package.json").exists()


def test_install_removes_previous_external_skills(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    skills_dir = isolated_home / ".config" / "opencode" / "skills"
    create_skill(skills_dir, "shadcn")
    create_skill(skills_dir, "prd")
    create_skill(skills_dir, "devhive_prd")

    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    assert not (skills_dir / "shadcn").exists()
    assert not (skills_dir / "prd").exists()
    assert not (skills_dir / "devhive_prd").exists()
    assert (skills_dir / "devhive-prd").exists()


def test_install_removes_external_skill_symlink_safely(runner, isolated_home, tmp_path, monkeypatch):
    monkeypatch.chdir(isolated_home)
    skills_dir = isolated_home / ".config" / "opencode" / "skills"
    skills_dir.mkdir(parents=True)
    external_skill = tmp_path / "external-prd"
    external_skill.mkdir()
    (external_skill / "SKILL.md").write_text("test", encoding="utf-8")
    (skills_dir / "prd").symlink_to(external_skill, target_is_directory=True)

    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    assert not (skills_dir / "prd").exists()
    assert external_skill.exists()


def test_install_removes_remote_skill_sources_from_config(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    config_path = isolated_home / ".config" / "opencode" / "opencode.json"

    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps(
            {
                "skills": [
                    "https://example.com/skills/",
                    "./internal-skills",
                ],
                "skill": {
                    "paths": ["https://example.com/legacy-skills/", "./legacy-skills"],
                    "urls": ["https://example.com/catalog/"],
                },
                "permission": {"edit": "allow"},
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    config = json.loads(config_path.read_text(encoding="utf-8"))
    assert config["skills"] == ["./internal-skills"]
    assert config["skill"]["paths"] == ["./legacy-skills"]
    assert config["skill"]["urls"] == []
    assert "permission" not in config
    assert {"action": "edit", "resource": "*", "effect": "allow"} in config["permissions"]


def test_install_restricts_only_devhive_agents(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    config_path = isolated_home / ".config" / "opencode" / "opencode.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))

    assert "agent" not in config

    devhive_permissions = config["agents"]["devhive"]["permissions"]
    assert devhive_permissions[0] == {"action": "skill", "resource": "*", "effect": "deny"}
    assert {
        "action": "skill",
        "resource": "devhive-*",
        "effect": "allow",
    } in devhive_permissions
    assert {
        "action": "skill",
        "resource": "frontend-design",
        "effect": "allow",
    } in devhive_permissions
    assert {
        "action": "skill",
        "resource": "opencode",
        "effect": "allow",
    } in devhive_permissions

    pm_permissions = config["agents"]["devhive-pm"]["permissions"]
    assert pm_permissions[0] == {"action": "skill", "resource": "*", "effect": "deny"}
    assert {
        "action": "skill",
        "resource": "devhive-*",
        "effect": "allow",
    } in pm_permissions
    assert {
        "action": "skill",
        "resource": "customize-opencode",
        "effect": "allow",
    } in pm_permissions


def test_update_skill_does_not_run_external_installer(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    result = runner.invoke(devhive_main.update_skill)

    assert result.exit_code == 0, result.output
    assert "npx" not in result.output


def test_install_preserves_unrelated_plugin_dependencies(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    plugins_dir = isolated_home / ".config" / "opencode" / "plugins"
    unrelated_dependency = plugins_dir / "node_modules" / "unrelated-plugin"
    unrelated_dependency.mkdir(parents=True)
    (unrelated_dependency / "package.json").write_text("{}", encoding="utf-8")

    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    assert unrelated_dependency.exists()


def test_install_preserves_project_local_skills(runner, isolated_home, monkeypatch):
    monkeypatch.chdir(isolated_home)
    project_skill = isolated_home / ".opencode" / "skills" / "team-skill"
    project_skill.mkdir(parents=True)
    (project_skill / "SKILL.md").write_text("test", encoding="utf-8")

    result = runner.invoke(devhive_main.install)

    assert result.exit_code == 0, result.output
    assert (project_skill / "SKILL.md").exists()
