import argparse
import json
from relay_kit_v3.intent_enhancer import build_prompt_enhancement, render_prompt_enhancement, write_prompt_enhancement

def run_prompt(args: argparse.Namespace) -> int:
    if getattr(args, "action", None) == "enhance":
        return run_prompt_enhance(args)
    return 2

def run_prompt_enhance(args: argparse.Namespace) -> int:
    report = build_prompt_enhancement(
        args.project_path,
        prompt=args.prompt,
        top_limit=args.top_limit,
    )
    output_path = None
    if getattr(args, "output_file", None):
        output_path = write_prompt_enhancement(args.project_path, report, args.output_file)
    if getattr(args, "json", False):
        payload = dict(report)
        if output_path is not None:
            payload["output_file"] = str(output_path)
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_prompt_enhancement(report))
        if output_path is not None:
            print(f"Wrote {output_path}")
    return 0
