import os
import sys
import tempfile
import yaml
import traceback
from relay_kit_v3.extensions.pack_format import ExtensionPack, PackValidationError

def test_valid_pack():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, 'skills', 'test-skill'))
        
        # Create a dummy skill file
        skill_path = os.path.join(tmpdir, 'skills', 'test-skill', 'SKILL.md')
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write("test content")
            
        import hashlib
        h = hashlib.sha256()
        h.update(b"test content")
        expected_hash = "sha256:" + h.hexdigest()
        
        pack_data = {
            "name": "test-pack",
            "version": "1.0.0",
            "hash": expected_hash,
            "skills": ["test-skill"],
            "permissions": {
                "shell": False,
                "network": False
            }
        }
        
        with open(os.path.join(tmpdir, 'pack.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(pack_data, f)
            
        pack = ExtensionPack(tmpdir)
        assert pack.name == "test-pack"
        assert pack.version == "1.0.0"
        assert pack.skills == ["test-skill"]
        assert pack.permissions.shell_required is False
        assert pack.verify_hash() is True

def test_invalid_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, 'skills', 'test-skill'))
        
        skill_path = os.path.join(tmpdir, 'skills', 'test-skill', 'SKILL.md')
        with open(skill_path, 'w', encoding='utf-8') as f:
            f.write("test content")
            
        pack_data = {
            "name": "test-pack",
            "version": "1.0.0",
            "hash": "sha256:wronghash",
            "skills": ["test-skill"],
            "permissions": {}
        }
        
        with open(os.path.join(tmpdir, 'pack.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(pack_data, f)
            
        pack = ExtensionPack(tmpdir)
        assert pack.verify_hash() is False

def test_missing_pack_yaml():
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            ExtensionPack(tmpdir)
            assert False, "Should have raised PackValidationError"
        except PackValidationError as e:
            assert "pack.yaml not found" in str(e)

def test_invalid_name():
    with tempfile.TemporaryDirectory() as tmpdir:
        pack_data = {
            "name": "Invalid_Name_123!",
            "version": "1.0.0",
            "hash": "sha256:abc",
            "skills": ["test-skill"],
            "permissions": {}
        }
        with open(os.path.join(tmpdir, 'pack.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(pack_data, f)
            
        try:
            ExtensionPack(tmpdir)
            assert False, "Should have raised PackValidationError"
        except PackValidationError as e:
            assert "Name must be non-empty and match" in str(e)

if __name__ == "__main__":
    tests = [
        test_valid_pack,
        test_invalid_hash,
        test_missing_pack_yaml,
        test_invalid_name
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
