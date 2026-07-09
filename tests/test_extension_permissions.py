import traceback
import sys
from relay_kit_v3.extensions.permissions import ExtensionPermissions, validate_permissions

def test_permissions_parsing():
    data = {
        "shell": True,
        "write_paths": [".relay-kit/extensions", "/etc/passwd"],
        "writes_generated_surface": True
    }
    perms = ExtensionPermissions(data)
    assert perms.shell_required is True
    assert perms.network_required is False
    assert len(perms.write_paths) == 2
    assert perms.writes_generated_surface is True

def test_validate_permissions_shell_network():
    data = {"shell": True}
    perms = ExtensionPermissions(data)
    
    # Untrusted + shell -> block
    res1 = validate_permissions(perms, "untrusted")
    assert res1.allowed is False
    assert len(res1.blocked_reasons) == 1
    
    # Reviewed + shell -> block (requires verified)
    res2 = validate_permissions(perms, "reviewed")
    assert res2.allowed is False
    
    # Verified + shell -> allow
    res3 = validate_permissions(perms, "verified")
    assert res3.allowed is True

def test_validate_permissions_paths():
    data = {"write_paths": [".relay-kit/safe", "/tmp/unsafe"]}
    perms = ExtensionPermissions(data)
    
    res = validate_permissions(perms, "verified")
    assert res.allowed is True
    assert len(res.warnings) == 1
    assert "outside .relay-kit/ sandbox" in res.warnings[0]

if __name__ == "__main__":
    tests = [
        test_permissions_parsing,
        test_validate_permissions_shell_network,
        test_validate_permissions_paths
    ]
    failed = False
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            traceback.print_exc()
            failed = True
            
    if failed:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
