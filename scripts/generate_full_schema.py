import ast
import yaml

with open('original_cli.py', encoding='utf-8') as f:
    code = f.read()

tree = ast.parse(code)
schema = {'commands': {}}

# we want to extract every function that starts with _parse_
# and add it to the schema

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name.startswith('_parse_') and not node.name == '_parse_args':
        cmd_name = node.name.replace('_parse_', '').replace('_args', '')
        
        help_text = ''
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                if getattr(stmt.value.func, 'attr', '') == 'ArgumentParser':
                    for kw in stmt.value.keywords:
                        if kw.arg == 'description':
                            help_text = getattr(kw.value, 'value', '')
                            break
        
        cmd_schema = {
            'handler': f'relay_kit_v3.cli.{cmd_name.replace("-", "_")}.run_{cmd_name.replace("-", "_")}',
            'help_text': help_text,
            'args': {},
            'flags': {}
        }
        
        subcmds_map = {}
        for stmt in ast.iter_child_nodes(node):
            if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                if getattr(stmt.value.func, 'attr', '') == 'add_parser':
                    if stmt.value.args and isinstance(stmt.value.args[0], ast.Constant):
                        subcmd_name = stmt.value.args[0].value
                        subcmds_map[stmt.targets[0].id] = subcmd_name
                        subhelp = ''
                        for kw in stmt.value.keywords:
                            if kw.arg == 'help':
                                subhelp = getattr(kw.value, 'value', '')
                        if 'subcommands' not in cmd_schema:
                            cmd_schema['subcommands'] = {}
                        cmd_schema['subcommands'][subcmd_name] = {
                            'handler': f'relay_kit_v3.cli.{cmd_name.replace("-", "_")}.run_{cmd_name.replace("-", "_")}',
                            'help_text': subhelp,
                            'args': {},
                            'flags': {}
                        }
        
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if getattr(stmt.value.func, 'attr', '') == 'add_argument':
                    var_name = getattr(stmt.value.func.value, 'id', '')
                    target_dict = None
                    if var_name in subcmds_map:
                        subcmd_name = subcmds_map[var_name]
                        target_dict = cmd_schema['subcommands'][subcmd_name]
                    elif var_name == 'parser':
                        target_dict = cmd_schema
                        
                    if target_dict is not None:
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
                            elif kw.arg == 'choices':
                                if hasattr(kw.value, 'elts'):
                                    kwargs['choices'] = [getattr(elt, 'value', str(elt)) for elt in kw.value.elts]
                            elif kw.arg == 'metavar':
                                kwargs['metavar'] = getattr(kw.value, 'value', '')
                            elif kw.arg == 'type':
                                if getattr(kw.value, 'id', '') == 'int':
                                    kwargs['type'] = 'int'
                            elif kw.arg == 'nargs':
                                kwargs['nargs'] = getattr(kw.value, 'value', '')
                            elif kw.arg == 'action':
                                kwargs['action'] = getattr(kw.value, 'value', '')
                            elif kw.arg == 'dest':
                                kwargs['dest'] = getattr(kw.value, 'value', '')
                            elif kw.arg == 'required':
                                kwargs['required'] = getattr(kw.value, 'value', True)

                        if arg_name.startswith('--'):
                            if 'flags' not in target_dict: target_dict['flags'] = {}
                            target_dict['flags'][arg_name] = kwargs
                        else:
                            if 'args' not in target_dict: target_dict['args'] = {}
                            target_dict['args'][arg_name] = kwargs
        
        if not cmd_schema.get('args'): cmd_schema.pop('args', None)
        if not cmd_schema.get('flags'): cmd_schema.pop('flags', None)
        if not cmd_schema.get('subcommands'): cmd_schema.pop('subcommands', None)
        
        if 'subcommands' in cmd_schema:
            for subcmd in list(cmd_schema['subcommands'].values()):
                if not subcmd.get('args'): subcmd.pop('args', None)
                if not subcmd.get('flags'): subcmd.pop('flags', None)
        
        schema['commands'][cmd_name] = cmd_schema

with open('relay_kit_v3/cli/command_schema.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(schema, f, sort_keys=False, default_flow_style=False)
print('Successfully generated full schema!')
