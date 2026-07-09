import os
import tempfile
import yaml
import traceback
import sys
from relay_kit_v3.extensions.installer import ExtensionInstaller

def create_pack(tmpdir, name="test-pack", valid=True, shell=False, routing=True):
    pack_dir = os.path.join(tmpdir, name)
    os.makedirs(pack_dir)
    os.makedirs(os.path.join(pack_dir, 'skills', 'test-skill'))
    
    content = "---\nname: test-skill\ndescription: "
    content += "Use when testing\n---\nBody" if routing else "Just testing\n---\nBody"
    
    with open(os.path.join(pack_dir, 'skills', 'test-skill', 'SKILL.md'), 'w', encoding='utf-8') as f:
        f.write(content)
        
    import hashlib
    h = hashlib.sha256()
    with open(os.path.join(pack_dir, 'skills', 'test-skill', 'SKILL.md'), 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    expected_hash = "sha256:" + h.hexdigest()
    if not valid:
        expected_hash = "sha256:wrong"
        
    pack_data = {
        "name": name,
        "version": "1.0.0",
        "hash": expected_hash,
        "skills": ["test-skill"],
        "permissions": {"shell": shell, "network": False}
    }
    with open(os.path.join(pack_dir, 'pack.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump(pack_data, f)
        
    return pack_dir

def test_install_valid_reviewed():
    with tempfile.TemporaryDirectory() as project_dir:
        installer = ExtensionInstaller(project_dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = create_pack(tmpdir, "my-pack")
            
            res = installer.install(source_dir, user_trust_flag="reviewed")
            assert res.exit_code == 0, f"Expected 0, got {res.exit_code}: {res.message}"
            assert "Successfully installed" in res.message

def test_install_invalid_hash():
    with tempfile.TemporaryDirectory() as project_dir:
        installer = ExtensionInstaller(project_dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = create_pack(tmpdir, "bad-hash", valid=False)
            
            res = installer.install(source_dir, user_trust_flag="reviewed")
            assert res.exit_code == 1
            assert "Hash mismatch" in res.message

def test_install_untrusted_shell():
    with tempfile.TemporaryDirectory() as project_dir:
        installer = ExtensionInstaller(project_dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = create_pack(tmpdir, "shell-pack", shell=True)
            
            res = installer.install(source_dir, user_trust_flag="reviewed")
            assert res.exit_code == 3, f"Expected 3, got {res.exit_code}: {res.message}"
            assert "Permission denied" in res.message

def test_install_gauntlet_fail():
    with tempfile.TemporaryDirectory() as project_dir:
        installer = ExtensionInstaller(project_dir)
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir = create_pack(tmpdir, "bad-routing", routing=False)
            
            res = installer.install(source_dir, user_trust_flag="reviewed")
            assert res.exit_code == 4, f"Expected 4, got {res.exit_code}: {res.message}"
            assert "Gauntlet failed" in res.message

if __name__ == "__main__":
    tests = [
        test_install_valid_reviewed,
        test_install_invalid_hash,
        test_install_untrusted_shell,
        test_install_gauntlet_fail
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
