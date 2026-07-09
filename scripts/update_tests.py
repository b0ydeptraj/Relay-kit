import re

cmds = [
    'accessibility', 'manifest', 'eval', 'proof', 'upgrade', 'policy', 
    'support', 'readiness', 'release', 'continuity', 'migration', 
    'publish', 'commercial', 'pulse', 'signal'
]

subcmds = {
    'accessibility': ['review'],
    'manifest': ['write', 'stamp', 'verify'],
    'eval': ['run', 'real-world', 'skill-battle', 'competency-battle', 'skill-weakness-report', 'battle-audit', 'battle-benchmark', 'repo-profile', 'domain-pack'],
    'proof': ['audit'],
    'upgrade': ['check', 'plan', 'mark-current'],
    'policy': ['check'],
    'support': ['bundle', 'request', 'triage', 'soak'],
    'readiness': ['check'],
    'release': ['verify', 'readiness'],
    'continuity': ['checkpoint', 'rehydrate', 'handoff', 'diff-since-last'],
    'migration': ['guard'],
    'publish': ['plan', 'evidence', 'trail', 'index-check', 'status'],
    'commercial': ['dossier'],
    'pulse': ['build'],
    'signal': ['export']
}

with open("tests/test_cli_compat.py", "r", encoding="utf-8") as f:
    code = f.read()

funcs = ""
calls = ""

for cmd in cmds:
    func_name = f"test_{cmd.replace('-', '_')}_help_compat"
    if func_name not in code:
        funcs += f"\ndef {func_name}():\n    passed = True\n"
        funcs += f'    passed = passed and check_help_compat(["{cmd}"], "{cmd}")\n'
        for sub in subcmds[cmd]:
            funcs += f'    passed = passed and check_help_compat(["{cmd}", "{sub}"], "{cmd}_{sub}")\n'
        funcs += "    return passed\n"
        calls += f"    passed = passed and {func_name}()\n"

if funcs:
    code = code.replace('if __name__ == "__main__":', funcs + '\nif __name__ == "__main__":')
    code = code.replace('sys.exit(0 if passed else 1)', calls + '    sys.exit(0 if passed else 1)')

with open("tests/test_cli_compat.py", "w", encoding="utf-8") as f:
    f.write(code)
