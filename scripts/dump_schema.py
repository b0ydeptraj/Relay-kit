import ast
import yaml
import re

parsers = [
    'accessibility', 'manifest', 'eval', 'proof', 'upgrade', 'policy', 
    'support', 'readiness', 'release', 'continuity', 'migration', 
    'publish', 'commercial', 'pulse', 'signal'
]

def parse_cli_to_schema():
    with open('old_cli.py', encoding='utf-8') as f:
        code = f.read()
    
    tree = ast.parse(code)
    schema = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('_parse_'):
            cmd_name = node.name.replace('_parse_', '').replace('_args', '')
            if cmd_name not in parsers:
                continue
            
            help_text = ""
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    if getattr(stmt.value.func, 'attr', '') == 'ArgumentParser':
                        for kw in stmt.value.keywords:
                            if kw.arg == 'description':
                                help_text = kw.value.value
                                break
            
            cmd_schema = {
                'help_text': help_text,
                'subcommands': {}
            }
            
            subcmds_map = {}
            for stmt in ast.iter_child_nodes(node):
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    if getattr(stmt.value.func, 'attr', '') == 'add_parser':
                        if stmt.value.args and isinstance(stmt.value.args[0], ast.Constant):
                            subcmd_name = stmt.value.args[0].value
                            subcmds_map[stmt.targets[0].id] = subcmd_name
                            subhelp = ""
                            for kw in stmt.value.keywords:
                                if kw.arg == 'help':
                                    subhelp = kw.value.value
                            cmd_schema['subcommands'][subcmd_name] = {
                                'handler': f'relay_kit_v3.cli.{cmd_name.replace("-", "_")}.run_{cmd_name.replace("-", "_")}',
                                'help_text': subhelp,
                                'args': {},
                                'flags': {}
                            }
            
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    if getattr(stmt.value.func, 'attr', '') == 'add_argument':
                        var_name = stmt.value.func.value.id
                        if var_name in subcmds_map:
                            subcmd_name = subcmds_map[var_name]
                            
                            arg_name = stmt.value.args[0].value
                            kwargs = {}
                            for kw in stmt.value.keywords:
                                if kw.arg == 'help':
                                    kwargs['help'] = getattr(kw.value, 'value', '')
                                elif kw.arg == 'default':
                                    if isinstance(kw.value, ast.Constant):
                                        kwargs['default'] = kw.value.value
                                    elif hasattr(kw.value, 'elts'):
                                        kwargs['default'] = [getattr(elt, 'value', str(elt)) for elt in kw.value.elts]
                                elif kw.arg == 'metavar':
                                    kwargs['metavar'] = getattr(kw.value, 'value', '')
                                elif kw.arg == 'choices':
                                    if hasattr(kw.value, 'elts'):
                                        kwargs['choices'] = [getattr(elt, 'value', str(elt)) for elt in kw.value.elts]
                                elif kw.arg == 'type':
                                    if getattr(kw.value, 'id', '') == 'int':
                                        kwargs['type'] = 'int'
                                elif kw.arg == 'nargs':
                                    kwargs['nargs'] = getattr(kw.value, 'value', '')
                                elif kw.arg == 'action':
                                    kwargs['action'] = getattr(kw.value, 'value', '')
                                elif kw.arg == 'required':
                                    kwargs['required'] = getattr(kw.value, 'value', True)

                            if arg_name.startswith('--'):
                                cmd_schema['subcommands'][subcmd_name]['flags'][arg_name] = kwargs
                            else:
                                cmd_schema['subcommands'][subcmd_name]['args'][arg_name] = kwargs
            
            for subcmd in cmd_schema['subcommands'].values():
                if not subcmd['args']:
                    del subcmd['args']
                if not subcmd['flags']:
                    del subcmd['flags']
            
            schema[cmd_name] = cmd_schema
            
    with open("generated_schema.yaml", "w", encoding="utf-8") as f:
        yaml.dump(schema, f, sort_keys=False, default_flow_style=False)
        
def generate_modules():
    with open('relay_kit_public_cli.py', encoding='utf-8') as f:
        code = f.read()

    for cmd in parsers:
        cmd_safe = cmd.replace('-', '_')
        pattern = rf"def run_{cmd_safe}\(args: argparse\.Namespace\) -> int:\n(.*?)(?=\ndef [a-zA-Z_]+\(|\Z)"
        match = re.search(pattern, code, re.DOTALL)
        if not match:
            print(f"Could not find run_{cmd_safe}")
            continue
        
        body = match.group(1)
        
        # Imports
        imports = "import argparse\nimport sys\nimport json\nfrom pathlib import Path\n"
        if "_run_script_main" in body:
            imports += "from relay_kit_v3.cli.utils import _run_script_main\n"
        
        content = f"{imports}\n\ndef run_{cmd_safe}(args: argparse.Namespace) -> int:\n{body}"
        with open(f"relay_kit_v3/cli/{cmd_safe}.py", "w", encoding="utf-8") as f:
            f.write(content)
            
if __name__ == '__main__':
    parse_cli_to_schema()
    generate_modules()
    print("Done")
