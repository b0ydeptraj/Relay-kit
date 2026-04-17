from __future__ import annotations

from typing import Dict

from .skill_models import SkillSpec, utility_provider_spec

DISCIPLINE_UTILITY_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": utility_provider_spec(
        name="root-cause-debugging",
        description="Use when a hub needs a disciplined investigation before proposing fixes. Structured root-cause debugging utility.",
        outputs=["root-cause notes and disproven hypotheses appended to investigation-notes or the active artifact"],
        references=["No fixes before investigation.", "Prefer evidence at component boundaries over guessed explanations."],
        next_steps=["debug-hub", "fix-hub", "test-hub"],
        mission="Force a root-cause-first debugging pass so the lane stops guessing and starts proving.",
        tasks=["Read the failure carefully and restate the symptom.", "Trace the issue through the narrowest useful chain of evidence.", "Record likely cause, non-causes, and the smallest validating next move."],
        rules=["Do not recommend fixes before the evidence is good enough to reject obvious alternatives.", "Prefer one hypothesis at a time.", "Escalate back to planning when the issue is really a requirements or architecture mismatch."],
    ),
    "test-first-development": utility_provider_spec(
        name="test-first-development",
        description="Use when implementation should follow a red-green-refactor loop instead of ad-hoc coding. Test-first execution utility.",
        outputs=["test-first execution notes and evidence appended to story, tech-spec, or qa-report"],
        references=["Write the failing test first when the behavior is testable.", "Keep the change minimal until the new test is green."],
        next_steps=["developer", "test-hub", "qa-governor"],
        mission="Drive implementation through the smallest useful red-green-refactor loop.",
        tasks=["Name the behavior that should fail first.", "Capture the failing test or reproduction evidence.", "Implement only enough to turn the signal green before cleanup."],
        rules=["If the behavior cannot be tested first, say why instead of pretending the loop happened.", "Keep one behavior per cycle.", "Keep tests, fixtures, and sample payloads plain ASCII unless the behavior explicitly depends on non-ASCII content.", "Do not widen scope during the green phase."],
    ),
    "evidence-before-completion": utility_provider_spec(
        name="evidence-before-completion",
        description="Use when a hub or specialist is about to say work is done, fixed, or ready. Completion-evidence utility.",
        outputs=["fresh verification evidence and claim checks appended to qa-report, workflow-state, or the active artifact"],
        references=["No completion claims without fresh verification output.", "Match every claim to the command or evidence that proves it."],
        next_steps=["test-hub", "qa-governor", "review-hub"],
        mission="Stop premature completion claims by forcing a claim-to-evidence check.",
        tasks=[
            "List the exact claims being made.",
            "Name the command, artifact, or output that proves each claim.",
            "Check whether expected artifact deltas actually exist for code-change claims.",
            "Reject claims that are not backed by fresh evidence.",
        ],
        rules=[
            "Confidence is not evidence.",
            "Partial verification is not completion.",
            "If evidence is stale or missing, route back to testing or debugging instead of approving the lane.",
            "If a code-change claim has zero file delta and zero verification output, mark it invalid unless the lane explicitly recorded a no-code outcome.",
        ],
    ),
    "srs-clarifier": utility_provider_spec(
        name="srs-clarifier",
        description="Use when non-technical requests need a structured SRS-first contract before PRD or story slicing.",
        outputs=["srs-spec draft or repaired sections with UC-ID traceability notes"],
        references=[
            "Translate plain-language requirements into actors, use cases, preconditions, postconditions, and exception flows.",
            "Keep language accessible for non-technical owners while preserving deterministic IDs for traceability.",
        ],
        next_steps=["plan-hub", "pm", "scrum-master", "qa-governor"],
        mission="Convert fuzzy non-technical intent into a stable SRS contract that downstream planning and QA can verify.",
        tasks=[
            "Create or repair `.relay-kit/contracts/srs-spec.md` using the required section template.",
            "Assign stable UC-IDs and ensure every use case has user-facing feedback and exception flow.",
            "Call out unresolved questions that block PRD-quality planning.",
        ],
        rules=[
            "Do not skip preconditions, postconditions, or exception flows when generating use cases.",
            "Prefer short, concrete sentences over jargon-heavy requirement language.",
            "When SRS-first policy is disabled, this skill stays optional and should not block quick-flow work.",
        ],
    ),
}

BASELINE_DISCIPLINE_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": DISCIPLINE_UTILITY_SKILLS["root-cause-debugging"],
    "evidence-before-completion": DISCIPLINE_UTILITY_SKILLS["evidence-before-completion"],
}
