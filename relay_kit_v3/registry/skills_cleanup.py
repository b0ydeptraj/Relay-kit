from __future__ import annotations

from textwrap import dedent
from typing import Dict

from .skill_models import SkillSpec

CLEANUP_SKILLS: Dict[str, SkillSpec] = {
    "execution-loop": SkillSpec(
        name="execution-loop",
        description="Use when building or fixing code iteratively and require evidence before claiming completion. Self-correcting development loop for implementation work.",
        role="developer-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["story or tech-spec", "project-context", "relevant support skills"],
        outputs=["working code plus test evidence"],
        references=[
            "testing-patterns",
            "If discipline utilities are installed, use `root-cause-debugging` before repeated fix attempts.",
            "If discipline utilities are installed, use `evidence-before-completion` before claiming success.",
            "State the slice objective and expected files before each cycle so context does not rot across long loops.",
        ],
        next_steps=["test-hub", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Execute implementation work in a tight loop without resorting to random fixes.

            ## The loop
            1. Understand the story or tech-spec completely.
            2. Make the smallest viable code change toward the goal.
            3. Run the relevant checks or tests.
            4. Analyze the result.
            5. If it failed, debug root cause before changing anything else.
            6. If it passed, collect evidence and hand off to QA.

            ## Non-negotiable rules
            - No quick fixes without root-cause reasoning.
            - No stacking multiple unrelated changes in one test cycle.
            - Write or update a failing test whenever the change fixes a bug.
            - Default to plain ASCII in code, comments, tests, fixtures, and sample data unless the repo or product explicitly requires non-ASCII content.
            - Do not say done without fresh evidence from commands actually run.
            - A code-change claim is invalid when there is zero file delta and zero verification output unless the task is explicitly a no-code decision update.

            ## Failure protocol
            After three failed fix attempts, stop and question the story, architecture, or assumptions instead of thrashing.
            """
        ).strip(),
    ),
}
