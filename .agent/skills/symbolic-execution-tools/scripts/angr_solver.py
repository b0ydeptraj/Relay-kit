#!/usr/bin/env python3
"""
angr_solver.py - Symbolic execution framework for solving binary constraints.
Uses angr to find inputs that reach target addresses or avoid bad states.

Usage:
    python scripts/angr_solver.py --binary crackme.exe --find 0x401337 --avoid 0x401400
    python scripts/angr_solver.py --binary crackme.exe --find-string "Correct!" --avoid-string "Wrong"
    python scripts/angr_solver.py --binary crackme.exe --mode password --max-len 20
    python scripts/angr_solver.py --binary crackme.exe --cfg --output cfg.dot

Requirements: pip install angr
"""
import argparse
import os
import sys
import time

def check_angr():
    try:
        import angr
        return True
    except ImportError:
        print("[-] angr not installed. Install: pip install angr")
        print("    Note: angr requires Python 3.8+ and ~500MB disk space")
        return False


def find_string_addresses(binary_path: str, target_str: str) -> list:
    """Find addresses of a string in binary (without angr)."""
    with open(binary_path, "rb") as f:
        data = f.read()
    addrs = []
    enc = target_str.encode("utf-8")
    idx = 0
    while True:
        pos = data.find(enc, idx)
        if pos == -1: break
        # Heuristic: assume PE base 0x400000
        addrs.append(0x400000 + pos)
        idx = pos + 1
    return addrs


def solve_with_angr(binary_path: str, find_addr: int, avoid_addrs: list,
                    input_len: int = 16, stdin_mode: bool = True) -> dict:
    """Run angr symbolic execution to find satisfying input."""
    try:
        import angr
        import claripy
    except ImportError:
        return {"error": "angr not installed"}

    print(f"[*] Loading binary: {binary_path}")
    start = time.time()

    try:
        proj = angr.Project(binary_path, auto_load_libs=False)
        print(f"[*] Architecture: {proj.arch.name}")
        print(f"[*] Entry: {hex(proj.entry)}")
        print(f"[*] Finding: {hex(find_addr)} | Avoiding: {[hex(a) for a in avoid_addrs]}")

        if stdin_mode:
            # Symbolic stdin
            flag = claripy.BVS("flag", input_len * 8)
            state = proj.factory.full_init_state(stdin=claripy.Concat(flag, claripy.BVV(b'\n')))

            # Add printable constraints
            for byte in flag.chop(8):
                state.add_constraints(byte >= 0x20)
                state.add_constraints(byte <= 0x7e)
        else:
            state = proj.factory.entry_state()

        sim = proj.factory.simulation_manager(state)
        sim.explore(find=find_addr, avoid=avoid_addrs, timeout=60)

        elapsed = round(time.time() - start, 1)
        if sim.found:
            found_state = sim.found[0]
            if stdin_mode:
                solution = found_state.solver.eval(flag, cast_to=bytes)
                solution_str = solution.decode("utf-8", errors="replace").rstrip("\x00")
                print(f"[+] SOLUTION FOUND in {elapsed}s: {repr(solution_str)}")
                return {"found": True, "input": solution_str, "elapsed": elapsed}
            else:
                print(f"[+] Reachable state found in {elapsed}s")
                return {"found": True, "state": str(found_state), "elapsed": elapsed}
        else:
            print(f"[-] No solution found in {elapsed}s")
            return {"found": False, "elapsed": elapsed}

    except Exception as e:
        return {"error": str(e)[:200]}


def generate_cfg(binary_path: str, output_path: str = "cfg.dot") -> bool:
    """Generate Control Flow Graph using angr."""
    try:
        import angr
        proj = angr.Project(binary_path, auto_load_libs=False)
        print(f"[*] Generating CFG for {binary_path}...")
        cfg = proj.analyses.CFGFast()
        print(f"[*] CFG: {len(cfg.graph.nodes())} nodes, {len(cfg.graph.edges())} edges")

        # Export to DOT format
        try:
            import networkx as nx
            nx.drawing.nx_pydot.write_dot(cfg.graph, output_path)
            print(f"[+] CFG saved: {output_path}")
            print(f"    View with: dot -Tpng {output_path} -o cfg.png")
            return True
        except ImportError:
            print("[!] networkx/pydot not installed. pip install networkx pydot")
            # Fallback: print stats
            for node in list(cfg.graph.nodes())[:10]:
                print(f"  Node: {node}")
            return False
    except ImportError:
        print("[-] angr not installed"); return False
    except Exception as e:
        print(f"[-] CFG error: {e}"); return False


def demo_mode():
    """Show what angr can do without actually running it."""
    print("[*] angr Symbolic Execution Capabilities:")
    print("")
    print("  1. Crack password checks:")
    print("     python angr_solver.py --binary crackme.exe --find 0x401337 --avoid 0x401400")
    print("")
    print("  2. Find input to reach specific code:")
    print("     python angr_solver.py --binary app.exe --find-string 'Congratulations'")
    print("")
    print("  3. Generate Control Flow Graph:")
    print("     python angr_solver.py --binary app.exe --cfg --output cfg.dot")
    print("")
    print("  4. Solve with max input length:")
    print("     python angr_solver.py --binary ctf.exe --find 0x4013B0 --max-len 32")
    print("")
    print("  Requirements: pip install angr (may take ~10 min first install)")
    print("")
    print("[*] Example angr script:")
    example = '''
import angr, claripy

proj = angr.Project("crackme.exe", auto_load_libs=False)
flag = claripy.BVS("flag", 16 * 8)  # 16-byte symbolic input
state = proj.factory.full_init_state(
    stdin=claripy.Concat(flag, claripy.BVV(b"\\n"))
)
# Constrain to printable ASCII
for b in flag.chop(8):
    state.add_constraints(b >= 0x20, b <= 0x7e)

sim = proj.factory.simulation_manager(state)
sim.explore(find=0x401337, avoid=[0x401400, 0x401450])

if sim.found:
    sol = sim.found[0].solver.eval(flag, cast_to=bytes)
    print(f"Password: {sol.decode()}")
'''
    print(example)


def main():
    p = argparse.ArgumentParser(description="Symbolic execution solver using angr")
    p.add_argument("--binary", help="Target binary")
    p.add_argument("--find", help="Address to find (hex)")
    p.add_argument("--find-string", help="String to find in binary and target")
    p.add_argument("--avoid", nargs="+", help="Addresses to avoid (hex)")
    p.add_argument("--avoid-string", help="String to avoid reaching")
    p.add_argument("--mode", choices=["password","stdin","argv"], default="stdin")
    p.add_argument("--max-len", type=int, default=16)
    p.add_argument("--cfg", action="store_true")
    p.add_argument("--output", default="cfg.dot")
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()

    if args.demo or not args.binary:
        demo_mode(); return

    if not os.path.exists(args.binary):
        print(f"[-] Binary not found: {args.binary}"); sys.exit(1)

    if args.cfg:
        generate_cfg(args.binary, args.output)
        return

    if not check_angr():
        sys.exit(1)

    # Resolve addresses
    find_addr = None
    avoid_addrs = []

    if args.find:
        find_addr = int(args.find, 16)
    elif args.find_string:
        addrs = find_string_addresses(args.binary, args.find_string)
        if addrs:
            find_addr = addrs[0]
            print(f"[*] Found '{args.find_string}' at: {[hex(a) for a in addrs]}")
        else:
            print(f"[-] String '{args.find_string}' not found in binary"); sys.exit(1)

    if args.avoid:
        avoid_addrs = [int(a, 16) for a in args.avoid]
    if args.avoid_string:
        addrs = find_string_addresses(args.binary, args.avoid_string)
        avoid_addrs.extend(addrs)

    if not find_addr:
        print("[-] --find or --find-string required"); sys.exit(1)

    result = solve_with_angr(args.binary, find_addr, avoid_addrs, args.max_len)
    if result.get("found"):
        print(f"[+] Input to reach {hex(find_addr)}: {repr(result.get('input',''))}")
    elif result.get("error"):
        print(f"[-] Error: {result['error']}")


if __name__ == "__main__":
    main()
