import argparse
import sys
import uvicorn
from pathlib import Path
import os


def setup_dashboard_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("dashboard", help="Start Relay-Kit Live Dashboard")
    parser.add_argument("project_path", nargs="?", default=".", help="Path to project root")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.set_defaults(func=run_dashboard)


def run_dashboard(args: argparse.Namespace) -> int:
    try:
        import fastapi
    except ImportError:
        print("Error: FastAPI is required for the live dashboard.", file=sys.stderr)
        print("Please install dependencies: pip install fastapi uvicorn", file=sys.stderr)
        return 1
        
    project = Path(args.project_path).resolve()
    if not project.exists():
        print(f"Error: Project path does not exist: {project}", file=sys.stderr)
        return 1

    print(f"Starting Relay-Kit Dashboard for project: {project}")
    print(f"Listening on http://{args.host}:{args.port}")

    # Pass the project root to the FastAPI app via environment variable
    os.environ["RELAY_KIT_PROJECT_ROOT"] = str(project)
    
    uvicorn.run("relay_kit_v3.dashboard.app:app", host=args.host, port=args.port, reload=False)
    
    return 0

