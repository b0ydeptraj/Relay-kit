"""
Test that all commands and handlers in command_schema.yaml exist,
can be resolved, and build valid argument parsers without errors.
"""
import importlib
import pytest
from pathlib import Path
from relay_kit_v3.cli.engine import _load_schema, build_parser, SCHEMA_PATH


def test_command_schema_file_exists():
    assert SCHEMA_PATH.exists(), f"Schema file missing at {SCHEMA_PATH}"


def _collect_handlers(schema_node, current_path=""):
    """Recursively collect all handler strings from schema nodes."""
    handlers = []
    if isinstance(schema_node, dict):
        if "handler" in schema_node and isinstance(schema_node["handler"], str):
            handlers.append((current_path, schema_node["handler"]))
        if "subcommands" in schema_node:
            for sub_name, sub_node in schema_node["subcommands"].items():
                sub_path = f"{current_path}.{sub_name}" if current_path else sub_name
                handlers.extend(_collect_handlers(sub_node, sub_path))
        if "commands" in schema_node:
            for cmd_name, cmd_node in schema_node["commands"].items():
                handlers.extend(_collect_handlers(cmd_node, cmd_name))
    return handlers


def test_all_schema_handlers_are_importable_and_callable():
    schema = _load_schema()
    handlers = _collect_handlers(schema)
    assert len(handlers) > 0, "No handlers found in command_schema.yaml"

    unresolvable = []
    for cmd_path, handler_path in handlers:
        try:
            module_name, func_name = handler_path.rsplit(".", 1)
            mod = importlib.import_module(module_name)
            func = getattr(mod, func_name)
            if not callable(func):
                unresolvable.append((cmd_path, handler_path, "Not callable"))
        except Exception as e:
            unresolvable.append((cmd_path, handler_path, str(e)))

    assert not unresolvable, f"Unresolvable handlers in schema: {unresolvable}"


def test_all_top_level_command_parsers_build_cleanly():
    schema = _load_schema()
    commands = schema.get("commands", {})
    assert len(commands) > 0, "No commands found in schema"

    for cmd_name in commands:
        parser = build_parser(cmd_name, schema)
        assert parser is not None
        # Format help string to verify parser has no structural crashes
        help_text = parser.format_help()
        assert len(help_text) > 0
