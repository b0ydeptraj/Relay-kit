import yaml
import importlib

with open('relay_kit_v3/cli/command_schema.yaml', 'r') as f:
    schema = yaml.safe_load(f)

# 1. Fix missing handlers
for cmd_name, cmd_data in schema['commands'].items():
    mod_name = cmd_name.replace('-', '_')
    try:
        mod = importlib.import_module(f'relay_kit_v3.cli.{mod_name}')
    except Exception:
        continue
    
    if 'subcommands' not in cmd_data:
        if hasattr(mod, f'run_{mod_name}'):
            cmd_data['handler'] = f'relay_kit_v3.cli.{mod_name}.run_{mod_name}'
    else:
        for sub_name, sub_data in cmd_data['subcommands'].items():
            sub_mod_name = sub_name.replace('-', '_')
            if hasattr(mod, f'run_{mod_name}_{sub_mod_name}'):
                sub_data['handler'] = f'relay_kit_v3.cli.{mod_name}.run_{mod_name}_{sub_mod_name}'
            elif hasattr(mod, f'run_{mod_name}'):
                sub_data['handler'] = f'relay_kit_v3.cli.{mod_name}.run_{mod_name}'

# 2. Fix context active set/show
ctx_cmds = schema['commands']['context']['subcommands']
if 'set' in ctx_cmds and 'show' in ctx_cmds:
    set_cmd = ctx_cmds.pop('set')
    show_cmd = ctx_cmds.pop('show')
    if 'subcommands' not in ctx_cmds['active']:
        ctx_cmds['active']['subcommands'] = {}
    ctx_cmds['active']['subcommands']['set'] = set_cmd
    ctx_cmds['active']['subcommands']['show'] = show_cmd

# 3. Fix policy list
if 'list' not in schema['commands']['policy']['subcommands']:
    schema['commands']['policy']['subcommands']['list'] = {
        'handler': 'relay_kit_v3.cli.policy.run_policy',
        'help_text': 'List available policy packs'
    }

# 4. Fix policy-pack choices
schema['commands']['doctor']['flags']['--policy-pack']['choices'] = ['baseline', 'enterprise', 'team']
schema['commands']['policy']['subcommands']['check']['flags']['--pack']['choices'] = ['baseline', 'enterprise', 'team']
schema['commands']['support']['subcommands']['bundle']['flags']['--policy-pack']['choices'] = ['baseline', 'enterprise', 'team']

# 5. Fix support request severity choices
schema['commands']['support']['subcommands']['request']['flags']['--severity']['choices'] = ['P0', 'P1', 'P2', 'P3']

with open('relay_kit_v3/cli/command_schema.yaml', 'w') as f:
    yaml.dump(schema, f, sort_keys=False, default_flow_style=False)
