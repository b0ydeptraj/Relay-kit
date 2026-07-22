import argparse
import importlib
import yaml
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "command_schema.yaml"

def _load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _apply_schema_to_parser(parser: argparse.ArgumentParser, schema: dict, dest_name: str = "action"):
    args_schema = schema.get("args", {})
    remainder_args: list[tuple[str, dict]] = []
    for arg_name, arg_config in args_schema.items():
        kwargs = dict(arg_config)
        if kwargs.get("nargs") == "REMAINDER":
            kwargs["nargs"] = argparse.REMAINDER
            remainder_args.append((arg_name, kwargs))
            continue
        parser.add_argument(arg_name, **kwargs)
        
    flags_schema = schema.get("flags", {})
    for flag_name, flag_config in flags_schema.items():
        kwargs = dict(flag_config)
        if kwargs.get("type") == "int":
            kwargs["type"] = int
        elif kwargs.get("type") == "float":
            kwargs["type"] = float
        if kwargs.get("nargs") == "REMAINDER":
            kwargs["nargs"] = argparse.REMAINDER
        parser.add_argument(flag_name, **kwargs)

    # REMAINDER positionals must be registered after flags so options such as
    # `--json -- <command...>` are parsed by Relay-kit before command capture.
    for arg_name, kwargs in remainder_args:
        parser.add_argument(arg_name, **kwargs)
        
    if "subcommands" in schema:
        subparsers = parser.add_subparsers(dest=dest_name, required=True)
        for sub_name, sub_config in schema["subcommands"].items():
            subparser = subparsers.add_parser(sub_name, help=sub_config.get("help_text", ""))
            # Use action_{sub_name} for nested dest to avoid collision
            _apply_schema_to_parser(subparser, sub_config, dest_name=f"action_{sub_name.replace('-', '_')}")

def build_parser(command_name: str, schema: dict | None = None) -> argparse.ArgumentParser:
    if schema is None:
        schema = _load_schema()
    
    cmd_schema = schema.get("commands", {}).get(command_name)
    if not cmd_schema:
        raise ValueError(f"Command '{command_name}' not found in schema.")
        
    parser = argparse.ArgumentParser(
        prog=f"relay-kit {command_name.replace('.', ' ')}",
        description=cmd_schema.get("help_text", "")
    )
    
    _apply_schema_to_parser(parser, cmd_schema)
        
    return parser

def dispatch(command_name: str, argv: list[str]) -> int:
    schema = _load_schema()
    cmd_schema = schema.get("commands", {}).get(command_name)
    if not cmd_schema:
        raise ValueError(f"Command '{command_name}' not found in schema.")
        
    command_tail: list[str] | None = None
    parse_argv = argv
    if command_name == "shell" and argv[:1] == ["compact"] and "--" in argv:
        separator_index = argv.index("--")
        command_tail = argv[separator_index + 1 :]
        parse_argv = argv[:separator_index]
        shell_parser = argparse.ArgumentParser(prog="relay-kit shell compact")
        shell_parser.add_argument("action")
        shell_parser.add_argument("project_path", nargs="?", default=".")
        shell_parser.add_argument("--cwd", default=None)
        shell_parser.add_argument("--timeout", default=None)
        shell_parser.add_argument("--strict", action="store_true")
        shell_parser.add_argument("--json", action="store_true")
        parsed_args = shell_parser.parse_args(parse_argv)
        setattr(parsed_args, "command", command_tail)
    else:
        parser = build_parser(command_name, schema)
        parsed_args = parser.parse_args(parse_argv)
    
    # Traverse to find the deepest handler
    current_schema = cmd_schema
    handler_path = current_schema.get("handler")
    
    # Find active subcommands dynamically
    # For depth 1: dest is "action", action value is e.g. "active"
    # For depth 2: dest is "action_active", action value is e.g. "set"
    
    action_val = getattr(parsed_args, "action", None)
    if action_val and "subcommands" in current_schema:
        current_schema = current_schema["subcommands"][action_val]
        if current_schema.get("handler"):
            handler_path = current_schema["handler"]
            
        # check for depth 2
        dest2 = f"action_{action_val.replace('-', '_')}"
        action_val2 = getattr(parsed_args, dest2, None)
        if action_val2 and "subcommands" in current_schema:
            current_schema = current_schema["subcommands"][action_val2]
            if current_schema.get("handler"):
                handler_path = current_schema["handler"]
                
    if not handler_path:
        raise ValueError(f"No handler defined for command '{command_name}'.")
        
    module_path, func_name = handler_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    handler = getattr(module, func_name)
    
    return handler(parsed_args)
