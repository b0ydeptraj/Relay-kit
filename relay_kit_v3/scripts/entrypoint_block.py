

PUBLIC_ENTRYPOINT_SKILLS: Dict[str, SkillSpec] = {
    "brainstorm": SkillSpec(
        name="brainstorm",
        description='Use when a rough idea needs to become a clear direction before implementation begins. Public Relay-kit entrypoint for brainstorming.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "build-it": SkillSpec(
        name="build-it",
        description='Use when an approved story or tech spec is ready for implementation with controlled scope and evidence. Public Relay-kit entrypoint for building.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "debug-systematically": SkillSpec(
        name="debug-systematically",
        description='Use when a bug, regression, flaky behavior, or mismatch needs disciplined debugging instead of guessing. Public Relay-kit entrypoint for the debug path.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "prove-it": SkillSpec(
        name="prove-it",
        description='Use when a completion claim needs one last evidence pass before work is called done, fixed, or ready. Public Relay-kit entrypoint for final proof.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "ready-check": SkillSpec(
        name="ready-check",
        description='Use when code exists and you need a real go or no-go decision about readiness or shipability. Public Relay-kit entrypoint for review and QA gating.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "review-pr": SkillSpec(
        name="review-pr",
        description='Use when a branch or PR needs a deliberate review before merge or sign-off. Public Relay-kit entrypoint for branch and PR review.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "start-here": SkillSpec(
        name="start-here",
        description='Use when a request arrives and you want Relay-kit to pick the right path, next skill, and next artifact without guessing. Easiest public Relay-kit entrypoint.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "write-steps": SkillSpec(
        name="write-steps",
        description='Use when approved work needs to be sliced into small, buildable, verifiable implementation steps. Public Relay-kit entrypoint for implementation slicing.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
}
