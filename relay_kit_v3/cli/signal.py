import argparse
import sys
import json
from pathlib import Path


def run_signal(args: argparse.Namespace) -> int:
    if args.action != "export":
        return 2
    payload = build_signal_export(
        args.project_path,
        pulse_file=args.pulse_file,
        event_limit=args.event_limit,
    )
    outputs = write_signal_export(args.project_path, payload, output_dir=args.output_dir, include_otlp=args.otlp)
    if args.json:
        print(
            json.dumps(
                {
                    "outputs": {name: str(path) for name, path in outputs.items()},
                    "export": payload,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
    else:
        print(f"Wrote {outputs['json']}")
        print(f"Wrote {outputs['jsonl']}")
        if "otlp" in outputs:
            print(f"Wrote {outputs['otlp']}")
        print(f"Signals: {payload['summary']['signal_count']}")
    return 0

