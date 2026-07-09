import os
import tempfile
import yaml
from relay_kit_v3.extensions.pack_format import ExtensionPack
from relay_kit_v3.extensions.trust_policy import TrustPolicyEngine, TrustLevel, TrustDecision

def create_dummy_pack(tmpdir, trust_sig=False, author="test-author", shell=False):
    os.makedirs(os.path.join(tmpdir, 'skills', 'test-skill'))
    
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
        "author": author,
        "hash": expected_hash,
        "skills": ["test-skill"],
        "permissions": {
            "shell": shell,
            "network": False
        }
    }
    
    with open(os.path.join(tmpdir, 'pack.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump(pack_data, f)
        
    if trust_sig:
        with open(os.path.join(tmpdir, 'trust.sig'), 'w', encoding='utf-8') as f:
            f.write("dummy-signature")
            
    return ExtensionPack(tmpdir)

def test_trust_levels():
    with tempfile.TemporaryDirectory() as project_dir:
        engine = TrustPolicyEngine(project_dir)
        
        # Untrusted
        with tempfile.TemporaryDirectory() as tmpdir:
            pack = create_dummy_pack(tmpdir)
            assert engine.get_pack_trust_level(pack, "") == TrustLevel.UNTRUSTED
            assert engine.evaluate_trust(pack, "") == TrustDecision.BLOCK
            
        # Reviewed
        with tempfile.TemporaryDirectory() as tmpdir:
            pack = create_dummy_pack(tmpdir)
            assert engine.get_pack_trust_level(pack, "reviewed") == TrustLevel.REVIEWED
            assert engine.evaluate_trust(pack, "reviewed") == TrustDecision.ALLOW
            
        # Verified
        with tempfile.TemporaryDirectory() as tmpdir:
            pack = create_dummy_pack(tmpdir, trust_sig=True)
            assert engine.get_pack_trust_level(pack, "") == TrustLevel.VERIFIED
            assert engine.evaluate_trust(pack, "") == TrustDecision.ALLOW

def test_permissions_check():
    with tempfile.TemporaryDirectory() as project_dir:
        engine = TrustPolicyEngine(project_dir)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Shell = true
            pack = create_dummy_pack(tmpdir, shell=True)
            
            # Untrusted -> should be blocked by permissions anyway
            assert engine.check_trust_for_permissions(TrustLevel.UNTRUSTED, pack.permissions) is False
            
            # Reviewed -> blocked because require_signature_for_shell=True
            assert engine.check_trust_for_permissions(TrustLevel.REVIEWED, pack.permissions) is False
            
            # Verified -> Allowed
            assert engine.check_trust_for_permissions(TrustLevel.VERIFIED, pack.permissions) is True

if __name__ == "__main__":
    import sys
    import traceback
    tests = [
        test_trust_levels,
        test_permissions_check
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
