from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "devhive_cli"


def read(path: str) -> str:
    return (CLI / path).read_text(encoding="utf-8")


def test_pm_loads_planning_skills_and_publishes_a_single_approved_story_package():
    pm = read("agents/devhive-pm.md")

    assert "`devhive-backlog`" in pm
    assert "`devhive-story`" in pm
    assert "### Step 5 — Roadmap & Prioritized Backlog" in pm
    assert "### Step 6 — User Stories and Mini-Plan Tasks" in pm
    assert "docs/PRODUCT/user-stories.md" in pm
    assert "Status: Draft" in pm
    assert "Status: Approved" in pm
    assert "one consolidated review" in pm
    assert "do not pause for approval after each skill/story" in pm.lower()
    assert "do not emit a command that implies the package is approved" in pm.lower()


def test_planning_skills_support_parent_pm_batch_without_changing_standalone_review():
    backlog = read("skills/devhive-backlog/SKILL.md")
    story = read("skills/devhive-story/SKILL.md")

    assert "PM batch mode" in backlog
    assert "without asking the user" in backlog
    assert "Standalone" in backlog
    assert "PM batch mode" in story
    assert "Status: Blocked" in story
    assert "exactly **2 or 3**" in story
    assert "no more than five bullets" in story


def test_devhive_orchestrator_checks_approval_and_keeps_prd_first_fallback():
    agent = read("agents/devhive.md")
    orchestrator = read("skills/devhive-orchestrator/SKILL.md")

    assert "Status: Approved" in agent
    assert "no PM artifacts are present" in agent
    assert "self-starting SDD flow" in agent
    assert "PM package preflight" in orchestrator
    assert "Status: Approved" in orchestrator
    assert "A Draft package requires explicit user approval" in orchestrator
    assert "Partial artifacts are optional context only" in orchestrator
    assert "preserve the existing PRD-first pipeline" in orchestrator
    assert "stale or conflict" in orchestrator


def test_planning_phases_and_taskplanner_preserve_pm_story_traceability():
    explorer = read("skills/devhive-explorer/SKILL.md")
    proposal = read("skills/devhive-proposal/SKILL.md")
    architect = read("skills/devhive-architect/SKILL.md")
    planner = read("skills/devhive-taskplanner/SKILL.md")

    assert "docs/PRODUCT/user-stories.md" in explorer
    assert "approved PM package" in proposal
    assert "approved PM package" in architect
    assert "PM-###" in planner
    assert "US-###" in planner
    assert "Given/When/Then acceptance criteria" in planner
    assert "If no PM package is provided" in planner
    assert "Product Backlog ID" in planner
    assert "Acceptance Criteria:" in planner
    assert "every applicable task in any domain section" in planner
