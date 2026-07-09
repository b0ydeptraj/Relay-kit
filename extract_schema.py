import sys
import yaml
import argparse
import old_cli_safe

captured_parser = None

original_parse_args = argparse.ArgumentParser.parse_args

def mock_parse_args(self, args=None, namespace=None):
    global captured_parser
    captured_parser = self
    sys.exit(0)

argparse.ArgumentParser.parse_args = mock_parse_args

try:
    old_cli_safe.main()
except SystemExit:
    pass

def dump_action(action):
    # Only care about arguments and flags
    if isinstance(action, argparse._HelpAction):
        return None
    if isinstance(action, argparse._SubParsersAction):
        return None
        
    cfg = {}
    if action.help:
        cfg['help'] = action.help
    if action.choices:
        cfg['choices'] = list(action.choices)
    if action.metavar:
        cfg['metavar'] = action.metavar
    if action.default is not argparse.SUPPRESS and action.default is not None and not isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
        # some defaults are functions or complicated, ignore them if they are complex
        if isinstance(action.default, (str, int, float, bool)):
            cfg['default'] = action.default
            
    if getattr(action, 'nargs', None) is not None:
        cfg['nargs'] = action.nargs
        
    if action.type:
        if action.type is int:
            cfg['type'] = 'int'
        elif action.type is float:
            cfg['type'] = 'float'
            
    if isinstance(action, argparse._StoreTrueAction):
        cfg['action'] = 'store_true'
    elif isinstance(action, argparse._StoreFalseAction):
        cfg['action'] = 'store_false'
        
    return cfg

def dump_parser(parser):
    schema = {}
    
    if parser.description:
        schema['help_text'] = parser.description
        
    args = {}
    flags = {}
    
    for action in parser._actions:
        cfg = dump_action(action)
        if not cfg: continue
        
        opts = action.option_strings
        if not opts:
            args[action.dest] = cfg
        else:
            # use the longest option string (e.g. --help)
            opt_name = max(opts, key=len)
            flags[opt_name] = cfg
            if len(opts) > 1:
                # also record short names if they exist, but schema engine maps them?
                # The engine currently just adds the flag_name. We should probably add all opts.
                pass
                
    if args:
        schema['args'] = args
    if flags:
        schema['flags'] = flags
        
    # subcommands
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            subcommands = {}
            for sub_name, sub_parser in action.choices.items():
                subcommands[sub_name] = dump_parser(sub_parser)
            schema['subcommands'] = subcommands
            
    return schema

if captured_parser:
    schema = dump_parser(captured_parser)
    
    # In monolith, the top-level commands are subcommands of the root parser
    commands = schema.get('subcommands', {})
    
    # We must preserve 'handler' fields from the existing command_schema.yaml
    with open('relay_kit_v3/cli/command_schema.yaml', 'r') as f:
        old_schema = yaml.safe_load(f)
        
    def merge_handlers(new_tree, old_tree):
        if 'handler' in old_tree:
            new_tree['handler'] = old_tree['handler']
        if 'subcommands' in new_tree and 'subcommands' in old_tree:
            for k in new_tree['subcommands']:
                if k in old_tree['subcommands']:
                    merge_handlers(new_tree['subcommands'][k], old_tree['subcommands'][k])
                    
    for cmd in commands:
        if cmd in old_schema.get('commands', {}):
            merge_handlers(commands[cmd], old_schema['commands'][cmd])
            
    final_schema = {'commands': commands}
    
    with open('relay_kit_v3/cli/command_schema.yaml', 'w') as f:
        yaml.dump(final_schema, f, sort_keys=False, default_flow_style=False)
    print("Successfully dumped schema!")
else:
    print("Failed to capture parser")
