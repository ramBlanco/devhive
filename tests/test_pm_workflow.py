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


def test_pm_requires_story_coverage_for_every_in_scope_backlog_item():
    pm = read("agents/devhive-pm.md")
    backlog = read("skills/devhive-backlog/SKILL.md")

    assert "complete prioritized backlog" in pm
    assert "Work through every backlog item" in pm
    assert "at least one story" in pm
    assert "coverage in both directions" in pm
    assert "Story IDs" in pm
    assert "complete prioritized backlog with stable `PM-###` IDs" in backlog
    assert "Do not stop after the first backlog item" in backlog
    assert "every in-scope backlog item has at least one story" in backlog
    assert "every story maps to a real backlog item" in backlog
    assert "`Won't have (this iteration)` are out of scope" in backlog


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
    assert "must select one specific `US-###`" in orchestrator
    assert "rather than choosing the first story" in orchestrator
    assert "explicitly scope the phase to that story" in orchestrator
    assert "do not default to the first story" in agent


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
    assert "plan only the specific `US-###` selected by the user" in planner
    assert "other package stories are context only" in planner
    assert "keep exploration scoped to that story" in explorer
    assert "do not include other stories as implementation scope" in proposal
    assert "other stories are context only" in architect


def test_pm_story_artifact_and_handoff_make_individual_story_selection_possible():
    pm = read("agents/devhive-pm.md")
    story = read("skills/devhive-story/SKILL.md")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "parent `PM-###` backlog item" in pm
    assert "corresponding `US-###` IDs in the backlog's `Story IDs` column" in pm
    assert "user selects the story to implement after approval" in pm
    assert "Product Backlog Item" in story
    assert "Implement story US-003 from backlog item PM-002" in readme
    assert "at least one story for every in-scope `PM-###` item" in readme
