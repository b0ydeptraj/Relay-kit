import os
import sys
import tempfile
import traceback
from relay_kit_v3.cli.engine import dispatch
from relay_kit_v3.extensions.quarantine import QuarantineManager

def test_cli_ext_list():
    
    # We will just verify it doesn't crash on list
    try:
        # Override sys.argv and sys.exit to avoid exiting the test suite
        original_exit = sys.exit
        exit_code = None
        def dummy_exit(code):
            nonlocal exit_code
            exit_code = code
            raise RuntimeError(f"Exit {code}")
            
        sys.exit = dummy_exit
        
        try:
            dispatch("ext", ["list"])
        except RuntimeError as e:
            assert exit_code == 0
    finally:
        sys.exit = original_exit

if __name__ == "__main__":
    tests = [
        test_cli_ext_list
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
