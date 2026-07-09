import os
import tempfile
import yaml
import traceback
import sys
from relay_kit_v3.extensions.pack_format import ExtensionPack
from relay_kit_v3.extensions.quarantine import QuarantineManager, LifecycleState

def create_pack(tmpdir, name="test-pack"):
    pack_dir = os.path.join(tmpdir, name)
    os.makedirs(pack_dir)
    os.makedirs(os.path.join(pack_dir, 'skills', 'test-skill'))
    
    with open(os.path.join(pack_dir, 'skills', 'test-skill', 'SKILL.md'), 'w') as f:
        f.write("content")
        
    pack_data = {
        "name": name,
        "version": "1.0.0",
        "hash": "sha256:dummy",
        "skills": ["test-skill"],
        "permissions": {}
    }
    with open(os.path.join(pack_dir, 'pack.yaml'), 'w') as f:
        yaml.dump(pack_data, f)
        
    return pack_dir, ExtensionPack(pack_dir)

def test_quarantine_lifecycle():
    with tempfile.TemporaryDirectory() as project_dir:
        qm = QuarantineManager(project_dir)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir, pack = create_pack(tmpdir, "my-pack")
            
            # Quarantine the pack (gauntlet passed)
            entry = qm.quarantine_pack(source_dir, pack, "reviewed", True)
            assert entry.pack_name == "my-pack"
            assert entry.state == LifecycleState.QUARANTINED
            
            # Check state
            assert qm.get_lifecycle_state("my-pack") == LifecycleState.QUARANTINED
            
            # Promote
            promoted = qm.promote_to_active("my-pack")
            assert promoted is True
            assert qm.get_lifecycle_state("my-pack") == LifecycleState.ACTIVE
            
            # Check list
            all_packs = qm.list_all()
            assert len(all_packs) == 1
            assert all_packs[0].pack_name == "my-pack"
            assert all_packs[0].state == LifecycleState.ACTIVE
            
            # Remove
            removed = qm.remove_pack("my-pack")
            assert removed is True
            assert qm.get_lifecycle_state("my-pack") == LifecycleState.NOT_FOUND

def test_quarantine_blocked():
    with tempfile.TemporaryDirectory() as project_dir:
        qm = QuarantineManager(project_dir)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir, pack = create_pack(tmpdir, "bad-pack")
            
            # Quarantine the pack (gauntlet failed)
            entry = qm.quarantine_pack(source_dir, pack, "reviewed", False)
            assert entry.state == LifecycleState.BLOCKED
            
            # Promote should fail
            promoted = qm.promote_to_active("bad-pack")
            assert promoted is False
            assert qm.get_lifecycle_state("bad-pack") == LifecycleState.BLOCKED

if __name__ == "__main__":
    tests = [
        test_quarantine_lifecycle,
        test_quarantine_blocked
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
