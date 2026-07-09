import os
import tempfile
import sys
import traceback
from relay_kit_v3.extensions.manager import ExtensionManager
from relay_kit_v3.extensions.quarantine import QuarantineManager, LifecycleState

def test_manager_list_and_remove():
    with tempfile.TemporaryDirectory() as project_dir:
        # Pre-populate quarantine registry
        qm = QuarantineManager(project_dir)
        qm._update_installed_registry("pack1", "active", {"version": "1.0", "skills_count": 2})
        qm._update_installed_registry("pack2", "quarantined", {"version": "2.0", "skills_count": 1})
        
        em = ExtensionManager(project_dir)
        all_exts = em.list_extensions()
        assert len(all_exts) == 2
        
        active_exts = em.list_extensions(LifecycleState.ACTIVE)
        assert len(active_exts) == 1
        assert active_exts[0]["name"] == "pack1"
        
        pack1 = em.inspect_extension("pack1")
        assert pack1 is not None
        assert pack1["state"] == "active"
        
        em.remove_extension("pack1")
        assert len(em.list_extensions()) == 1

if __name__ == "__main__":
    tests = [
        test_manager_list_and_remove
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
