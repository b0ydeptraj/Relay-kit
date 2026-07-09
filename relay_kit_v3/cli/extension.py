import sys
from relay_kit_v3.extensions.installer import ExtensionInstaller
from relay_kit_v3.extensions.manager import ExtensionManager

def cmd_install(args):
    installer = ExtensionInstaller()
    trust_flag = "reviewed" if getattr(args, "reviewed", False) else ""
    result = installer.install(args.path, trust_flag)
    
    print(result.message)
    sys.exit(result.exit_code)

def cmd_list(args):
    manager = ExtensionManager()
    exts = manager.list_extensions()
    
    if not exts:
        print("No extensions found.")
        sys.exit(0)
        
    print(f"{'NAME':<20} | {'STATE':<12} | {'VERSION':<8} | {'SKILLS'}")
    print("-" * 55)
    for ext in exts:
        print(f"{ext['name']:<20} | {ext['state']:<12} | {ext['version']:<8} | {ext['skills_count']}")
    sys.exit(0)

def cmd_remove(args):
    manager = ExtensionManager()
    if manager.remove_extension(args.name):
        print(f"Successfully removed extension '{args.name}'")
        sys.exit(0)
    else:
        print(f"Extension '{args.name}' not found")
        sys.exit(1)
