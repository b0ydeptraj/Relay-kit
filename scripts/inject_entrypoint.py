"""
Inject PUBLIC_ENTRYPOINT_SKILLS into skills.py and register into ALL_V3_SKILLS
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
skills_path = REPO / "relay_kit_v3" / "registry" / "skills.py"
block_path = REPO / "scripts" / "entrypoint_block.py"

block = block_path.read_text(encoding="utf-8")
content = skills_path.read_text(encoding="utf-8")

if "PUBLIC_ENTRYPOINT_SKILLS" in content:
    print("Already injected PUBLIC_ENTRYPOINT_SKILLS, skipping.")
else:
    # Insert before ALL_V3_SKILLS: Dict[str, SkillSpec] = {}
    INSERT_BEFORE = "ALL_V3_SKILLS: Dict[str, SkillSpec] = {}"
    if INSERT_BEFORE in content:
        new_content = content.replace(
            INSERT_BEFORE,
            block.strip() + "\n\n\n" + INSERT_BEFORE
        )
        skills_path.write_text(new_content, encoding="utf-8")
        print("Injected PUBLIC_ENTRYPOINT_SKILLS block OK")
    else:
        print("ERROR: insert point not found")

# Now add to ALL_V3_SKILLS if not there
content2 = skills_path.read_text(encoding="utf-8")
OLD = "ALL_V3_SKILLS.update(OFFENSIVE_TOOL_PACK_SKILLS)"
NEW = "ALL_V3_SKILLS.update(OFFENSIVE_TOOL_PACK_SKILLS)\nALL_V3_SKILLS.update(PUBLIC_ENTRYPOINT_SKILLS)"
if "PUBLIC_ENTRYPOINT_SKILLS" in content2 and NEW not in content2 and OLD in content2:
    content3 = content2.replace(OLD, NEW)
    skills_path.write_text(content3, encoding="utf-8")
    print("Added PUBLIC_ENTRYPOINT_SKILLS to ALL_V3_SKILLS.update chain OK")
else:
    print("Update chain already present or error.")
