from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "devhive_cli" / "skills"


def test_backlog_skill_returns_traceable_user_story_format_without_implicit_execution():
    content = (SKILLS / "devhive-backlog" / "SKILL.md").read_text(encoding="utf-8")

    assert "As a [user/persona], I want [capability], so that [user value]." in content
    assert "**Source:**" in content
    assert "do not add estimates, priority scores, implementation tasks" in content
    assert "not authorization to implement it" in content


def test_story_skill_enforces_criteria_and_plan_cardinality():
    content = (SKILLS / "devhive-story" / "SKILL.md").read_text(encoding="utf-8")

    assert "exactly **2 or 3**" in content
    assert "every criterion with all three labels: **Given**, **When**, and **Then**" in content
    assert "no more than five bullets" in content
    assert "exactly 2 or 3 numbered criteria" in content
    assert "between one and five bullets" in content
    assert "Approval never triggers implementation." in content
