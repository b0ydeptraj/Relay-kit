"""
Generate full Relay-Kit offensive tool pack pipeline for 23 skills.
Pipeline: registry (already done) -> safety scope -> generate all adapters -> eval/gate
"""
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(r"C:\Users\b0ydeptrai\Documents\relay-kit")
ADAPTERS = [".agent", ".codex", ".claude"]

OFFENSIVE_SKILLS = [
    "advanced-python-engineering",
    "antibot-challenge-solving",
    "attack-chain-orchestration",
    "binary-reverse-methodology",
    "binary-stealth-obfuscation",
    "browser-fingerprint-engineering",
    "cpp-systems-engineering",
    "desktop-imgui-development",
    "desktop-python-ui",
    "edr-evasion-tactics",
    "field-journal-evolution",
    "frontend-crypto-reverse",
    "malware-analysis-workflows",
    "mmo-llm-automation",
    "mmo-onchain-security-audit",
    "mobile-app-reverse",
    "network-stealth-c2",
    "offensive-security-engagement",
    "process-injection-techniques",
    "protocol-fingerprint-spoofing",
    "telemetry-blinding",
    "terminal-operator-ui",
    "windows-native-internals",
]

# --- Skill metadata for generating domain-specific content ---
SKILL_META = {
    "advanced-python-engineering": {
        "role": "python-specialist",
        "category": "engineering",
        "task": "implement advanced Python patterns including async I/O, ctypes/cffi interop, metaprogramming, and C extension modules",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["asyncio", "ctypes", "cffi"],
        "terms": ["async model", "ctypes signature", "error hierarchy", "version pin"],
        "traps": ["no version pin", "mixed async/sync", "missing C header doc"],
        "competencies": [
            ("engineering.async-discipline", "Declare async model and identify cancellation points.", ["asyncio", "trio", "cancellation"]),
            ("engineering.interop-safety", "Document ctypes/cffi signatures with original C headers.", ["ctypes", "cffi", "calling convention"]),
            ("engineering.error-hierarchy", "Define recoverable vs fatal exception hierarchy.", ["exception", "recoverable", "fatal"]),
            ("engineering.dependency-pins", "Pin all external dependency versions.", ["version", "pin", "requirements"]),
        ],
        "failure_traps_list": [
            ("engineering.mixed-async-sync", "Mixed async and sync I/O in the same call chain without explicit bridging."),
            ("engineering.floating-deps", "Floating dependency versions causing reproducibility failures."),
        ],
    },
    "antibot-challenge-solving": {
        "role": "antibot-specialist",
        "category": "evasion",
        "task": "solve or bypass antibot challenges including CAPTCHAs, JavaScript challenges, and behavioral verification",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["challenge_solver", "captcha"],
        "terms": ["challenge type", "solver strategy", "behavioral bypass", "token extraction"],
        "traps": ["brute force without analysis", "hardcoded selectors", "no fallback strategy"],
        "competencies": [
            ("evasion.challenge-classification", "Classify challenge type before attempting solution.", ["challenge", "CAPTCHA", "JS challenge"]),
            ("evasion.solver-strategy", "Select appropriate solver based on challenge analysis.", ["solver", "strategy", "fallback"]),
            ("evasion.token-extraction", "Extract and validate challenge response tokens.", ["token", "response", "validation"]),
        ],
        "failure_traps_list": [
            ("evasion.brute-force", "Attempting brute force without analyzing the challenge type."),
            ("evasion.no-fallback", "No fallback strategy when primary solver fails."),
        ],
    },
    "attack-chain-orchestration": {
        "role": "attack-orchestrator",
        "category": "offensive",
        "task": "orchestrate multi-phase attack chains following ATT&CK framework ordering with OPSEC discipline",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["attack_chain", "phase_order"],
        "terms": ["ATT&CK phase", "kill chain", "OPSEC ordering", "phase transition"],
        "traps": ["skip recon phase", "no OPSEC check between phases", "unordered execution"],
        "competencies": [
            ("offensive.phase-ordering", "Follow ATT&CK kill chain ordering strictly.", ["ATT&CK", "kill chain", "phase"]),
            ("offensive.opsec-gates", "Enforce OPSEC checks between phase transitions.", ["OPSEC", "transition", "gate"]),
            ("offensive.evidence-chain", "Maintain evidence chain across all phases.", ["evidence", "chain", "artifact"]),
        ],
        "failure_traps_list": [
            ("offensive.skip-recon", "Skipping reconnaissance phase before initial access."),
            ("offensive.no-opsec-gate", "No OPSEC validation between attack phases."),
        ],
    },
    "binary-reverse-methodology": {
        "role": "reverse-engineer",
        "category": "reverse-engineering",
        "task": "systematically reverse-engineer binary executables using static and dynamic analysis techniques",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["disassembly", "decompiler"],
        "terms": ["static analysis", "dynamic analysis", "control flow", "function boundary"],
        "traps": ["skip static before dynamic", "no function boundary map", "guessing without evidence"],
        "competencies": [
            ("reverse.static-first", "Perform static analysis before dynamic analysis.", ["static", "disassembly", "strings"]),
            ("reverse.function-map", "Map function boundaries and call graph before deep analysis.", ["function", "call graph", "boundary"]),
            ("reverse.hypothesis-driven", "Form and test hypotheses about binary behavior.", ["hypothesis", "test", "verify"]),
        ],
        "failure_traps_list": [
            ("reverse.dynamic-first", "Jumping to dynamic analysis without static analysis context."),
            ("reverse.guess-without-evidence", "Guessing binary behavior without disassembly evidence."),
        ],
    },
    "binary-stealth-obfuscation": {
        "role": "obfuscation-specialist",
        "category": "evasion",
        "task": "obfuscate binary payloads to evade static analysis, AV signatures, and YARA rules",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["obfuscator", "packer"],
        "terms": ["entropy control", "signature evasion", "packing", "mutation engine"],
        "traps": ["high entropy without justification", "no AV test", "single technique only"],
        "competencies": [
            ("evasion.entropy-control", "Control binary entropy to avoid statistical detection.", ["entropy", "histogram", "section"]),
            ("evasion.signature-mutation", "Mutate signatures to evade pattern matching.", ["signature", "mutation", "YARA"]),
            ("evasion.av-testing", "Test against AV engines before deployment.", ["AV", "test", "detection rate"]),
        ],
        "failure_traps_list": [
            ("evasion.high-entropy", "Producing high-entropy output that triggers statistical detection."),
            ("evasion.untested-payload", "Deploying without AV/EDR testing."),
        ],
    },
    "browser-fingerprint-engineering": {
        "role": "fingerprint-engineer",
        "category": "evasion",
        "task": "engineer consistent browser fingerprints to defeat canvas, WebGL, AudioContext, and behavioral fingerprinting",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["canvas_fingerprint", "webgl_hash"],
        "terms": ["canvas hash", "WebGL renderer", "AudioContext", "font enumeration"],
        "traps": ["inconsistent fingerprint components", "detectable spoofing", "missing navigator props"],
        "competencies": [
            ("evasion.fingerprint-consistency", "Ensure all fingerprint components are internally consistent.", ["canvas", "WebGL", "AudioContext", "navigator"]),
            ("evasion.spoof-detection", "Verify spoofed fingerprints are not detectable as spoofed.", ["detection", "consistency", "entropy"]),
            ("evasion.behavioral-mimicry", "Mimic real user behavioral patterns.", ["mouse", "keyboard", "scroll", "timing"]),
        ],
        "failure_traps_list": [
            ("evasion.inconsistent-fp", "Fingerprint components contradict each other."),
            ("evasion.detectable-spoof", "Spoofed values are detectable by integrity checks."),
        ],
    },
    "cpp-systems-engineering": {
        "role": "cpp-specialist",
        "category": "engineering",
        "task": "implement systems-level C++ for kernel drivers, DLL injection, memory manipulation, and Win32/NT API integration",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["NtApi", "HANDLE", "DWORD"],
        "terms": ["Win32 API", "NT internals", "memory layout", "calling convention"],
        "traps": ["no error checking on API calls", "memory leak", "wrong calling convention"],
        "competencies": [
            ("engineering.api-error-check", "Check return values for every Win32/NT API call.", ["GetLastError", "NTSTATUS", "return value"]),
            ("engineering.memory-safety", "Prevent leaks and UAF in manual memory management.", ["RAII", "leak", "use-after-free"]),
            ("engineering.abi-correctness", "Use correct calling conventions and struct alignment.", ["stdcall", "cdecl", "alignment"]),
        ],
        "failure_traps_list": [
            ("engineering.unchecked-api", "Ignoring return values from system API calls."),
            ("engineering.memory-leak", "Allocating without corresponding deallocation path."),
        ],
    },
    "desktop-imgui-development": {
        "role": "imgui-developer",
        "category": "engineering",
        "task": "build desktop overlay and tool UIs using Dear ImGui with DirectX/OpenGL backends",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["ImGui", "ImVec2", "ImGuiWindowFlags"],
        "terms": ["render loop", "overlay", "input handling", "widget layout"],
        "traps": ["blocking render loop", "no input passthrough", "missing cleanup"],
        "competencies": [
            ("engineering.render-loop", "Implement non-blocking render loop with proper frame timing.", ["frame", "vsync", "delta time"]),
            ("engineering.overlay-transparency", "Configure transparent overlay with click-through.", ["overlay", "transparent", "passthrough"]),
            ("engineering.imgui-state", "Manage ImGui widget state and ID stack correctly.", ["ID", "PushID", "state"]),
        ],
        "failure_traps_list": [
            ("engineering.blocking-render", "Blocking the render loop with synchronous operations."),
            ("engineering.no-cleanup", "Missing ImGui/backend cleanup on shutdown."),
        ],
    },
    "desktop-python-ui": {
        "role": "python-ui-developer",
        "category": "engineering",
        "task": "build desktop applications using Python UI frameworks like PyQt, PySide, Tkinter, or Dear PyGui",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["QApplication", "MainWindow"],
        "terms": ["event loop", "signal-slot", "widget tree", "threading model"],
        "traps": ["UI updates from worker thread", "blocking event loop", "no error dialog"],
        "competencies": [
            ("engineering.event-loop", "Keep the UI event loop responsive.", ["event loop", "responsive", "non-blocking"]),
            ("engineering.thread-safety", "Never update UI from worker threads directly.", ["thread", "signal", "invoke"]),
            ("engineering.layout-discipline", "Use layout managers instead of absolute positioning.", ["layout", "grid", "box"]),
        ],
        "failure_traps_list": [
            ("engineering.ui-from-thread", "Updating UI widgets directly from a background thread."),
            ("engineering.blocking-loop", "Blocking the event loop with synchronous I/O."),
        ],
    },
    "edr-evasion-tactics": {
        "role": "edr-evasion-specialist",
        "category": "evasion",
        "task": "evade EDR detection through unhooking, direct syscalls, callback manipulation, and ETW blinding",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["syscall_stub", "unhook"],
        "terms": ["userland hook", "direct syscall", "ETW patch", "callback removal"],
        "traps": ["incomplete unhook", "wrong syscall number", "detectable ETW patch"],
        "competencies": [
            ("evasion.syscall-correctness", "Use correct syscall numbers for target OS version.", ["syscall", "SSN", "version"]),
            ("evasion.unhook-completeness", "Unhook all monitored APIs, not just common ones.", ["unhook", "ntdll", "IAT"]),
            ("evasion.etw-blinding", "Blind ETW without detectable patching artifacts.", ["ETW", "patch", "blind"]),
        ],
        "failure_traps_list": [
            ("evasion.wrong-ssn", "Using wrong syscall service number for the target OS build."),
            ("evasion.partial-unhook", "Unhooking only common APIs while leaving others monitored."),
        ],
    },
    "field-journal-evolution": {
        "role": "journal-curator",
        "category": "meta",
        "task": "evolve field journal entries by capturing pitfalls, techniques, and routing gaps with evidence backing",
        "files": ["relay_kit_v3/field_journal.py", "relay_kit_v3/evidence_quality.py"],
        "symbols": ["capture_entry", "evidence_ref"],
        "terms": ["evidence ref", "confidence level", "pattern capture", "journal append"],
        "traps": ["entry without evidence", "auto-promote", "duplicate pattern"],
        "competencies": [
            ("meta.evidence-gating", "Never write journal entry without evidence reference.", ["evidence", "ref", "hash"]),
            ("meta.no-auto-promote", "Never auto-promote entries; require human approval.", ["candidate", "promote", "human"]),
            ("meta.dedup-check", "Check for duplicate patterns before capturing.", ["duplicate", "existing", "signature"]),
        ],
        "failure_traps_list": [
            ("meta.no-evidence", "Writing journal entry without evidence_ref."),
            ("meta.auto-promote", "Automatically promoting entry without human approval."),
        ],
    },
    "frontend-crypto-reverse": {
        "role": "crypto-reverser",
        "category": "reverse-engineering",
        "task": "reverse client-side cryptography, obfuscated JavaScript, WASM modules, and API signing parameters",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["crypto_params", "wasm_decode"],
        "terms": ["JS deobfuscation", "WASM reverse", "signing algorithm", "key extraction"],
        "traps": ["assuming algorithm without proof", "missing key rotation", "no replay test"],
        "competencies": [
            ("reverse.deobfuscation", "Systematically deobfuscate JavaScript before analysis.", ["deobfuscate", "AST", "control flow"]),
            ("reverse.algorithm-id", "Identify cryptographic algorithm from implementation patterns.", ["algorithm", "HMAC", "AES", "RSA"]),
            ("reverse.key-extraction", "Extract signing keys and rotation schedule.", ["key", "rotation", "extraction"]),
        ],
        "failure_traps_list": [
            ("reverse.assumed-algo", "Assuming crypto algorithm without evidence from code."),
            ("reverse.no-replay", "Not testing replayed requests to verify signing logic."),
        ],
    },
    "malware-analysis-workflows": {
        "role": "malware-analyst",
        "category": "reverse-engineering",
        "task": "analyze malware samples using sandbox, static, dynamic, and behavioral analysis workflows",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["sandbox_run", "ioc_extract"],
        "terms": ["IOC extraction", "sandbox analysis", "behavioral pattern", "YARA rule"],
        "traps": ["running on host", "no network isolation", "incomplete IOC list"],
        "competencies": [
            ("reverse.sandbox-isolation", "Always analyze in isolated sandbox environment.", ["sandbox", "VM", "isolation"]),
            ("reverse.ioc-completeness", "Extract complete IOC set including network, file, and registry.", ["IOC", "network", "file", "registry"]),
            ("reverse.yara-authoring", "Write YARA rules from identified patterns.", ["YARA", "rule", "pattern"]),
        ],
        "failure_traps_list": [
            ("reverse.host-execution", "Executing malware sample on analysis host."),
            ("reverse.incomplete-ioc", "Missing IOC categories in extraction."),
        ],
    },
    "mmo-llm-automation": {
        "role": "llm-automation-specialist",
        "category": "automation",
        "task": "integrate LLM APIs for bulk content generation, behavioral variance, and Sybil evasion in MMO operations",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["llm_client", "variance_engine"],
        "terms": ["prompt diversity", "behavioral variance", "content generation", "Sybil evasion"],
        "traps": ["identical outputs", "no rate limiting", "detectable patterns"],
        "competencies": [
            ("automation.prompt-diversity", "Generate diverse prompts to avoid pattern detection.", ["prompt", "diversity", "template"]),
            ("automation.rate-discipline", "Respect API rate limits and implement backoff.", ["rate", "limit", "backoff"]),
            ("automation.output-variance", "Ensure output variance across generated content.", ["variance", "unique", "fingerprint"]),
        ],
        "failure_traps_list": [
            ("automation.identical-output", "Producing identical content across multiple accounts."),
            ("automation.no-rate-limit", "Ignoring API rate limits."),
        ],
    },
    "mmo-onchain-security-audit": {
        "role": "onchain-auditor",
        "category": "security",
        "task": "audit on-chain scripts, smart contracts, and wallet automation for security vulnerabilities before deployment",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["contract_audit", "reentrancy_check"],
        "terms": ["reentrancy", "front-running", "access control", "integer overflow"],
        "traps": ["skip reentrancy check", "no gas analysis", "unchecked external call"],
        "competencies": [
            ("security.reentrancy-check", "Check for reentrancy vulnerabilities in all external calls.", ["reentrancy", "external call", "state change"]),
            ("security.access-control", "Verify access control on all privileged functions.", ["onlyOwner", "modifier", "access"]),
            ("security.gas-analysis", "Analyze gas costs and potential DoS through gas exhaustion.", ["gas", "loop", "DoS"]),
        ],
        "failure_traps_list": [
            ("security.missed-reentrancy", "Missing reentrancy check on external call."),
            ("security.no-access-control", "Privileged function without access control modifier."),
        ],
    },
    "mobile-app-reverse": {
        "role": "mobile-reverser",
        "category": "reverse-engineering",
        "task": "reverse-engineer mobile applications including APK/IPA analysis, SSL pinning bypass, and API extraction",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["apk_decompile", "ssl_unpin"],
        "terms": ["APK decompile", "IPA analysis", "SSL pinning", "API endpoint extraction"],
        "traps": ["skip manifest analysis", "no root/jailbreak detection bypass", "incomplete API map"],
        "competencies": [
            ("reverse.manifest-analysis", "Analyze AndroidManifest.xml/Info.plist before code.", ["manifest", "permissions", "components"]),
            ("reverse.ssl-bypass", "Bypass SSL pinning for traffic interception.", ["SSL", "pinning", "Frida", "proxy"]),
            ("reverse.api-mapping", "Map all API endpoints from decompiled code.", ["API", "endpoint", "URL", "request"]),
        ],
        "failure_traps_list": [
            ("reverse.skip-manifest", "Diving into code without analyzing app manifest."),
            ("reverse.incomplete-api", "Missing API endpoints in extraction."),
        ],
    },
    "network-stealth-c2": {
        "role": "c2-engineer",
        "category": "offensive",
        "task": "build and operate C2 infrastructure with traffic blending, domain fronting, protocol mimicry, and beaconing discipline",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["beacon_config", "redirector"],
        "terms": ["domain fronting", "traffic blending", "jitter", "redirector chain"],
        "traps": ["fixed beacon interval", "no redirector", "plaintext C2 channel"],
        "competencies": [
            ("offensive.beacon-discipline", "Configure beacon with jitter and sleep variation.", ["beacon", "jitter", "sleep"]),
            ("offensive.traffic-blending", "Blend C2 traffic with legitimate protocols.", ["HTTPS", "DNS", "CDN", "blend"]),
            ("offensive.redirector-chain", "Use redirector chain to hide true C2 server.", ["redirector", "proxy", "CDN"]),
        ],
        "failure_traps_list": [
            ("offensive.fixed-interval", "Fixed beacon interval without jitter."),
            ("offensive.direct-c2", "Direct connection to C2 server without redirectors."),
        ],
    },
    "offensive-security-engagement": {
        "role": "engagement-gate",
        "category": "offensive",
        "task": "gate and provide context for offensive security lanes including engagement proof caching and ATT&CK mapping",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["engagement_proof", "risk_tier"],
        "terms": ["engagement proof", "authorization", "ATT&CK phase", "risk tier"],
        "traps": ["proceed without authorization", "missing ATT&CK mapping", "own the lane"],
        "competencies": [
            ("offensive.authorization-gate", "Block all offensive work until engagement proof is cached.", ["authorization", "engagement", "proof"]),
            ("offensive.attack-mapping", "Map every offensive task to ATT&CK phase.", ["ATT&CK", "phase", "mapping"]),
            ("offensive.risk-annotation", "Annotate risk tier before specialist execution.", ["risk", "tier", "annotation"]),
        ],
        "failure_traps_list": [
            ("offensive.no-auth", "Proceeding with offensive techniques without engagement proof."),
            ("offensive.no-attack-map", "Skipping ATT&CK phase mapping."),
        ],
    },
    "process-injection-techniques": {
        "role": "injection-specialist",
        "category": "offensive",
        "task": "implement process injection techniques including DLL injection, process hollowing, APC injection, and thread hijacking",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["inject_dll", "hollow_process"],
        "terms": ["DLL injection", "process hollowing", "APC queue", "thread context"],
        "traps": ["wrong process architecture", "no cleanup on failure", "detectable allocation pattern"],
        "competencies": [
            ("offensive.arch-check", "Verify target process architecture before injection.", ["x86", "x64", "WoW64", "architecture"]),
            ("offensive.cleanup-on-fail", "Clean up allocated resources if injection fails.", ["cleanup", "VirtualFreeEx", "handle"]),
            ("offensive.alloc-stealth", "Use stealthy memory allocation patterns.", ["MEM_COMMIT", "PAGE_READWRITE", "RWX"]),
        ],
        "failure_traps_list": [
            ("offensive.arch-mismatch", "Injecting into process with wrong architecture."),
            ("offensive.no-cleanup", "Leaving allocated memory on injection failure."),
        ],
    },
    "protocol-fingerprint-spoofing": {
        "role": "protocol-spoofer",
        "category": "evasion",
        "task": "spoof TLS/HTTP protocol fingerprints to match specific clients and evade JA3/JA4/HTTP2 fingerprinting",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["ja3_hash", "tls_config"],
        "terms": ["JA3 fingerprint", "JA4", "cipher suite order", "HTTP/2 settings"],
        "traps": ["cipher order mismatch", "missing extensions", "inconsistent HTTP/2 frames"],
        "competencies": [
            ("evasion.ja3-match", "Match JA3/JA4 fingerprint to target client exactly.", ["JA3", "JA4", "cipher", "extension"]),
            ("evasion.http2-consistency", "Ensure HTTP/2 settings match target browser.", ["SETTINGS", "WINDOW_UPDATE", "PRIORITY"]),
            ("evasion.tls-extension-order", "Maintain correct TLS extension ordering.", ["extension", "order", "SNI", "ALPN"]),
        ],
        "failure_traps_list": [
            ("evasion.cipher-mismatch", "Cipher suite order doesn't match target JA3 hash."),
            ("evasion.missing-extension", "Missing TLS extensions that target client sends."),
        ],
    },
    "telemetry-blinding": {
        "role": "telemetry-specialist",
        "category": "evasion",
        "task": "blind or suppress host telemetry including ETW, Sysmon, AMSI, and Windows event logging",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["etw_patch", "amsi_bypass"],
        "terms": ["ETW provider", "Sysmon filter", "AMSI patch", "event log"],
        "traps": ["incomplete provider list", "detectable patch", "no verification"],
        "competencies": [
            ("evasion.provider-enumeration", "Enumerate all active ETW providers before blinding.", ["ETW", "provider", "enumerate"]),
            ("evasion.amsi-bypass", "Bypass AMSI without detectable memory patches.", ["AMSI", "AmsiScanBuffer", "patch"]),
            ("evasion.verification", "Verify telemetry is actually suppressed after blinding.", ["verify", "event", "suppressed"]),
        ],
        "failure_traps_list": [
            ("evasion.partial-blind", "Only blinding some telemetry providers while others report."),
            ("evasion.no-verify", "Not verifying telemetry suppression after patching."),
        ],
    },
    "terminal-operator-ui": {
        "role": "tui-developer",
        "category": "engineering",
        "task": "build terminal-based operator UIs using curses, Rich, Textual, or similar TUI frameworks",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["App", "Screen", "Widget"],
        "terms": ["TUI framework", "keybinding", "live update", "responsive layout"],
        "traps": ["blocking input loop", "no resize handling", "missing keybinding docs"],
        "competencies": [
            ("engineering.responsive-tui", "Handle terminal resize events gracefully.", ["resize", "SIGWINCH", "responsive"]),
            ("engineering.keybind-map", "Document all keybindings and provide help screen.", ["keybind", "help", "shortcut"]),
            ("engineering.live-refresh", "Implement non-blocking live data refresh.", ["live", "refresh", "async", "polling"]),
        ],
        "failure_traps_list": [
            ("engineering.blocking-input", "Blocking input loop preventing live updates."),
            ("engineering.no-resize", "Crashing or garbling on terminal resize."),
        ],
    },
    "windows-native-internals": {
        "role": "windows-internals-specialist",
        "category": "engineering",
        "task": "work with Windows NT internals including undocumented APIs, PEB/TEB structures, kernel objects, and system information classes",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["PEB", "TEB", "NtQuerySystemInformation"],
        "terms": ["PEB walk", "TEB access", "SYSTEM_INFORMATION_CLASS", "kernel object"],
        "traps": ["wrong struct offset for OS version", "undocumented API without fallback", "no version check"],
        "competencies": [
            ("engineering.struct-versioning", "Verify struct offsets against target OS build number.", ["PEB", "offset", "build number"]),
            ("engineering.fallback-path", "Provide fallback when undocumented API changes.", ["fallback", "documented", "alternative"]),
            ("engineering.version-gating", "Gate behavior on OS version/build number.", ["version", "build", "IsWindows10OrGreater"]),
        ],
        "failure_traps_list": [
            ("engineering.wrong-offset", "Using struct offset from wrong OS version."),
            ("engineering.no-fallback", "No fallback path for undocumented API."),
        ],
    },
}


def generate_competencies_json(skill_name: str, meta: dict) -> str:
    now = datetime.now(timezone.utc).isoformat()
    data = {
        "schema_version": "relay-kit.skill-competency.v1",
        "skill": skill_name,
        "role": meta["role"],
        "category": meta["category"],
        "core_competencies": [
            {
                "id": c[0],
                "label": c[1],
                "evidence_terms": c[2],
                "archetypes": [meta["category"]],
            }
            for c in meta["competencies"]
        ],
        "failure_traps": [
            {"id": ft[0], "description": ft[1]}
            for ft in meta["failure_traps_list"]
        ],
        "unknown_domain_policy": "scout_first_without_expert_claim",
        "claim_policy": "competency-covered only when every core competency is present and battle evidence passes.",
        "generated_at": now,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def generate_evals_json(skill_name: str, meta: dict) -> str:
    cases = [
        {
            "id": f"{skill_name}-battle-read-first",
            "skill": skill_name,
            "repo_profile": f"Relay-kit offensive tool pack with {skill_name} skill",
            "task": f"{meta['task']}. Use `{skill_name}` and cite the first files before advice.",
            "expected_files": meta["files"],
            "expected_symbols": meta["symbols"],
            "expected_tests": [f"tests/test_{skill_name.replace('-', '_')}.py"],
            "expected_evidence_terms": meta["terms"],
            "bad_answer_traps": meta["traps"],
        },
        {
            "id": f"{skill_name}-deep-weakness-trap",
            "skill": skill_name,
            "repo_profile": f"deep relay suite fixture with {skill_name} domain expertise",
            "task": f"Score `{skill_name}` against a deep battle case, identify weak evidence, and avoid claiming maximum strength until files, symbols, tests, and residual risk are proven.",
            "expected_files": meta["files"],
            "expected_symbols": meta["symbols"],
            "expected_tests": [f"tests/test_{skill_name.replace('-', '_')}.py"],
            "expected_evidence_terms": meta["terms"] + ["residual risk", "weak evidence"],
            "bad_answer_traps": ["looks like", "usual checklist", "battle-max-on-suite without proof"],
        },
    ]
    return json.dumps(cases, indent=2, ensure_ascii=False)


def generate_operator_contract(skill_name: str, meta: dict) -> str:
    return f"""# {skill_name} Battle Contract

Primary role: {meta['role']}
Layer: layer-4-specialists-and-standalones
Battle family: offensive-tool-pack

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: Relay-kit offensive tool pack with {skill_name} domain expertise
- First files to inspect: {', '.join(meta['files'])}
- Symbols or named surfaces to confirm: {', '.join(meta['symbols'])}
- Evidence terms that should appear in a strong answer: {', '.join(meta['terms'])}

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, docs, release, routing, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Guessing from the skill name without opening files.
- Treating a checklist as proof.
- Saying a change is ready when tests, generated adapters, docs, or safety scans were not checked.
- Hiding that a public repo benchmark is read-only and not user adoption proof.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, static scan, route score, benchmark hit, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or CLI gate when another lane should continue.
"""


def generate_good_output(skill_name: str, meta: dict) -> str:
    return f"""# {skill_name} Battle-Calibrated Output

Request: {meta['task']}

Recommended skill: `{skill_name}` because the request matches `{meta['role']}` work and has concrete repo anchors.

Read first:

{chr(10).join(f'- `{f}`' for f in meta['files'])}

Evidence gathered:

- Confirmed `{meta['symbols'][0]}` or nearby ownership before recommending changes.
- Checked `{meta['terms'][0]}` and `{meta['terms'][1]}` against the relevant source path.
- Identified `{meta['terms'][2]}` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `{meta['terms'][-1]}` remains unverified until the focused gate or benchmark hit is captured.
"""


def generate_bad_output(skill_name: str, meta: dict) -> str:
    return f"""# {skill_name} Weak Output Anti-Example

Request: {meta['task']}

Weak answer:

This looks like `{skill_name}`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `Relay-kit offensive tool pack with {skill_name} domain expertise` was inspected.
- No symbol such as `{meta['symbols'][0]}` was confirmed.
- No proof surface was named for `{meta['terms'][0]}`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
"""


def generate_for_skill(skill_name: str):
    meta = SKILL_META[skill_name]
    source_skill_path = REPO / ".agent" / "skills" / skill_name / "SKILL.md"

    if not source_skill_path.exists():
        print(f"  SKIP {skill_name}: SKILL.md not found in .agent/skills/")
        return

    skill_md_content = source_skill_path.read_text(encoding="utf-8")

    for adapter in ADAPTERS:
        adapter_skill_dir = REPO / adapter / "skills" / skill_name
        adapter_skill_dir.mkdir(parents=True, exist_ok=True)

        # Write SKILL.md
        (adapter_skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

        # competencies/
        comp_dir = adapter_skill_dir / "competencies"
        comp_dir.mkdir(exist_ok=True)
        (comp_dir / f"{skill_name}-competencies.json").write_text(
            generate_competencies_json(skill_name, meta), encoding="utf-8"
        )

        # evals/
        evals_dir = adapter_skill_dir / "evals"
        evals_dir.mkdir(exist_ok=True)
        (evals_dir / f"{skill_name}-cases.json").write_text(
            generate_evals_json(skill_name, meta), encoding="utf-8"
        )

        # examples/
        examples_dir = adapter_skill_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        (examples_dir / f"{skill_name}-good-output.md").write_text(
            generate_good_output(skill_name, meta), encoding="utf-8"
        )
        (examples_dir / f"{skill_name}-bad-output.md").write_text(
            generate_bad_output(skill_name, meta), encoding="utf-8"
        )

        # references/
        refs_dir = adapter_skill_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        (refs_dir / f"{skill_name}-operator-contract.md").write_text(
            generate_operator_contract(skill_name, meta), encoding="utf-8"
        )

    print(f"  OK {skill_name}: generated for {', '.join(ADAPTERS)}")


def main():
    print(f"Generating offensive tool pack for {len(OFFENSIVE_SKILLS)} skills...")
    print(f"Adapters: {', '.join(ADAPTERS)}")
    print()

    for skill_name in OFFENSIVE_SKILLS:
        generate_for_skill(skill_name)

    print()
    print(f"Done. {len(OFFENSIVE_SKILLS)} skills x {len(ADAPTERS)} adapters = {len(OFFENSIVE_SKILLS) * len(ADAPTERS)} skill directories generated.")
    print(f"Each directory contains: SKILL.md, competencies/, evals/, examples/, references/")


if __name__ == "__main__":
    main()
