import sys

def _run_script_main(module: object, program: str, argv: list[str]) -> int:
    original_argv = sys.argv[:]
    try:
        sys.argv = [program, *argv]
        return int(module.main())  # type: ignore[attr-defined]
    finally:
        sys.argv = original_argv
