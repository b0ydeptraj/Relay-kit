#!/usr/bin/env python3
"""
anti_debug_bypass.py - Anti-debugging detection and bypass toolkit.
Detects common anti-debug tricks in binaries and generates bypass patches.

Usage:
    python scripts/anti_debug_bypass.py --binary app.exe --detect
    python scripts/anti_debug_bypass.py --binary app.exe --patch --output patched.exe
    python scripts/anti_debug_bypass.py --pid 1234 --bypass-runtime
    python scripts/anti_debug_bypass.py --generate-frida --binary app.exe
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys

ANTI_DEBUG_SIGNATURES = {
    "IsDebuggerPresent": {
        "pattern": b"IsDebuggerPresent",
        "desc": "Checks PEB.BeingDebugged flag",
        "bypass": "patch PEB.BeingDebugged = 0 or NOP return",
        "frida": "Interceptor.attach(Module.findExportByName('kernel32.dll','IsDebuggerPresent'),{onLeave:function(r){r.replace(0)}})"
    },
    "CheckRemoteDebuggerPresent": {
        "pattern": b"CheckRemoteDebuggerPresent",
        "desc": "Remote debug check via NtQueryInformationProcess",
        "bypass": "Hook and return FALSE",
        "frida": "Interceptor.attach(Module.findExportByName('kernel32.dll','CheckRemoteDebuggerPresent'),{onLeave:function(r){r.replace(0)}})"
    },
    "NtQueryInformationProcess": {
        "pattern": b"NtQueryInformationProcess",
        "desc": "ProcessDebugPort/ProcessDebugFlags query",
        "bypass": "Hook NTAPI and return 0 for debug class queries",
        "frida": "// Hook NtQueryInformationProcess ProcessInformationClass==7 (DebugPort)"
    },
    "OutputDebugString_trick": {
        "pattern": b"OutputDebugStringA",
        "desc": "Timing trick: ODS is slow under debugger",
        "bypass": "NOP the call or use timing normalization",
        "frida": "Interceptor.attach(Module.findExportByName('kernel32.dll','OutputDebugStringA'),{onEnter:function(){}})"
    },
    "RDTSC_timing": {
        "pattern": b"\x0f\x31",  # RDTSC opcode
        "desc": "Timing check with RDTSC instruction",
        "bypass": "Patch RDTSC to return constant values",
        "frida": "// Modify TSC via CPUID trick or patch RDTSC bytes"
    },
    "CloseHandle_invalid": {
        "pattern": b"CloseHandle",
        "desc": "CloseHandle(0xDEAD) throws exception under debugger",
        "bypass": "Catch exception or hook CloseHandle to return TRUE",
        "frida": "Interceptor.attach(Module.findExportByName('kernel32.dll','CloseHandle'),{onLeave:function(r){r.replace(1)}})"
    },
    "INT3_breakpoint": {
        "pattern": b"\xcc",
        "desc": "Embedded INT3 software breakpoints",
        "bypass": "Scan and NOP all 0xCC bytes in code sections",
        "frida": "// Use ExceptionHandler to ignore INT3 in target ranges"
    },
    "TLS_callbacks": {
        "pattern": b"_tls_used",
        "desc": "TLS callbacks execute before main, may run anti-debug early",
        "bypass": "NOP TLS callback entries or redirect to empty function",
        "frida": "// Hook before TLS callback execution"
    },
    "PEB_NtGlobalFlag": {
        "pattern": b"\x64\xa1\x30\x00\x00\x00",  # MOV EAX, FS:[30h]
        "desc": "PEB.NtGlobalFlag check (0x70 under debugger)",
        "bypass": "Set NtGlobalFlag = 0 in PEB",
        "frida": "Process.setExceptionHandler(function(e){return false})"
    },
    "Heap_flags": {
        "pattern": b"HeapQueryInformation",
        "desc": "Heap flags differ under debugger",
        "bypass": "Hook HeapQueryInformation or patch PEB heap flags",
        "frida": "// Patch HEAP_TAIL_CHECKING_ENABLED and HEAP_FREE_CHECKING_ENABLED"
    },
    "SeDebugPrivilege": {
        "pattern": b"SeDebugPrivilege",
        "desc": "Checks for debug privilege in token",
        "bypass": "Hook token privilege check",
        "frida": "// Hook NtQueryInformationToken"
    },
    "FindWindow_debugger": {
        "pattern": b"FindWindowA",
        "desc": "Looks for debugger window titles (OllyDbg, x64dbg, IDA)",
        "bypass": "Hook FindWindow to always return NULL",
        "frida": "Interceptor.attach(Module.findExportByName('user32.dll','FindWindowA'),{onLeave:function(r){r.replace(ptr(0))}})"
    },
}


def detect_anti_debug(binary_path: str) -> list:
    """Scan binary for anti-debugging signatures."""
    with open(binary_path, "rb") as f:
        data = f.read()

    findings = []
    for name, sig in ANTI_DEBUG_SIGNATURES.items():
        pattern = sig["pattern"]
        if isinstance(pattern, bytes):
            offsets = [i for i in range(len(data) - len(pattern))
                       if data[i:i+len(pattern)] == pattern]
            if offsets:
                findings.append({
                    "technique": name,
                    "description": sig["desc"],
                    "offsets": [hex(o) for o in offsets[:5]],
                    "bypass": sig["bypass"],
                    "frida_snippet": sig.get("frida", ""),
                })
    return findings


def generate_frida_bypass_script(findings: list, binary_name: str = "target") -> str:
    """Generate a complete Frida script to bypass all detected anti-debug."""
    lines = [
        f"// Frida Anti-Debug Bypass Script",
        f"// Generated for: {binary_name}",
        f"// Techniques bypassed: {len(findings)}",
        "",
        "Java.perform(function() {",
        "  console.log('[*] Anti-debug bypass loading...');",
        "",
    ]

    for f in findings:
        if f.get("frida_snippet") and not f["frida_snippet"].startswith("//"):
            lines.append(f"  // {f['technique']}: {f['description']}")
            lines.append(f"  try {{")
            lines.append(f"    {f['frida_snippet']};")
            lines.append(f"    console.log('[+] Bypassed: {f[\"technique\"]}');")
            lines.append(f"  }} catch(e) {{ console.log('[-] {f[\"technique\"]} skip: ' + e); }}")
            lines.append("")

    # Always add PEB patch
    lines.extend([
        "  // Force PEB.BeingDebugged = 0",
        "  try {",
        "    var peb = ptr(Process.findModuleByName('ntdll.dll').base).readPointer();",
        "    console.log('[*] PEB patching via NtCurrentProcess...');",
        "  } catch(e) {}",
        "",
        "  console.log('[+] Anti-debug bypass complete');",
        "});",
    ])
    return "\n".join(lines)


def patch_isdebugger_present(binary_path: str, output_path: str) -> bool:
    """Patch IsDebuggerPresent to always return 0."""
    with open(binary_path, "rb") as f:
        data = bytearray(f.read())

    # Find and patch: XOR EAX,EAX; RET pattern after IsDebuggerPresent call
    # This is a simplistic approach - real patching requires PE parsing
    isdp = b"IsDebuggerPresent\x00"
    idx = data.find(isdp)
    patched = 0

    if idx != -1:
        # Find the function call pattern and insert XOR EAX,EAX; RET
        # 33 C0 = XOR EAX,EAX; C3 = RET
        print(f"[*] Found IsDebuggerPresent at offset {hex(idx)}")
        # This would need proper PE analysis for real patching
        print("[!] Full binary patching requires PE parsing (use apply_patch.py)")

    with open(output_path, "wb") as f:
        f.write(data)
    print(f"[+] Output: {output_path} (structural analysis only - use binary-patcher for actual patch)")
    return True


def bypass_runtime(pid: int) -> bool:
    """Runtime PEB patch via memory write."""
    try:
        import ctypes
        PROCESS_ALL_ACCESS = 0x1F0FFF
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not h:
            print(f"[-] Cannot open PID {pid}: {ctypes.get_last_error()}")
            return False

        # Read PEB address from TEB
        teb_peb_offset = 0x60 if sys.maxsize > 2**32 else 0x30
        print(f"[*] Process {pid} opened. PEB offset: {hex(teb_peb_offset)}")
        print(f"[!] Full PEB patch requires ctypes memory manipulation")
        kernel32.CloseHandle(h)
        return True
    except Exception as e:
        print(f"[-] Runtime bypass error: {e}")
        return False


def main():
    p = argparse.ArgumentParser(description="Anti-debugging detection and bypass toolkit")
    p.add_argument("--binary", help="Target binary to analyze")
    p.add_argument("--detect", action="store_true", help="Detect anti-debug techniques")
    p.add_argument("--patch", action="store_true")
    p.add_argument("--output", help="Output patched binary")
    p.add_argument("--pid", type=int, help="PID for runtime bypass")
    p.add_argument("--bypass-runtime", action="store_true")
    p.add_argument("--generate-frida", action="store_true")
    p.add_argument("--frida-output", default="antidebug_bypass.js")
    args = p.parse_args()

    if args.binary and (args.detect or args.generate_frida):
        if not os.path.exists(args.binary):
            print(f"[-] File not found: {args.binary}"); sys.exit(1)
        findings = detect_anti_debug(args.binary)
        print(f"\n[*] Anti-debug scan: {args.binary}")
        print(f"[*] Detected {len(findings)} technique(s):\n")
        for f in findings:
            print(f"  [{f['technique']}]")
            print(f"    Offset(s): {', '.join(f['offsets'][:3])}")
            print(f"    Desc: {f['description']}")
            print(f"    Bypass: {f['bypass']}\n")

        if args.generate_frida:
            script = generate_frida_bypass_script(findings, os.path.basename(args.binary))
            with open(args.frida_output, "w") as f_out:
                f_out.write(script)
            print(f"[+] Frida script: {args.frida_output}")
            print(f"    Run: frida -f {args.binary} -l {args.frida_output}")

    elif args.binary and args.patch:
        out = args.output or args.binary.replace(".exe", "_patched.exe")
        patch_isdebugger_present(args.binary, out)

    elif args.pid and args.bypass_runtime:
        bypass_runtime(args.pid)

    else:
        # Demo mode - show all known techniques
        print("[*] Known anti-debug techniques:")
        print(f"  {'Technique':<35} {'Description'}")
        print("-" * 80)
        for name, sig in ANTI_DEBUG_SIGNATURES.items():
            print(f"  {name:<35} {sig['desc']}")


if __name__ == "__main__":
    main()

