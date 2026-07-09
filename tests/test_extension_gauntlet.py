import os
import tempfile
import yaml
import traceback
import sys
from relay_kit_v3.extensions.pack_format import ExtensionPack
from relay_kit_v3.extensions.gauntlet_gate import run_skill_gauntlet

def create_skill_pack(tmpdir, skills_data, manifest_skills=None):
    pack_data = {
        "name": "test-pack",
        "version": "1.0.0",
        "hash": "sha256:dummy",
        "skills": list(skills_data.keys()),
        "permissions": {}
    }
    
    with open(os.path.join(tmpdir, 'pack.yaml'), 'w', encoding='utf-8') as f:
        yaml.dump(pack_data, f)
        
    for skill_name, content in skills_data.items():
        skill_dir = os.path.join(tmpdir, 'skills', skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        if content is not None:
            with open(os.path.join(skill_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
                f.write(content)
                
    if manifest_skills is not None:
        manifest_data = {"skills": [{"name": s} for s in manifest_skills]}
        with open(os.path.join(tmpdir, 'skills.manifest.yaml'), 'w', encoding='utf-8') as f:
            yaml.dump(manifest_data, f)
            
    return ExtensionPack(tmpdir)

def test_gauntlet_pass():
    with tempfile.TemporaryDirectory() as tmpdir:
        content = "---\nname: my-skill\ndescription: Use when testing\n---\nBody"
        pack = create_skill_pack(tmpdir, {"my-skill": content})
        
        result = run_skill_gauntlet(pack, project_path=tmpdir)
        assert result.passed is True
        assert len(result.failed_skills) == 0

def test_gauntlet_missing_skill_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        pack = create_skill_pack(tmpdir, {"my-skill": None})
        
        result = run_skill_gauntlet(pack, project_path=tmpdir)
        assert result.passed is False
        assert "my-skill" in result.failed_skills

def test_gauntlet_missing_frontmatter():
    with tempfile.TemporaryDirectory() as tmpdir:
        content = "Just some text, no frontmatter"
        pack = create_skill_pack(tmpdir, {"my-skill": content})
        
        result = run_skill_gauntlet(pack, project_path=tmpdir)
        assert result.passed is False

def test_gauntlet_routing_contract():
    with tempfile.TemporaryDirectory() as tmpdir:
        content = "---\nname: my-skill\ndescription: Does some stuff\n---\nBody"
        pack = create_skill_pack(tmpdir, {"my-skill": content})
        
        result = run_skill_gauntlet(pack, project_path=tmpdir)
        assert result.passed is False
        assert any("Use when" in c.message for c in result.checks if not c.passed)

def test_gauntlet_manifest_collision():
    with tempfile.TemporaryDirectory() as tmpdir:
        content = "---\nname: existing-skill\ndescription: Use when testing\n---\nBody"
        pack = create_skill_pack(tmpdir, {"existing-skill": content}, manifest_skills=["existing-skill"])
        
        result = run_skill_gauntlet(pack, project_path=tmpdir)
        assert result.passed is False
        assert any("already exists" in c.message for c in result.checks if not c.passed)

if __name__ == "__main__":
    tests = [
        test_gauntlet_pass,
        test_gauntlet_missing_skill_md,
        test_gauntlet_missing_frontmatter,
        test_gauntlet_routing_contract,
        test_gauntlet_manifest_collision
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
