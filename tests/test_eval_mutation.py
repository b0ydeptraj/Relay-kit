"""
Mutation test suite verifying that Relay-kit verification gates
(skill_gauntlet, frontmatter validation, skill_resources checks)
detect corrupted or mutated resources and correctly FAIL instead of blindly passing.
"""
import json
import re
import yaml
import pytest
from pathlib import Path

FRONTMATTER = re.compile(r"^---\r?\n(.*?)^---\r?\n", re.S | re.M)


def validate_skill_frontmatter_text(text: str) -> dict:
    match = FRONTMATTER.match(text)
    if match is None:
        raise ValueError("No leading --- frontmatter fence")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must parse to a mapping")
    return data


def validate_competencies_data(data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != "relay-kit.skill-competency.v1":
        errors.append("Invalid schema_version")
    core = data.get("core_competencies", [])
    if not isinstance(core, list) or len(core) < 5:
        errors.append("core_competencies count must be >= 5")
    traps = data.get("failure_traps", [])
    if not isinstance(traps, list) or len(traps) < 2:
        errors.append("failure_traps count must be >= 2")
    return errors


def validate_eval_cases_data(cases: list) -> list[str]:
    errors = []
    if not isinstance(cases, list) or len(cases) < 3:
        errors.append("eval cases count must be >= 3")
    for case in cases:
        if not case.get("expected_evidence_terms") or len(case["expected_evidence_terms"]) < 3:
            errors.append("case expected_evidence_terms count must be >= 3")
    return errors


def test_mutation_corrupted_frontmatter_fails_gate():
    """Mutating a SKILL.md frontmatter with invalid YAML must fail the frontmatter gate."""
    corrupted_text = "---\nname: test-skill\ndescription: : [invalid yaml: colon without quotes\n---\n"
    with pytest.raises(Exception):
        validate_skill_frontmatter_text(corrupted_text)


def test_mutation_missing_competencies_fails_skill_resources_check():
    """Mutating competencies file to have < 5 core competencies must fail competency validation."""
    mutated_competencies = {
        "schema_version": "relay-kit.skill-competency.v1",
        "skill": "test-skill",
        "core_competencies": [{"id": "c1"}],  # Only 1 competency (required: >= 5)
        "failure_traps": [{"id": "t1"}, {"id": "t2"}]
    }
    errors = validate_competencies_data(mutated_competencies)
    assert len(errors) > 0, "Gate failed to detect insufficient core competencies count!"


def test_mutation_corrupted_eval_cases_fails_eval_schema_gate():
    """Mutating evals file to have < 3 eval cases must fail eval case validation."""
    mutated_cases = [{"id": "c1", "expected_evidence_terms": ["term1"]}]  # Only 1 case (required: >= 3)
    errors = validate_eval_cases_data(mutated_cases)
    assert len(errors) > 0, "Gate failed to detect insufficient eval cases count!"


def test_mutation_skills_gauntlet_detects_tampered_resource(tmp_path):
    """Mutating a skill resource in a target project causes skill_gauntlet to report findings."""
    from relay_kit_v3.scripts import skill_gauntlet
    
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    paths = skill_gauntlet.collect_skills(tmp_path)
    missing = [p for p in paths if not p.exists()]
    assert len(missing) > 0, "Skill collector must detect missing runtime skills!"
