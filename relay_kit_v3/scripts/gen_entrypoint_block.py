"""
Generate PUBLIC_ENTRYPOINT_SKILLS block for 8 remaining skills
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = ["brainstorm","build-it","debug-systematically","prove-it","ready-check","review-pr","start-here","write-steps"]


def parse_list_section(content, header):
    items = []
    in_sec = False
    for line in content.split("\n"):
        if header in line:
            in_sec = True
            continue
        if in_sec and line.startswith("- "):
            items.append(line[2:].strip())
        elif in_sec and line.startswith("#"):
            break
    return items


def parse_body(content):
    parts = content.split("---")
    if len(parts) >= 3:
        body_rest = "---".join(parts[2:])
        role_idx = body_rest.find("## Role")
        if role_idx > 0:
            return body_rest[:role_idx].strip()
    return ""


entries = []
for s in SKILLS:
    p = REPO / ".agent" / "skills" / s / "SKILL.md"
    content = p.read_text(encoding="utf-8")

    m = re.search(r"description:\s*(.+)", content)
    desc = m.group(1).strip() if m else ""

    m2 = re.search(r"## Role\s*\n- (.+)", content)
    role = m2.group(1).strip() if m2 else "specialist"

    m3 = re.search(r"## Layer\s*\n- (.+)", content)
    layer = m3.group(1).strip() if m3 else "layer-4-specialists-and-standalones"

    inputs = parse_list_section(content, "## Inputs")
    outputs = parse_list_section(content, "## Outputs")
    references = parse_list_section(content, "## Reference skills and rules")
    next_steps = parse_list_section(content, "## Likely next step")
    body = parse_body(content)

    entry = f"""    "{s}": SkillSpec(
        name="{s}",
        description={repr(desc)},
        role="{role}",
        layer="{layer}",
        inputs={repr(inputs)},
        outputs={repr(outputs)},
        references={repr(references)},
        next_steps={repr(next_steps)},
        body=dedent(
            \"\"\"\\
{body}
            \"\"\"
        ).strip(),
    ),"""
    entries.append(entry)

block = "\n\nPUBLIC_ENTRYPOINT_SKILLS: Dict[str, SkillSpec] = {\n" + "\n".join(entries) + "\n}\n"
out = REPO / "scripts" / "entrypoint_block.py"
out.write_text(block, encoding="utf-8")
print(f"Done: {len(SKILLS)} entries, {block.count(chr(10))} lines -> {out}")
