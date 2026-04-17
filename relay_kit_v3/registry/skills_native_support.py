from __future__ import annotations

from textwrap import dedent
from typing import Dict

from .skill_models import SkillSpec

NATIVE_SUPPORT_SKILLS: Dict[str, SkillSpec] = {
    "project-architecture": SkillSpec(
        name="project-architecture",
        description="Use when designing a change, reviewing architectural drift, or implementing code in an unfamiliar area. Analyze the current codebase shape and maintain a living architecture reference.",
        role="architecture-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["repository tree", ".relay-kit/contracts/project-context.md", ".relay-kit/contracts/architecture.md when available"],
        outputs=[".relay-kit/references/project-architecture.md"],
        references=[
            "Document what the codebase actually does today, not what the team intended six months ago.",
            "Include concrete file paths, entrypoints, and dependency direction.",
        ],
        next_steps=["architect", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build and maintain an accurate map of the current architecture so downstream roles stop guessing.

            ## Produce `.relay-kit/references/project-architecture.md`
            Cover:
            - entry points and execution flow
            - layer or package structure
            - module responsibilities
            - dependency direction and boundaries
            - architecture drift and hotspots
            - files to mirror when adding new work

            ## Working rules
            - Prefer observed runtime or code flow over folder names alone.
            - Name boundaries explicitly: controllers, services, repositories, adapters, domain logic, jobs, or scripts.
            - Flag any mismatch between the intended architecture and what the code actually does.
            - Add file paths whenever the reference names a pattern or module.
            """
        ).strip(),
    ),
    "dependency-management": SkillSpec(
        name="dependency-management",
        description="Use when adding packages, updating libraries, or diagnosing environment drift. Capture dependency policy, lockfile usage, environment setup, and safe add-or-upgrade rules.",
        role="build-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["package metadata files", "lockfiles", "toolchain config", "CI setup if present"],
        outputs=[".relay-kit/references/dependency-management.md"],
        references=[
            "Record both the official package manager and what contributors actually use day to day.",
            "Make transitive risk and pinning policy explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Prevent dependency changes from becoming hidden architecture or release risk.

            ## Produce `.relay-kit/references/dependency-management.md`
            Cover:
            - package manager and lockfiles
            - environment and toolchain setup
            - version pinning and upgrade policy
            - dev vs prod dependencies
            - how to add a new dependency
            - known dependency risks

            ## Working rules
            - Name the exact files that define dependencies.
            - Note whether the team uses strict pinning, ranges, extras, or split requirement sets.
            - Explain how contributors should add, upgrade, and verify dependencies without drifting from CI.
            - Flag packages that are security-sensitive, hard to upgrade, or tightly coupled to runtime behavior.
            """
        ).strip(),
    ),
    "api-integration": SkillSpec(
        name="api-integration",
        description="Use when building or changing API clients, webhooks, endpoints, or network-facing code. Document external service integration patterns, clients, auth, retries, and error handling.",
        role="integration-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["HTTP or RPC client code", "settings or secret config", "test or mock code"],
        outputs=[".relay-kit/references/api-integration.md"],
        references=[
            "Prefer concrete service names, client classes, and endpoint groups over generic summaries.",
            "Make retries, timeouts, idempotency, and error translation explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Make network-facing behavior predictable so changes to API code do not become reliability surprises.

            ## Produce `.relay-kit/references/api-integration.md`
            Cover:
            - clients, transports, and endpoints
            - authentication and secret handling
            - retry, timeout, and idempotency rules
            - request and response patterns
            - error mapping and recovery
            - testing and mocking approach

            ## Working rules
            - Name client wrappers, service classes, or endpoint modules directly.
            - Include where auth is injected and how secrets are sourced.
            - Explain how the code handles network failures, partial failures, and upstream rate limits.
            - Note what should be mocked versus tested against a real service.
            """
        ).strip(),
    ),
    "data-persistence": SkillSpec(
        name="data-persistence",
        description="Use when touching schemas, repositories, transactions, caches, or data flows. Document storage topology, models, migrations, caching, and consistency rules.",
        role="persistence-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["model files", "repository or DAO code", "migration files", "cache config if present"],
        outputs=[".relay-kit/references/data-persistence.md"],
        references=[
            "Cover both primary storage and auxiliary state like caches, queues, or object stores when relevant.",
            "Document rollback and migration risks, not only happy-path structure.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Make data changes safer by documenting where state lives, how it moves, and what can go wrong.

            ## Produce `.relay-kit/references/data-persistence.md`
            Cover:
            - stores and connection points
            - schemas, models, and repositories
            - migrations and schema evolution
            - transactions and consistency
            - caching and invalidation
            - data risks and rollback notes

            ## Working rules
            - Name concrete stores and frameworks: Postgres, Redis, SQLite, MongoDB, ORM, query builder, and so on.
            - Explain who owns writes, reads, cache invalidation, and transaction boundaries.
            - Flag destructive migrations, data backfills, and dual-write or consistency hazards.
            - Include file paths for models, repositories, migrations, and seed logic when they exist.
            """
        ).strip(),
    ),
    "testing-patterns": SkillSpec(
        name="testing-patterns",
        description="Use when adding tests, updating fixtures, validating regressions, or deciding what proof is enough. Capture how the project tests code, mocks dependencies, and gathers evidence.",
        role="quality-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["test folders", "test config", "fixtures or factories", "CI or local test commands"],
        outputs=[".relay-kit/references/testing-patterns.md"],
        references=[
            "Explain how to produce evidence locally, not only what frameworks exist.",
            "Map tests to risk areas and brittle zones where regressions cluster.",
        ],
        next_steps=["developer", "qa-governor", "debug-hub", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Turn the project test suite into a usable playbook for implementation and quality review.

            ## Produce `.relay-kit/references/testing-patterns.md`
            Cover:
            - frameworks and folder rules
            - fixture and factory patterns
            - mocking and dependency isolation
            - async or integration testing rules
            - commands for local evidence
            - coverage gaps and brittle areas

            ## Working rules
            - Name the real commands contributors should run for fast confidence versus deeper verification.
            - Show where fixtures, factories, and mocks live and when each should be preferred.
            - Call out unstable tests, heavy integration paths, and areas with weak coverage.
            - Tie recommendations back to risk, not just test quantity.
            """
        ).strip(),
    ),
}
