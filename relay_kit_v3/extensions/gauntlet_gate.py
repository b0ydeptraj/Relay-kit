import os
import re
import yaml
from typing import List
from relay_kit_v3.extensions.pack_format import ExtensionPack

class CheckResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

class GauntletResult:
    def __init__(self, passed: bool, checks: List[CheckResult], failed_skills: List[str]):
        self.passed = passed
        self.checks = checks
        self.failed_skills = failed_skills

def run_skill_gauntlet(pack: ExtensionPack, project_path: str = ".") -> GauntletResult:
    checks = []
    failed_skills = set()
    
    # Pre-load existing skills manifest to check for collisions
    manifest_path = os.path.join(project_path, "skills.manifest.yaml")
    existing_skills = set()
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = yaml.safe_load(f)
                if manifest_data and "skills" in manifest_data:
                    existing_skills = {s.get("name") for s in manifest_data["skills"] if isinstance(s, dict) and "name" in s}
        except Exception:
            pass

    for skill_name in pack.skills:
        # 1. Naming Guard
        if not re.match(r"^[a-z0-9-]+$", skill_name):
            checks.append(CheckResult(f"{skill_name} - Naming Guard", False, "Skill name must match [a-z0-9-]+"))
            failed_skills.add(skill_name)
            continue
            
        skill_dir = os.path.join(pack.skills_dir, skill_name)
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md_path):
            checks.append(CheckResult(f"{skill_name} - Naming Guard", False, "Missing SKILL.md"))
            failed_skills.add(skill_name)
            continue
        checks.append(CheckResult(f"{skill_name} - Naming Guard", True))
        
        # 2. SKILL.md Structure
        try:
            with open(skill_md_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            parts = content.split("---")
            if len(parts) < 3 or not content.strip().startswith("---"):
                checks.append(CheckResult(f"{skill_name} - Structure", False, "Missing YAML frontmatter (---)"))
                failed_skills.add(skill_name)
                continue
                
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                checks.append(CheckResult(f"{skill_name} - Structure", False, "Frontmatter must be a valid YAML dictionary"))
                failed_skills.add(skill_name)
                continue
                
            if "name" not in frontmatter or "description" not in frontmatter:
                checks.append(CheckResult(f"{skill_name} - Structure", False, "Frontmatter missing 'name' or 'description'"))
                failed_skills.add(skill_name)
                continue
                
            checks.append(CheckResult(f"{skill_name} - Structure", True))
            
            # 4. Routing Contract (Use when)
            description = frontmatter.get("description", "").strip()
            if not description.startswith("Use when"):
                checks.append(CheckResult(f"{skill_name} - Routing Contract", False, "Description must start with 'Use when'"))
                failed_skills.add(skill_name)
                continue
            checks.append(CheckResult(f"{skill_name} - Routing Contract", True))
            
        except Exception as e:
            checks.append(CheckResult(f"{skill_name} - Structure", False, f"Failed to parse SKILL.md: {e}"))
            failed_skills.add(skill_name)
            continue
            
        # 3. Manifest Collision
        if skill_name in existing_skills:
            checks.append(CheckResult(f"{skill_name} - Collision Check", False, f"Skill '{skill_name}' already exists in skills.manifest.yaml"))
            failed_skills.add(skill_name)
            continue
        checks.append(CheckResult(f"{skill_name} - Collision Check", True))
        
    return GauntletResult(
        passed=len(failed_skills) == 0,
        checks=checks,
        failed_skills=list(failed_skills)
    )
