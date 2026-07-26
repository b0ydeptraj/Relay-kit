"""
Read 23 offensive SKILL.md files and generate the Python dict entries 
for relay_kit_v3/registry/skills.py -> OFFENSIVE_TOOL_PACK_SKILLS
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SKILLS = [
    "advanced-python-engineering","antibot-challenge-solving","attack-chain-orchestration",
    "binary-reverse-methodology","binary-stealth-obfuscation","browser-fingerprint-engineering",
    "cpp-systems-engineering","desktop-imgui-development","desktop-python-ui",
    "edr-evasion-tactics","field-journal-evolution","frontend-crypto-reverse",
    "malware-analysis-workflows","mmo-llm-automation","mmo-onchain-security-audit",
    "mobile-app-reverse","network-stealth-c2","offensive-security-engagement",
    "process-injection-techniques","protocol-fingerprint-spoofing","telemetry-blinding",
    "terminal-operator-ui","windows-native-internals",
]

def parse_skill(name):
    p = REPO / ".agent" / "skills" / name / "SKILL.md"
    content = p.read_text(encoding="utf-8")
    
    # Description
    m = re.search(r'description:\s*(.+)', content)
    desc = m.group(1).strip() if m else ""
    
    # Role
    m = re.search(r'## Role\s*\n- (.+)', content)
    role = m.group(1).strip() if m else "specialist"
    
    # Layer
    m = re.search(r'## Layer\s*\n- (.+)', content)
    layer = m.group(1).strip() if m else "layer-4-specialists-and-standalones"
    
    # allowed-tools
    m = re.search(r'allowed-tools:\s*\[(.+)\]', content)
    allowed_tools = None
    if m:
        allowed_tools = [t.strip().strip('"').strip("'") for t in m.group(1).split(",")]
    
    # Body (between --- and ## Role)
    parts = content.split("---")
    if len(parts) >= 3:
        body_and_rest = "---".join(parts[2:])
        # Everything before ## Role
        role_idx = body_and_rest.find("## Role")
        if role_idx > 0:
            body = body_and_rest[:role_idx].strip()
        else:
            body = body_and_rest.strip()
    else:
        body = ""
    
    # Inputs
    inputs = []
    in_section = False
    for line in content.split('\n'):
        if '## Inputs' in line:
            in_section = True
            continue
        if in_section and line.startswith('- '):
            inputs.append(line[2:].strip())
        elif in_section and line.startswith('#'):
            break
    
    # Outputs
    outputs = []
    in_section = False
    for line in content.split('\n'):
        if '## Outputs' in line:
            in_section = True
            continue
        if in_section and line.startswith('- '):
            outputs.append(line[2:].strip())
        elif in_section and line.startswith('#'):
            break
    
    # References
    references = []
    in_section = False
    for line in content.split('\n'):
        if '## Reference skills and rules' in line:
            in_section = True
            continue
        if in_section and line.startswith('- '):
            references.append(line[2:].strip())
        elif in_section and line.startswith('#'):
            break
    
    # Next steps
    next_steps = []
    in_section = False
    for line in content.split('\n'):
        if '## Likely next step' in line:
            in_section = True
            continue
        if in_section and line.startswith('- '):
            next_steps.append(line[2:].strip())
        elif in_section and line.startswith('#'):
            break
    
    return {
        "name": name,
        "desc": desc,
        "role": role,
        "layer": layer,
        "body": body,
        "inputs": inputs,
        "outputs": outputs,
        "references": references,
        "next_steps": next_steps,
        "allowed_tools": allowed_tools,
    }


def escape(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def gen_entry(data):
    name = data["name"]
    lines = []
    lines.append(f'    "{name}": SkillSpec(')
    lines.append(f'        name="{name}",')
    lines.append(f'        description="{escape(data["desc"])}",')
    lines.append(f'        role="{data["role"]}",')
    lines.append(f'        layer="{data["layer"]}",')
    
    # inputs
    lines.append(f'        inputs=[')
    for inp in data["inputs"]:
        lines.append(f'            "{escape(inp)}",')
    lines.append(f'        ],')
    
    # outputs
    lines.append(f'        outputs=[')
    for out in data["outputs"]:
        lines.append(f'            "{escape(out)}",')
    lines.append(f'        ],')
    
    # references
    lines.append(f'        references=[')
    for ref in data["references"]:
        lines.append(f'            "{escape(ref)}",')
    lines.append(f'        ],')
    
    # next_steps
    lines.append(f'        next_steps=[')
    for ns in data["next_steps"]:
        lines.append(f'            "{escape(ns)}",')
    lines.append(f'        ],')
    
    # body
    body_escaped = data["body"].replace('\\', '\\\\').replace('"', '\\"')
    body_lines = body_escaped.split('\n')
    lines.append('        body=dedent(')
    lines.append('            """\\')
    for bl in body_lines:
        lines.append(f'            {bl}')
    lines.append('            """')
    lines.append('        ).strip(),')
    
    if data["allowed_tools"]:
        tools_str = ", ".join(f'"{t}"' for t in data["allowed_tools"])
        lines.append(f'        allowed_tools=[{tools_str}],')
    
    lines.append(f'    ),')
    return '\n'.join(lines)


# Generate
all_entries = []
for skill_name in SKILLS:
    data = parse_skill(skill_name)
    all_entries.append(gen_entry(data))

output = f'''
OFFENSIVE_TOOL_PACK_SKILLS: Dict[str, SkillSpec] = {{
{chr(10).join(all_entries)}
}}
'''

# Write to a temp file for review
out_path = REPO / "scripts" / "offensive_registry_block.py"
out_path.write_text(output, encoding="utf-8")
print(f"Generated {len(SKILLS)} entries -> {out_path}")
print(f"Total lines: {output.count(chr(10))}")
