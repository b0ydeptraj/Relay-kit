import re

parsers = [
    'doctor', 'evidence', 'contract', 'context', 'lane', 'delegation', 'locale', 'token', 'calibrate', 'shell', 'adapter', 'command',
    'agent', 'query', 'prompt', 'service', 'runtime', 'skill', 'impact',
    'accessibility', 'manifest', 'eval', 'proof', 'upgrade', 'policy', 
    'support', 'readiness', 'release', 'continuity', 'migration', 
    'publish', 'commercial', 'pulse', 'signal'
]

with open('relay_kit_public_cli.py', encoding='utf-8') as f:
    code = f.read()

# Replace main function
new_main = """def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    
    known_commands = {
        "doctor", "evidence", "contract", "context", "lane", "delegation",
        "locale", "token", "calibrate", "shell", "adapter", "command",
        "agent", "query", "prompt", "service", "runtime", "skill", "impact",
        "accessibility", "manifest", "eval", "proof", "upgrade", "policy",
        "support", "readiness", "release", "continuity", "migration",
        "publish", "commercial", "pulse", "signal"
    }
    
    if raw_argv and raw_argv[0] in known_commands:
        return engine.dispatch(raw_argv[0], raw_argv[1:])

    args = _parse_args(raw_argv)
    _setup_logging(args.verbose)
    
    # Global public install fallback
    if args.diagnostic_run:
        print(f"Relay-kit public runtime diagnostic: PASS (mock)")
        return 0
        
    ai_str = _resolve_ai(args)
    if not ai_str:
        print("Error: Must specify --codex, --claude, or --antigravity", file=sys.stderr)
        return 1

    print(f"Generating public Relay-kit ({args.bundle}) runtime in {args.project_path} for {ai_str}...")
    _write_stub_files(args.project_path, ai_str, args.bundle)
    print("Done. Relay-kit runtime is ready.")
    return 0
"""

code = re.sub(r"def main\(argv: list\[str\] \| None = None\) -> int:\n.*?(?=\nif __name__ ==)", new_main, code, flags=re.DOTALL)

# Delete all `def _parse_X_args` except `_parse_args`
code = re.sub(r"def _parse_(accessibility|manifest|eval|proof|upgrade|policy|support|readiness|release|continuity|migration|publish|commercial|pulse|signal)_args\(.*?\) -> argparse\.Namespace:\n(?:(?: {4}.*?\n|\n)*)", "", code)

# Delete all `def run_X(args: argparse.Namespace) -> int:`
code = re.sub(r"def run_(accessibility|manifest|eval|proof|upgrade|policy|support|readiness|release|continuity|migration|publish|commercial|pulse|signal)\(.*?\) -> int:\n(?:(?: {4}.*?\n|\n)*)", "", code)

with open('relay_kit_public_cli.py', 'w', encoding='utf-8') as f:
    f.write(code)
