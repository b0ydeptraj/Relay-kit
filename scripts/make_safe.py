import sys
from pathlib import Path

# Modify old CLI to not exit
with open('old_cli.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("if __name__ == '__main__':\n    raise SystemExit(main())", "")
code = code.replace("if __name__ == \"__main__\":\n    raise SystemExit(main())", "")

with open('old_cli_safe.py', 'w', encoding='utf-8') as f:
    f.write(code)
