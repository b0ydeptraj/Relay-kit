#!/usr/bin/env python3
"""
string_encrypt.py - XOR-encrypt all string literals in a Python source file.
Replaces plaintext strings with runtime XOR-decrypt calls for obfuscation.

Usage:
    python scripts/string_encrypt.py --input target.py --output target_obf.py --key MYKEY
    python scripts/string_encrypt.py --input target.py --key auto
"""
import argparse
import ast
import base64
import os
import re
import sys


def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def generate_decoder_stub(key_b64: str) -> str:
    return f"""
import base64 as _b64
def _d(s):
    k=_b64.b64decode("{key_b64}");d=_b64.b64decode(s);return bytes(b^k[i%len(k)]for i,b in enumerate(d)).decode()
"""


def obfuscate_strings(source: str, key: bytes) -> str:
    """Replace string literals with _d(encrypted_b64) calls."""
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[-] SyntaxError: {e}"); return source

    replacements = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if len(val) < 3:
                continue  # skip trivial strings
            encrypted = xor_encrypt(val.encode("utf-8", errors="replace"), key)
            enc_b64 = base64.b64encode(encrypted).decode()
            replacements.append((node.value, f'_d("{enc_b64}")'))

    result = source
    for orig, replacement in sorted(replacements, key=lambda x: -len(x[0])):
        result = result.replace(f'"{orig}"', replacement, 1)
        result = result.replace(f"'{orig}'", replacement, 1)

    return result


def scramble_identifiers(source: str) -> str:
    """Replace non-dunder variable names with hashed versions (basic)."""
    import hashlib
    seen = {}
    tokens = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', source)
    keywords = {"def","class","if","else","elif","while","for","in","return","import","from",
                "True","False","None","and","or","not","pass","break","continue","try","except",
                "finally","with","as","raise","del","yield","lambda","global","nonlocal",
                "assert","is","print","len","range","str","int","float","list","dict","set",
                "bytes","open","os","sys","re","_d","_b64"}
    for tok in set(tokens):
        if tok in keywords or tok.startswith("__") or tok[0].isupper():
            continue
        h = "_" + hashlib.md5(tok.encode()).hexdigest()[:8]
        seen[tok] = h

    result = source
    for orig, rep in seen.items():
        result = re.sub(rf'\b{re.escape(orig)}\b', rep, result)
    return result


def main():
    p = argparse.ArgumentParser(description="Python source string obfuscator")
    p.add_argument("--input", required=True)
    p.add_argument("--output", help="Output file (default: <input>_obf.py)")
    p.add_argument("--key", default="auto", help="XOR key string or 'auto'")
    p.add_argument("--scramble-names", action="store_true", help="Also scramble variable names")
    args = p.parse_args()

    if not os.path.exists(args.input):
        print(f"[-] File not found: {args.input}"); sys.exit(1)

    key_str = os.urandom(16).hex() if args.key == "auto" else args.key
    key = key_str.encode()
    key_b64 = base64.b64encode(key).decode()

    print(f"[*] Input  : {args.input}")
    print(f"[*] Key    : {key_str}")

    source = open(args.input, "r", encoding="utf-8").read()
    obf = obfuscate_strings(source, key)
    if args.scramble_names:
        obf = scramble_identifiers(obf)

    decoder = generate_decoder_stub(key_b64)
    final = f"# Obfuscated by string_encrypt.py\n{decoder}\n{obf}"

    out = args.output or args.input.replace(".py", "_obf.py")
    open(out, "w", encoding="utf-8").write(final)
    print(f"[+] Output : {out} ({os.path.getsize(out):,} bytes)")
    print(f"[+] XOR key (b64): {key_b64}")


if __name__ == "__main__":
    main()
