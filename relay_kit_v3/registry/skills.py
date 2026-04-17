from __future__ import annotations

from typing import Dict

from .skill_models import SkillSpec, render_skill
from .skills_cleanup import CLEANUP_SKILLS
from .skills_disciplines import BASELINE_DISCIPLINE_SKILLS, DISCIPLINE_UTILITY_SKILLS
from .skills_hubs import WORKFLOW_HUB_SKILLS
from .skills_legacy import LEGACY_ROLE_MAP
from .skills_native_support import NATIVE_SUPPORT_SKILLS
from .skills_orchestrators import ORCHESTRATOR_SKILLS
from .skills_roles import ROLE_SKILLS
from .skills_utilities import UTILITY_PROVIDER_SKILLS


ROUND2_CORE_ORDER = [
    "workflow-router",
    "analyst",
    "pm",
    "architect",
    "scrum-master",
    "qa-governor",
]

CORE_SKILLS: Dict[str, SkillSpec] = {
    name: (ORCHESTRATOR_SKILLS | ROLE_SKILLS)[name] for name in ROUND2_CORE_ORDER
}

ALL_V3_SKILLS: Dict[str, SkillSpec] = {}
ALL_V3_SKILLS.update(ORCHESTRATOR_SKILLS)
ALL_V3_SKILLS.update(WORKFLOW_HUB_SKILLS)
ALL_V3_SKILLS.update(ROLE_SKILLS)
ALL_V3_SKILLS.update(UTILITY_PROVIDER_SKILLS)
ALL_V3_SKILLS.update(DISCIPLINE_UTILITY_SKILLS)
ALL_V3_SKILLS.update(CLEANUP_SKILLS)
ALL_V3_SKILLS.update(NATIVE_SUPPORT_SKILLS)
