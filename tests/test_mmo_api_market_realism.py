from __future__ import annotations

from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill


MMO_MARKET_REALISM_TERMS = {
    "mmo-reup-automation": [
        "source inventory",
        "bulk action",
        "publish queue",
        "reject drawer",
        "evidence timeline",
    ],
    "mmo-account-operations": [
        "profile table",
        "proxy binding",
        "health score",
        "cooldown",
        "quarantine",
    ],
    "mmo-browser-fleet-automation": [
        "profile-to-proxy affinity",
        "session lease",
        "live debug",
        "screenshot",
        "console logs",
    ],
    "mmo-social-marketing-automation": [
        "campaign workspace",
        "content calendar",
        "approval lane",
        "quota meter",
        "reject reason",
    ],
    "mmo-lowcode-automation": [
        "node graph",
        "execution list",
        "manual execution",
        "production execution",
        "redacted execution",
    ],
    "mmo-mobile-app-automation": [
        "device inventory",
        "hub",
        "provider",
        "lease owner",
        "logcat",
    ],
    "mmo-cloud-operations-automation": [
        "worker pool",
        "queue dashboard",
        "stalled",
        "dead-letter",
        "pause",
    ],
    "mmo-http-api-automation": [
        "endpoint catalog",
        "request ledger",
        "status code",
        "retry count",
        "idempotency key",
    ],
}


FORBIDDEN_OPERATOR_UI_SMELLS = [
    "hero layout",
    "landing page",
    "beautiful dashboard",
    "generic crud",
    "aesthetic-first",
    "animated cards",
    "textbook architecture",
]


def test_mmo_skills_include_real_operator_workflow_terms() -> None:
    missing_by_skill: dict[str, list[str]] = {}
    for skill_name, required_terms in MMO_MARKET_REALISM_TERMS.items():
        rendered = render_skill(ALL_V3_SKILLS[skill_name]).lower()
        missing = [term for term in required_terms if term.lower() not in rendered]
        if missing:
            missing_by_skill[skill_name] = missing

    assert missing_by_skill == {}


def test_mmo_skills_avoid_fake_dashboard_language() -> None:
    offenders: dict[str, list[str]] = {}
    for skill_name in MMO_MARKET_REALISM_TERMS:
        rendered = render_skill(ALL_V3_SKILLS[skill_name]).lower()
        phrases = [phrase for phrase in FORBIDDEN_OPERATOR_UI_SMELLS if phrase in rendered]
        if phrases:
            offenders[skill_name] = phrases

    assert offenders == {}


def test_research_note_keeps_public_source_and_safety_boundary() -> None:
    note = Path("docs/relay-kit-mmo-api-realism-research.md").read_text(encoding="utf-8").lower()

    for term in [
        "gologin",
        "browserless",
        "pinchtab",
        "apify",
        "crawlee",
        "n8n",
        "bullmq",
        "scrapfly",
        "gads",
        "safety boundary",
    ]:
        assert term in note
