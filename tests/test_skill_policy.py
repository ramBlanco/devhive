from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / "devhive_cli" / "plugins" / "devhive-skills-only.ts"


def test_plugin_allows_devhive_and_project_skills_but_removes_external_skills():
    source = PLUGIN_PATH.read_text(encoding="utf-8")

    assert "ctx.skill.transform" in source
    assert "editor.remove(skill.id)" in source
    assert "isDevHiveSkill(skill.id)" in source
    assert "isBuiltInSkill(skill.id, skill.path)" in source
    assert "isProjectSkill(skill.path, projectRoot)" in source
    assert "/.opencode/skills" in source
    assert "/.claude/skills" in source
    assert "/.agents/skills" in source
    assert "${projectRoot}/skills" in source


def test_repository_has_no_external_skill_installer():
    main_source = (ROOT / "devhive_cli" / "main.py").read_text(encoding="utf-8")

    assert "npx" not in main_source
    assert "github.com/shadcn" not in main_source
    assert "awesome-copilot" not in main_source
    assert "subprocess" not in main_source


def test_bundled_skills_do_not_depend_on_external_skills():
    root = ROOT / "devhive_cli"
    sources = list((root / "skills").glob("*/SKILL.md"))
    sources += list((root / "community_skills").glob("*/SKILL.md"))
    sources += list((root / "agents").glob("*.md"))
    sources += list((root / "templates").glob("*.md"))

    for source in sources:
        content = source.read_text(encoding="utf-8").lower()
        assert "github.com/shadcn" not in content, source
        assert "awesome-copilot" not in content, source


def test_bundled_agents_and_skills_have_valid_frontmatter():
    root = ROOT / "devhive_cli"
    skill_files = list((root / "skills").glob("*/SKILL.md"))
    skill_files += list((root / "community_skills").glob("*/SKILL.md"))

    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---\n"), skill_file
        frontmatter = content.split("---", 2)[1]
        assert "name:" in frontmatter, skill_file
        assert "description:" in frontmatter, skill_file

    for agent_file in (root / "agents").glob("*.md"):
        content = agent_file.read_text(encoding="utf-8")
        assert content.startswith("---\n"), agent_file
        frontmatter = content.split("---", 2)[1]
        assert "description:" in frontmatter, agent_file
        if "permissions:" in frontmatter:
            assert "action: skill" in frontmatter, agent_file
            assert "resource:" in frontmatter, agent_file
            assert "effect:" in frontmatter, agent_file


def test_product_planning_skills_define_required_output_contracts():
    skill_root = ROOT / "devhive_cli" / "skills"
    backlog = (skill_root / "devhive-backlog" / "SKILL.md").read_text(encoding="utf-8")
    story = (skill_root / "devhive-story" / "SKILL.md").read_text(encoding="utf-8")

    assert "name: devhive-backlog" in backlog
    assert "traceability" in backlog.lower()
    assert "Do not invent" in backlog or "Never invent" in backlog
    assert "approval" in backlog.lower()

    assert "name: devhive-story" in story
    assert "exactly **2 or 3**" in story
    assert "Given" in story and "When" in story and "Then" in story
    assert "no more than five bullets" in story
    assert "approval never triggers implementation" in story.lower()


def test_manifest_packages_plugin_assets():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "recursive-include devhive_cli/plugins *" in manifest
    assert (ROOT / "devhive_cli" / "plugins" / "devhive-skills-only.ts").exists()
    assert (ROOT / "devhive_cli" / "plugins" / "package.json").exists()


def test_python_and_plugin_allowlists_match():
    python_source = (ROOT / "devhive_cli" / "main.py").read_text(encoding="utf-8")
    plugin_source = PLUGIN_PATH.read_text(encoding="utf-8")

    for skill_pattern in ("devhive-*", "architecture-patterns", "backend-architect",
                          "backend-security-coder", "docker-expert", "frontend-design",
                          "frontend-developer", "theme-factory"):
        assert f'"{skill_pattern}"' in python_source
        if skill_pattern == "devhive-*":
            assert "/^devhive-/" in plugin_source
        else:
            assert f"/^{skill_pattern}$/" in plugin_source
