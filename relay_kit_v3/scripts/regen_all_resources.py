"""
Regenerate all 31 skill resource files to pass test_skill_resources.py:
- core_competencies >= 5
- failure_traps >= 2
- cases >= 3
- expected_evidence_terms >= 3
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ALL_31 = [
    # 23 offensive
    "advanced-python-engineering","antibot-challenge-solving","attack-chain-orchestration",
    "binary-reverse-methodology","binary-stealth-obfuscation","browser-fingerprint-engineering",
    "cpp-systems-engineering","desktop-imgui-development","desktop-python-ui",
    "edr-evasion-tactics","field-journal-evolution","frontend-crypto-reverse",
    "malware-analysis-workflows","mmo-llm-automation","mmo-onchain-security-audit",
    "mobile-app-reverse","network-stealth-c2","offensive-security-engagement",
    "process-injection-techniques","protocol-fingerprint-spoofing","telemetry-blinding",
    "terminal-operator-ui","windows-native-internals",
    # 8 entrypoint
    "brainstorm","build-it","debug-systematically","prove-it","ready-check","review-pr","start-here","write-steps",
]

SKILL_META = {
    "advanced-python-engineering": {
        "role": "python-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["asyncio", "ctypes", "cffi", "MetaClass"],
        "terms": ["async model", "ctypes signature", "error hierarchy", "version pin", "event loop"],
        "traps": ["no version pin", "mixed async/sync", "missing C header doc"],
        "task": "implement advanced Python patterns including async I/O, ctypes/cffi interop, metaprogramming, and C extension modules",
        "comps": [
            ("engineering.async-discipline", "Declare async model and identify cancellation points.", ["asyncio", "trio", "cancellation"]),
            ("engineering.interop-safety", "Document ctypes/cffi signatures with original C headers.", ["ctypes", "cffi", "calling convention"]),
            ("engineering.error-hierarchy", "Define recoverable vs fatal exception hierarchy.", ["exception", "recoverable", "fatal"]),
            ("engineering.dependency-pins", "Pin all external dependency versions.", ["version", "pin", "requirements"]),
            ("engineering.type-hints", "Use type hints on all public interfaces.", ["type hint", "annotation", "mypy"]),
            ("engineering.test-coverage", "Verify implementation with focused unit and integration tests.", ["test", "coverage", "pytest"]),
        ],
        "traps_list": [
            ("engineering.mixed-async-sync", "Mixed async and sync I/O in the same call chain without explicit bridging."),
            ("engineering.floating-deps", "Floating dependency versions causing reproducibility failures."),
            ("engineering.no-type-hints", "Missing type hints on public API surfaces."),
        ],
    },
    "antibot-challenge-solving": {
        "role": "antibot-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["challenge_solver", "captcha", "turnstile", "datadome"],
        "terms": ["challenge type", "solver strategy", "behavioral bypass", "token extraction", "fallback"],
        "traps": ["brute force without analysis", "hardcoded selectors", "no fallback strategy"],
        "task": "solve or bypass antibot challenges including CAPTCHAs, Cloudflare Turnstile, Datadome, and behavioral verification",
        "comps": [
            ("evasion.challenge-classification", "Classify challenge type before attempting solution.", ["challenge", "CAPTCHA", "JS challenge"]),
            ("evasion.solver-strategy", "Select appropriate solver based on challenge analysis.", ["solver", "strategy", "fallback"]),
            ("evasion.token-extraction", "Extract and validate challenge response tokens.", ["token", "response", "validation"]),
            ("evasion.behavioral-timing", "Match human-like timing patterns to avoid behavioral detection.", ["timing", "delay", "human"]),
            ("evasion.fingerprint-consistency", "Maintain consistent fingerprint during challenge solving.", ["fingerprint", "canvas", "WebGL"]),
        ],
        "traps_list": [
            ("evasion.brute-force", "Attempting brute force without analyzing the challenge type."),
            ("evasion.no-fallback", "No fallback strategy when primary solver fails."),
            ("evasion.static-selectors", "Using hardcoded CSS selectors that break with DOM changes."),
        ],
    },
    "attack-chain-orchestration": {
        "role": "attack-chain-planner", "category": "offensive",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["attack_chain", "phase_order", "engagement_proof", "ATT_CK"],
        "terms": ["ATT&CK phase", "kill chain", "OPSEC ordering", "phase transition", "engagement proof"],
        "traps": ["skip recon phase", "no OPSEC check between phases", "unordered execution"],
        "task": "orchestrate multi-phase authorized attack chains following ATT&CK framework with OPSEC discipline",
        "comps": [
            ("offensive.phase-ordering", "Follow ATT&CK kill chain ordering strictly.", ["ATT&CK", "kill chain", "phase"]),
            ("offensive.opsec-gates", "Enforce OPSEC checks between phase transitions.", ["OPSEC", "transition", "gate"]),
            ("offensive.evidence-chain", "Maintain evidence chain across all phases.", ["evidence", "chain", "artifact"]),
            ("offensive.authorization-first", "Verify engagement proof before any offensive action.", ["authorization", "proof", "scope"]),
            ("offensive.cleanup-planning", "Plan cleanup and removal for each phase.", ["cleanup", "removal", "persistence"]),
        ],
        "traps_list": [
            ("offensive.skip-recon", "Skipping reconnaissance phase before initial access."),
            ("offensive.no-opsec-gate", "No OPSEC validation between attack phases."),
            ("offensive.no-cleanup-plan", "No cleanup or removal plan for deployed artifacts."),
        ],
    },
    "binary-reverse-methodology": {
        "role": "reverse-engineer", "category": "reverse-engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["disassembly", "decompiler", "IDA", "ghidra"],
        "terms": ["static analysis", "dynamic analysis", "control flow", "function boundary", "call graph"],
        "traps": ["skip static before dynamic", "no function boundary map", "guessing without evidence"],
        "task": "systematically reverse-engineer binary executables using static and dynamic analysis techniques",
        "comps": [
            ("reverse.static-first", "Perform static analysis before dynamic analysis.", ["static", "disassembly", "strings"]),
            ("reverse.function-map", "Map function boundaries and call graph before deep analysis.", ["function", "call graph", "boundary"]),
            ("reverse.hypothesis-driven", "Form and test hypotheses about binary behavior.", ["hypothesis", "test", "verify"]),
            ("reverse.anti-analysis", "Identify and neutralize anti-analysis techniques.", ["anti-debug", "obfuscation", "packing"]),
            ("reverse.protocol-reconstruction", "Reconstruct network protocol or data format from binary.", ["protocol", "format", "struct"]),
        ],
        "traps_list": [
            ("reverse.dynamic-first", "Jumping to dynamic analysis without static analysis context."),
            ("reverse.guess-without-evidence", "Guessing binary behavior without disassembly evidence."),
            ("reverse.ignore-anti-analysis", "Not checking for anti-analysis techniques before debugging."),
        ],
    },
    "binary-stealth-obfuscation": {
        "role": "obfuscation-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["obfuscator", "packer", "mutation", "entropy"],
        "terms": ["entropy control", "signature evasion", "packing", "mutation engine", "YARA rule"],
        "traps": ["high entropy without justification", "no AV test", "single technique only"],
        "task": "obfuscate binary payloads to evade static analysis, AV/EDR signatures, and YARA rules",
        "comps": [
            ("evasion.entropy-control", "Control binary entropy to avoid statistical detection.", ["entropy", "histogram", "section"]),
            ("evasion.signature-mutation", "Mutate signatures to evade pattern matching.", ["signature", "mutation", "YARA"]),
            ("evasion.av-testing", "Test against AV engines before deployment.", ["AV", "test", "detection rate"]),
            ("evasion.import-obfuscation", "Obfuscate import table to avoid API-based detection.", ["import", "IAT", "hash"]),
            ("evasion.string-encryption", "Encrypt or encode strings to avoid string-based detection.", ["string", "encrypt", "XOR"]),
        ],
        "traps_list": [
            ("evasion.high-entropy", "Producing high-entropy output that triggers statistical detection."),
            ("evasion.untested-payload", "Deploying without AV/EDR testing."),
            ("evasion.clear-imports", "Leaving IAT intact exposing suspicious API calls."),
        ],
    },
    "browser-fingerprint-engineering": {
        "role": "browser-fingerprint-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["canvas_fingerprint", "webgl_hash", "audiocontext", "navigator"],
        "terms": ["canvas hash", "WebGL renderer", "AudioContext", "font enumeration", "navigator consistency"],
        "traps": ["inconsistent fingerprint components", "detectable spoofing", "missing navigator props"],
        "task": "engineer consistent browser fingerprints to defeat canvas, WebGL, AudioContext, and behavioral fingerprinting",
        "comps": [
            ("evasion.fingerprint-consistency", "Ensure all fingerprint components are internally consistent.", ["canvas", "WebGL", "AudioContext", "navigator"]),
            ("evasion.spoof-detection", "Verify spoofed fingerprints are not detectable as spoofed.", ["detection", "consistency", "entropy"]),
            ("evasion.behavioral-mimicry", "Mimic real user behavioral patterns.", ["mouse", "keyboard", "scroll", "timing"]),
            ("evasion.font-enumeration", "Control font enumeration to match target browser profile.", ["font", "enumeration", "metric"]),
            ("evasion.timezone-locale", "Set timezone, locale, and language to match fingerprint profile.", ["timezone", "locale", "language"]),
        ],
        "traps_list": [
            ("evasion.inconsistent-fp", "Fingerprint components contradict each other."),
            ("evasion.detectable-spoof", "Spoofed values are detectable by integrity checks."),
            ("evasion.wrong-font-set", "Font list doesn't match target OS/browser combination."),
        ],
    },
    "cpp-systems-engineering": {
        "role": "cpp-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["NtApi", "HANDLE", "DWORD", "RAII"],
        "terms": ["Win32 API", "NT internals", "memory layout", "calling convention", "RAII"],
        "traps": ["no error checking on API calls", "memory leak", "wrong calling convention"],
        "task": "implement systems-level C++ for Windows native APIs, memory management, and kernel-adjacent code",
        "comps": [
            ("engineering.api-error-check", "Check return values for every Win32/NT API call.", ["GetLastError", "NTSTATUS", "return value"]),
            ("engineering.memory-safety", "Prevent leaks and UAF in manual memory management.", ["RAII", "leak", "use-after-free"]),
            ("engineering.abi-correctness", "Use correct calling conventions and struct alignment.", ["stdcall", "cdecl", "alignment"]),
            ("engineering.handle-discipline", "Properly close handles and release resources in all exit paths.", ["CloseHandle", "RAII", "destructor"]),
            ("engineering.exception-safety", "Ensure exception safety in constructors and destructors.", ["exception", "noexcept", "destructor"]),
        ],
        "traps_list": [
            ("engineering.unchecked-api", "Ignoring return values from system API calls."),
            ("engineering.memory-leak", "Allocating without corresponding deallocation path."),
            ("engineering.handle-leak", "Failing to close handles in all exit paths."),
        ],
    },
    "desktop-imgui-development": {
        "role": "imgui-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["ImGui", "ImVec2", "ImGuiWindowFlags", "ImDrawList"],
        "terms": ["render loop", "overlay", "input handling", "widget layout", "ImDrawList"],
        "traps": ["blocking render loop", "no input passthrough", "missing cleanup"],
        "task": "build desktop overlay and tool UIs using Dear ImGui with DirectX/OpenGL backends",
        "comps": [
            ("engineering.render-loop", "Implement non-blocking render loop with proper frame timing.", ["frame", "vsync", "delta time"]),
            ("engineering.overlay-transparency", "Configure transparent overlay with click-through.", ["overlay", "transparent", "passthrough"]),
            ("engineering.imgui-state", "Manage ImGui widget state and ID stack correctly.", ["ID", "PushID", "state"]),
            ("engineering.backend-init", "Initialize backend (D3D/GL) and clean up in all paths.", ["backend", "D3D11", "OpenGL"]),
            ("engineering.hotkey-system", "Implement configurable hotkey system for operator control.", ["hotkey", "VK", "toggle"]),
        ],
        "traps_list": [
            ("engineering.blocking-render", "Blocking the render loop with synchronous operations."),
            ("engineering.no-cleanup", "Missing ImGui/backend cleanup on shutdown."),
            ("engineering.id-collision", "Widget ID collisions causing incorrect state."),
        ],
    },
    "desktop-python-ui": {
        "role": "python-ui-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["QApplication", "MainWindow", "QThread", "Signal"],
        "terms": ["event loop", "signal-slot", "widget tree", "threading model", "layout manager"],
        "traps": ["UI updates from worker thread", "blocking event loop", "no error dialog"],
        "task": "build desktop Python GUI applications using PyQt6/PySide6, Tkinter, or wxPython",
        "comps": [
            ("engineering.event-loop", "Keep the UI event loop responsive.", ["event loop", "responsive", "non-blocking"]),
            ("engineering.thread-safety", "Never update UI from worker threads directly.", ["thread", "signal", "invoke"]),
            ("engineering.layout-discipline", "Use layout managers instead of absolute positioning.", ["layout", "grid", "box"]),
            ("engineering.error-display", "Show user-facing error dialogs for all unexpected failures.", ["error", "dialog", "QMessageBox"]),
            ("engineering.resource-cleanup", "Properly close connections and clean up resources on exit.", ["cleanup", "close", "destructor"]),
        ],
        "traps_list": [
            ("engineering.ui-from-thread", "Updating UI widgets directly from a background thread."),
            ("engineering.blocking-loop", "Blocking the event loop with synchronous I/O."),
            ("engineering.silent-error", "Catching exceptions silently without user notification."),
        ],
    },
    "edr-evasion-tactics": {
        "role": "edr-evasion-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["syscall_stub", "unhook", "SSN", "AMSI"],
        "terms": ["userland hook", "direct syscall", "ETW patch", "callback removal", "SSN"],
        "traps": ["incomplete unhook", "wrong syscall number", "detectable ETW patch"],
        "task": "evade EDR detection through unhooking, direct syscalls, ETW patching, and callback manipulation",
        "comps": [
            ("evasion.syscall-correctness", "Use correct syscall numbers for target OS version.", ["syscall", "SSN", "version"]),
            ("evasion.unhook-completeness", "Unhook all monitored APIs, not just common ones.", ["unhook", "ntdll", "IAT"]),
            ("evasion.etw-blinding", "Blind ETW without detectable patching artifacts.", ["ETW", "patch", "blind"]),
            ("evasion.callback-removal", "Remove security product callbacks from kernel list.", ["callback", "kernel", "PsSetCreateProcessNotifyRoutine"]),
            ("evasion.stack-spoofing", "Spoof call stack to avoid stack-based detection.", ["stack", "spoof", "return address"]),
        ],
        "traps_list": [
            ("evasion.wrong-ssn", "Using wrong syscall service number for the target OS build."),
            ("evasion.partial-unhook", "Unhooking only common APIs while leaving others monitored."),
            ("evasion.detectable-etw", "ETW patch leaves detectable byte sequence."),
        ],
    },
    "field-journal-evolution": {
        "role": "knowledge-writeback", "category": "meta",
        "files": ["relay_kit_v3/field_journal.py", "relay_kit_v3/evidence_quality.py"],
        "symbols": ["capture_entry", "evidence_ref", "journal_append", "confidence"],
        "terms": ["evidence ref", "confidence level", "pattern capture", "journal append", "candidate status"],
        "traps": ["entry without evidence", "auto-promote", "duplicate pattern"],
        "task": "evolve field journal by capturing pitfalls, techniques, and routing gaps with evidence backing",
        "comps": [
            ("meta.evidence-gating", "Never write journal entry without evidence reference.", ["evidence", "ref", "hash"]),
            ("meta.no-auto-promote", "Never auto-promote entries; require human approval.", ["candidate", "promote", "human"]),
            ("meta.dedup-check", "Check for duplicate patterns before capturing.", ["duplicate", "existing", "signature"]),
            ("meta.confidence-labeling", "Label confidence level explicitly on every entry.", ["confidence", "low", "medium"]),
            ("meta.pattern-classification", "Classify entry as pitfall, technique, routing-gap, or discovery.", ["pitfall", "technique", "routing-gap"]),
        ],
        "traps_list": [
            ("meta.no-evidence", "Writing journal entry without evidence_ref."),
            ("meta.auto-promote", "Automatically promoting entry without human approval."),
            ("meta.wrong-classification", "Misclassifying entry type causing incorrect retrieval."),
        ],
    },
    "frontend-crypto-reverse": {
        "role": "crypto-reverse-specialist", "category": "reverse-engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["crypto_params", "wasm_decode", "deobfuscate", "HMAC"],
        "terms": ["JS deobfuscation", "WASM reverse", "signing algorithm", "key extraction", "replay test"],
        "traps": ["assuming algorithm without proof", "missing key rotation", "no replay test"],
        "task": "reverse client-side cryptography, obfuscated JavaScript, WASM modules, and API signing parameters",
        "comps": [
            ("reverse.deobfuscation", "Systematically deobfuscate JavaScript before analysis.", ["deobfuscate", "AST", "control flow"]),
            ("reverse.algorithm-id", "Identify cryptographic algorithm from implementation patterns.", ["algorithm", "HMAC", "AES", "RSA"]),
            ("reverse.key-extraction", "Extract signing keys and rotation schedule.", ["key", "rotation", "extraction"]),
            ("reverse.wasm-analysis", "Analyze WASM modules for crypto logic.", ["WASM", "binary", "module"]),
            ("reverse.replay-verification", "Verify signing logic by replaying captured requests.", ["replay", "request", "verify"]),
        ],
        "traps_list": [
            ("reverse.assumed-algo", "Assuming crypto algorithm without evidence from code."),
            ("reverse.no-replay", "Not testing replayed requests to verify signing logic."),
            ("reverse.missed-key-rotation", "Not accounting for key rotation schedule."),
        ],
    },
    "malware-analysis-workflows": {
        "role": "malware-analyst", "category": "reverse-engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["sandbox_run", "ioc_extract", "yara_rule", "behavioral_report"],
        "terms": ["IOC extraction", "sandbox analysis", "behavioral pattern", "YARA rule", "network indicators"],
        "traps": ["running on host", "no network isolation", "incomplete IOC list"],
        "task": "analyze malware samples using sandbox, static, dynamic, and behavioral analysis workflows",
        "comps": [
            ("reverse.sandbox-isolation", "Always analyze in isolated sandbox environment.", ["sandbox", "VM", "isolation"]),
            ("reverse.ioc-completeness", "Extract complete IOC set including network, file, and registry.", ["IOC", "network", "file", "registry"]),
            ("reverse.yara-authoring", "Write YARA rules from identified patterns.", ["YARA", "rule", "pattern"]),
            ("reverse.behavioral-timeline", "Build behavioral timeline from sandbox report.", ["timeline", "behavioral", "sequence"]),
            ("reverse.c2-identification", "Identify C2 infrastructure from network indicators.", ["C2", "beacon", "domain"]),
        ],
        "traps_list": [
            ("reverse.host-execution", "Executing malware sample on analysis host."),
            ("reverse.incomplete-ioc", "Missing IOC categories in extraction."),
            ("reverse.no-yara", "Not authoring YARA rule after identifying unique patterns."),
        ],
    },
    "mmo-llm-automation": {
        "role": "llm-automation-specialist", "category": "automation",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["llm_client", "variance_engine", "prompt_template", "batch_generate"],
        "terms": ["prompt diversity", "behavioral variance", "content generation", "Sybil evasion", "rate limit"],
        "traps": ["identical outputs", "no rate limiting", "detectable patterns"],
        "task": "integrate LLM APIs for bulk content generation, behavioral variance, and Sybil evasion in MMO operations",
        "comps": [
            ("automation.prompt-diversity", "Generate diverse prompts to avoid pattern detection.", ["prompt", "diversity", "template"]),
            ("automation.rate-discipline", "Respect API rate limits and implement backoff.", ["rate", "limit", "backoff"]),
            ("automation.output-variance", "Ensure output variance across generated content.", ["variance", "unique", "fingerprint"]),
            ("automation.quality-filter", "Filter low-quality outputs before publishing.", ["quality", "filter", "threshold"]),
            ("automation.cost-tracking", "Track LLM API costs per operation.", ["cost", "tokens", "budget"]),
        ],
        "traps_list": [
            ("automation.identical-output", "Producing identical content across multiple accounts."),
            ("automation.no-rate-limit", "Ignoring API rate limits."),
            ("automation.no-quality-filter", "Publishing LLM output without quality check."),
        ],
    },
    "mmo-onchain-security-audit": {
        "role": "onchain-auditor", "category": "security",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["contract_audit", "reentrancy_check", "access_control", "gas_analysis"],
        "terms": ["reentrancy", "front-running", "access control", "integer overflow", "gas analysis"],
        "traps": ["skip reentrancy check", "no gas analysis", "unchecked external call"],
        "task": "audit on-chain scripts, smart contracts, and wallet automation for security vulnerabilities",
        "comps": [
            ("security.reentrancy-check", "Check for reentrancy vulnerabilities in all external calls.", ["reentrancy", "external call", "state change"]),
            ("security.access-control", "Verify access control on all privileged functions.", ["onlyOwner", "modifier", "access"]),
            ("security.gas-analysis", "Analyze gas costs and potential DoS through gas exhaustion.", ["gas", "loop", "DoS"]),
            ("security.integer-safety", "Check for integer overflow/underflow in arithmetic operations.", ["overflow", "underflow", "SafeMath"]),
            ("security.event-logging", "Verify critical state changes emit events for transparency.", ["event", "emit", "log"]),
        ],
        "traps_list": [
            ("security.missed-reentrancy", "Missing reentrancy check on external call."),
            ("security.no-access-control", "Privileged function without access control modifier."),
            ("security.unchecked-arithmetic", "Integer arithmetic without overflow protection."),
        ],
    },
    "mobile-app-reverse": {
        "role": "mobile-reverse-specialist", "category": "reverse-engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["apk_decompile", "ssl_unpin", "frida_hook", "jadx"],
        "terms": ["APK decompile", "IPA analysis", "SSL pinning", "API endpoint extraction", "Frida hook"],
        "traps": ["skip manifest analysis", "no root/jailbreak detection bypass", "incomplete API map"],
        "task": "reverse-engineer mobile APK/IPA apps to find API endpoints, signing keys, and certificate pinning",
        "comps": [
            ("reverse.manifest-analysis", "Analyze AndroidManifest.xml/Info.plist before code.", ["manifest", "permissions", "components"]),
            ("reverse.ssl-bypass", "Bypass SSL pinning for traffic interception.", ["SSL", "pinning", "Frida", "proxy"]),
            ("reverse.api-mapping", "Map all API endpoints from decompiled code.", ["API", "endpoint", "URL", "request"]),
            ("reverse.root-detection-bypass", "Bypass root/jailbreak detection checks.", ["root", "jailbreak", "detection"]),
            ("reverse.signing-key-extract", "Extract signing keys or certificate from app bundle.", ["signing", "key", "certificate"]),
        ],
        "traps_list": [
            ("reverse.skip-manifest", "Diving into code without analyzing app manifest."),
            ("reverse.incomplete-api", "Missing API endpoints in extraction."),
            ("reverse.no-root-bypass", "Not bypassing root detection before analysis."),
        ],
    },
    "network-stealth-c2": {
        "role": "c2-specialist", "category": "offensive",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["beacon_config", "redirector", "jitter", "domain_fronting"],
        "terms": ["domain fronting", "traffic blending", "jitter", "redirector chain", "beacon discipline"],
        "traps": ["fixed beacon interval", "no redirector", "plaintext C2 channel"],
        "task": "build C2 infrastructure with traffic blending, domain fronting, protocol mimicry, and beaconing discipline",
        "comps": [
            ("offensive.beacon-discipline", "Configure beacon with jitter and sleep variation.", ["beacon", "jitter", "sleep"]),
            ("offensive.traffic-blending", "Blend C2 traffic with legitimate protocols.", ["HTTPS", "DNS", "CDN", "blend"]),
            ("offensive.redirector-chain", "Use redirector chain to hide true C2 server.", ["redirector", "proxy", "CDN"]),
            ("offensive.protocol-mimicry", "Mimic legitimate protocol traffic patterns.", ["mimicry", "HTTP", "pattern"]),
            ("offensive.operator-security", "Protect operator infrastructure from attribution.", ["attribution", "VPN", "opsec"]),
        ],
        "traps_list": [
            ("offensive.fixed-interval", "Fixed beacon interval without jitter."),
            ("offensive.direct-c2", "Direct connection to C2 server without redirectors."),
            ("offensive.plaintext-channel", "Using unencrypted C2 communication channel."),
        ],
    },
    "offensive-security-engagement": {
        "role": "engagement-gate", "category": "offensive",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["engagement_proof", "risk_tier", "workflow_state", "ATT_CK"],
        "terms": ["engagement proof", "authorization", "ATT&CK phase", "risk tier", "lane mode"],
        "traps": ["proceed without authorization", "missing ATT&CK mapping", "own the lane"],
        "task": "gate offensive security lanes by verifying engagement proof and mapping ATT&CK phases",
        "comps": [
            ("offensive.authorization-gate", "Block all offensive work until engagement proof is cached.", ["authorization", "engagement", "proof"]),
            ("offensive.attack-mapping", "Map every offensive task to ATT&CK phase.", ["ATT&CK", "phase", "mapping"]),
            ("offensive.risk-annotation", "Annotate risk tier before specialist execution.", ["risk", "tier", "annotation"]),
            ("offensive.scope-enforcement", "Enforce engagement scope boundaries on every lane.", ["scope", "boundary", "in-scope"]),
            ("offensive.handoff-discipline", "Return control to calling hub after caching proof.", ["handoff", "return", "hub"]),
        ],
        "traps_list": [
            ("offensive.no-auth", "Proceeding with offensive techniques without engagement proof."),
            ("offensive.no-attack-map", "Skipping ATT&CK phase mapping."),
            ("offensive.lane-ownership", "Taking ownership of the lane instead of returning to hub."),
        ],
    },
    "process-injection-techniques": {
        "role": "injection-specialist", "category": "offensive",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["inject_dll", "hollow_process", "apc_inject", "thread_hijack"],
        "terms": ["DLL injection", "process hollowing", "APC queue", "thread context", "reflective loading"],
        "traps": ["wrong process architecture", "no cleanup on failure", "detectable allocation pattern"],
        "task": "implement process injection including DLL injection, process hollowing, APC injection, and thread hijacking",
        "comps": [
            ("offensive.arch-check", "Verify target process architecture before injection.", ["x86", "x64", "WoW64", "architecture"]),
            ("offensive.cleanup-on-fail", "Clean up allocated resources if injection fails.", ["cleanup", "VirtualFreeEx", "handle"]),
            ("offensive.alloc-stealth", "Use stealthy memory allocation patterns.", ["MEM_COMMIT", "PAGE_READWRITE", "RWX"]),
            ("offensive.technique-selection", "Select injection technique based on target process protections.", ["technique", "PPL", "Protected Process"]),
            ("offensive.pid-validation", "Validate target PID exists and is accessible before injection.", ["PID", "OpenProcess", "ACCESS_DENIED"]),
        ],
        "traps_list": [
            ("offensive.arch-mismatch", "Injecting into process with wrong architecture."),
            ("offensive.no-cleanup", "Leaving allocated memory on injection failure."),
            ("offensive.rwx-allocation", "Using RWX allocation that triggers security alerts."),
        ],
    },
    "protocol-fingerprint-spoofing": {
        "role": "protocol-fingerprint-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["ja3_hash", "tls_config", "cipher_suite", "http2_settings"],
        "terms": ["JA3 fingerprint", "JA4", "cipher suite order", "HTTP/2 settings", "TLS extension order"],
        "traps": ["cipher order mismatch", "missing extensions", "inconsistent HTTP/2 frames"],
        "task": "spoof TLS/HTTP protocol fingerprints to match specific clients and evade JA3/JA4 fingerprinting",
        "comps": [
            ("evasion.ja3-match", "Match JA3/JA4 fingerprint to target client exactly.", ["JA3", "JA4", "cipher", "extension"]),
            ("evasion.http2-consistency", "Ensure HTTP/2 settings match target browser.", ["SETTINGS", "WINDOW_UPDATE", "PRIORITY"]),
            ("evasion.tls-extension-order", "Maintain correct TLS extension ordering.", ["extension", "order", "SNI", "ALPN"]),
            ("evasion.alpn-selection", "Configure ALPN negotiation to match target profile.", ["ALPN", "h2", "http/1.1"]),
            ("evasion.session-ticket", "Handle TLS session tickets consistently with target.", ["session", "ticket", "resumption"]),
        ],
        "traps_list": [
            ("evasion.cipher-mismatch", "Cipher suite order doesn't match target JA3 hash."),
            ("evasion.missing-extension", "Missing TLS extensions that target client sends."),
            ("evasion.alpn-mismatch", "ALPN negotiation differs from target browser behavior."),
        ],
    },
    "telemetry-blinding": {
        "role": "telemetry-specialist", "category": "evasion",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["etw_patch", "amsi_bypass", "sysmon_filter", "event_log"],
        "terms": ["ETW provider", "Sysmon filter", "AMSI patch", "event log", "telemetry suppression"],
        "traps": ["incomplete provider list", "detectable patch", "no verification"],
        "task": "suppress or blind host telemetry including ETW, Sysmon, AMSI, and Windows event logging",
        "comps": [
            ("evasion.provider-enumeration", "Enumerate all active ETW providers before blinding.", ["ETW", "provider", "enumerate"]),
            ("evasion.amsi-bypass", "Bypass AMSI without detectable memory patches.", ["AMSI", "AmsiScanBuffer", "patch"]),
            ("evasion.verification", "Verify telemetry is actually suppressed after blinding.", ["verify", "event", "suppressed"]),
            ("evasion.sysmon-evasion", "Evade Sysmon rules for process and network events.", ["Sysmon", "rule", "process"]),
            ("evasion.eventlog-clearing", "Clear or filter Windows event log entries selectively.", ["event log", "clear", "filter"]),
        ],
        "traps_list": [
            ("evasion.partial-blind", "Only blinding some telemetry providers while others report."),
            ("evasion.no-verify", "Not verifying telemetry suppression after patching."),
            ("evasion.detectable-clear", "Clearing event logs in detectable way (log of log clearing)."),
        ],
    },
    "terminal-operator-ui": {
        "role": "tui-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["App", "Screen", "Widget", "rich_console"],
        "terms": ["TUI framework", "keybinding", "live update", "responsive layout", "Rich"],
        "traps": ["blocking input loop", "no resize handling", "missing keybinding docs"],
        "task": "build terminal-based operator UIs using Rich, Textual, or curses for automation dashboards and CLI tools",
        "comps": [
            ("engineering.responsive-tui", "Handle terminal resize events gracefully.", ["resize", "SIGWINCH", "responsive"]),
            ("engineering.keybind-map", "Document all keybindings and provide help screen.", ["keybind", "help", "shortcut"]),
            ("engineering.live-refresh", "Implement non-blocking live data refresh.", ["live", "refresh", "async", "polling"]),
            ("engineering.panel-layout", "Use panel and grid layout for structured display.", ["panel", "grid", "layout"]),
            ("engineering.color-coding", "Use consistent color coding for status and severity.", ["color", "status", "severity"]),
        ],
        "traps_list": [
            ("engineering.blocking-input", "Blocking input loop preventing live updates."),
            ("engineering.no-resize", "Crashing or garbling on terminal resize."),
            ("engineering.hardcoded-layout", "Hardcoded pixel positions instead of relative layout."),
        ],
    },
    "windows-native-internals": {
        "role": "windows-internals-specialist", "category": "engineering",
        "files": ["relay_kit_v3/registry/skills.py"],
        "symbols": ["PEB", "TEB", "NtQuerySystemInformation", "SSDT"],
        "terms": ["PEB walk", "TEB access", "SYSTEM_INFORMATION_CLASS", "kernel object", "SSDT"],
        "traps": ["wrong struct offset for OS version", "undocumented API without fallback", "no version check"],
        "task": "work with Windows NT internals including undocumented APIs, PEB/TEB structures, kernel objects, and SSDT",
        "comps": [
            ("engineering.struct-versioning", "Verify struct offsets against target OS build number.", ["PEB", "offset", "build number"]),
            ("engineering.fallback-path", "Provide fallback when undocumented API changes.", ["fallback", "documented", "alternative"]),
            ("engineering.version-gating", "Gate behavior on OS version/build number.", ["version", "build", "IsWindows10OrGreater"]),
            ("engineering.handle-inheritance", "Understand handle inheritance and duplication semantics.", ["handle", "inheritance", "DuplicateHandle"]),
            ("engineering.wow64-awareness", "Account for WoW64 differences in 32-bit on 64-bit Windows.", ["WoW64", "32-bit", "64-bit"]),
        ],
        "traps_list": [
            ("engineering.wrong-offset", "Using struct offset from wrong OS version."),
            ("engineering.no-fallback", "No fallback path for undocumented API."),
            ("engineering.wow64-blind", "Ignoring WoW64 differences when targeting both architectures."),
        ],
    },
    # 8 entrypoint skills - simpler domain-agnostic metadata
    "brainstorm": {
        "role": "specialist", "category": "ideation",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["brainstorm_hub", "workflow_router", "product_brief"],
        "terms": ["product brief", "ideation", "direction", "opportunity", "user segment"],
        "traps": ["giant feature list", "no user segment", "skip to planning"],
        "task": "turn a rough idea into a clear direction before implementation begins",
        "comps": [
            ("ideation.problem-framing", "Frame the core problem before generating solutions.", ["problem", "framing", "user"]),
            ("ideation.segment-definition", "Define target user segment and their jobs-to-be-done.", ["segment", "user", "jobs-to-be-done"]),
            ("ideation.opportunity-sizing", "Estimate opportunity size before committing to direction.", ["opportunity", "size", "priority"]),
            ("ideation.assumption-listing", "List key assumptions that could invalidate the idea.", ["assumption", "risk", "unknown"]),
            ("ideation.direction-choice", "End with a clear direction or stop decision.", ["direction", "stop", "decision"]),
        ],
        "traps_list": [
            ("ideation.feature-list", "Generating a giant feature wish list instead of bounded direction."),
            ("ideation.no-user-segment", "Missing target user segment in the output."),
            ("ideation.premature-plan", "Jumping to planning before direction is validated."),
        ],
    },
    "build-it": {
        "role": "specialist", "category": "implementation",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["developer", "execution_loop", "story", "tech_spec"],
        "terms": ["story", "tech-spec", "implementation", "evidence", "controlled scope"],
        "traps": ["skip story review", "no evidence gate", "unbounded scope"],
        "task": "implement an approved story or tech spec with controlled scope and evidence",
        "comps": [
            ("implementation.scope-control", "Keep edits bounded to the accepted story or fix.", ["scope", "changed files", "blast radius"]),
            ("implementation.context-before-edit", "Read relevant files, tests, and contracts before editing.", ["read first", "source files", "tests"]),
            ("implementation.test-evidence", "Tie completion to focused and risk-scaled verification.", ["test", "verification", "regression"]),
            ("implementation.rollback-note", "Name rollback or recovery path for risky changes.", ["rollback", "recovery", "residual risk"]),
            ("implementation.handoff-quality", "Produce a clear handoff with changed files and remaining risk.", ["handoff", "changed files", "risk"]),
        ],
        "traps_list": [
            ("implementation.edit-before-context", "Edits before reading the relevant source and tests."),
            ("implementation.completion-without-proof", "Says done without a command, artifact, or observed proof."),
            ("implementation.scope-creep", "Expanding scope beyond the accepted story boundaries."),
        ],
    },
    "debug-systematically": {
        "role": "specialist", "category": "debugging",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["debug_hub", "root_cause", "investigation_notes", "reproduction"],
        "terms": ["root cause", "reproduction", "investigation notes", "symptom", "evidence"],
        "traps": ["guess and patch", "no reproduction", "skip investigation notes"],
        "task": "debug a bug, regression, or mismatch using disciplined root-cause analysis",
        "comps": [
            ("debugging.reproduction-first", "Reproduce the issue before proposing fixes.", ["reproduce", "failing", "command"]),
            ("debugging.root-cause", "Identify root cause, not just symptoms.", ["root cause", "symptom", "cause"]),
            ("debugging.investigation-notes", "Write investigation notes with evidence and ruled-out causes.", ["investigation", "evidence", "ruled out"]),
            ("debugging.hypothesis-testing", "Test hypotheses systematically before implementing fix.", ["hypothesis", "probe", "test"]),
            ("debugging.fix-scope", "Bound the fix surface before implementing.", ["fix", "scope", "blast radius"]),
        ],
        "traps_list": [
            ("debugging.guess-patch", "Guessing at fixes without establishing root cause."),
            ("debugging.no-reproduction", "Proposing fixes without reproducing the issue."),
            ("debugging.symptom-not-cause", "Fixing symptoms without addressing root cause."),
        ],
    },
    "prove-it": {
        "role": "specialist", "category": "verification",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["evidence_before_completion", "claim", "proof", "qa_report"],
        "terms": ["evidence", "claim", "proof", "verification", "residual risk"],
        "traps": ["claim without proof", "skip verification", "self-assertion"],
        "task": "verify completion claims with one last evidence pass before calling work done",
        "comps": [
            ("verification.claim-mapping", "Map every completion claim to concrete evidence.", ["claim", "evidence", "proof"]),
            ("verification.command-proof", "Cite the exact command and output that proves the claim.", ["command", "output", "log"]),
            ("verification.residual-risk", "Name what is still unverified after evidence pass.", ["residual", "unverified", "risk"]),
            ("verification.no-self-assertion", "Never accept self-assertion as proof.", ["self-assertion", "proof", "evidence"]),
            ("verification.regression-check", "Verify no regressions introduced by the change.", ["regression", "existing", "test"]),
        ],
        "traps_list": [
            ("verification.self-assertion", "Accepting self-assertion as proof of completion."),
            ("verification.no-command-proof", "Missing command output to substantiate claims."),
            ("verification.hidden-residual", "Not naming what remains unverified after evidence pass."),
        ],
    },
    "ready-check": {
        "role": "specialist", "category": "readiness",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["qa_governor", "readiness_verdict", "go_nogo", "acceptance_criteria"],
        "terms": ["go/no-go", "readiness", "acceptance criteria", "QA report", "verdict"],
        "traps": ["green without criteria check", "skip QA report", "no explicit verdict"],
        "task": "make a real go or no-go readiness decision about code shipability",
        "comps": [
            ("readiness.criteria-check", "Verify all acceptance criteria are met before go decision.", ["acceptance", "criteria", "met"]),
            ("readiness.qa-report", "Produce or reference QA report with test results.", ["QA", "report", "test"]),
            ("readiness.explicit-verdict", "End with explicit go, no-go, or conditional verdict.", ["verdict", "go", "no-go"]),
            ("readiness.regression-surface", "Check regression surface against test coverage.", ["regression", "coverage", "test"]),
            ("readiness.risk-statement", "State residual risk with the readiness verdict.", ["risk", "residual", "statement"]),
        ],
        "traps_list": [
            ("readiness.no-criteria", "Declaring ready without checking acceptance criteria."),
            ("readiness.no-verdict", "Not providing explicit go/no-go verdict."),
            ("readiness.hidden-risk", "Not stating residual risk alongside readiness verdict."),
        ],
    },
    "review-pr": {
        "role": "specialist", "category": "review",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["review_hub", "pr_review", "branch", "merge"],
        "terms": ["branch review", "PR review", "code review", "merge criteria", "sign-off"],
        "traps": ["merge without review", "review without criteria", "skip regression check"],
        "task": "review a branch or PR before merge with evidence-backed sign-off",
        "comps": [
            ("review.criteria-driven", "Review against explicit acceptance criteria, not intuition.", ["criteria", "acceptance", "explicit"]),
            ("review.regression-check", "Check that existing tests still pass.", ["regression", "test", "pass"]),
            ("review.architecture-alignment", "Verify change aligns with existing architecture.", ["architecture", "alignment", "boundary"]),
            ("review.evidence-requirement", "Require evidence before sign-off, not just inspection.", ["evidence", "sign-off", "proof"]),
            ("review.explicit-verdict", "End with explicit merge/request-changes verdict.", ["merge", "request-changes", "verdict"]),
        ],
        "traps_list": [
            ("review.no-criteria", "Reviewing without checking acceptance criteria."),
            ("review.inspection-only", "Signing off based on code read without evidence."),
            ("review.no-verdict", "Not providing explicit merge or request-changes verdict."),
        ],
    },
    "start-here": {
        "role": "specialist", "category": "routing",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["workflow_router", "next_skill", "routing_kernel"],
        "terms": ["routing", "next skill", "track", "entrypoint", "workflow state"],
        "traps": ["skip routing", "no skill recommendation", "skip workflow state"],
        "task": "route a request to the right Relay-kit path, next skill, and artifact without guessing",
        "comps": [
            ("routing.intent-classification", "Classify request intent before recommending a path.", ["intent", "classify", "complexity"]),
            ("routing.skill-recommendation", "Recommend a specific next skill with reasoning.", ["skill", "recommend", "reason"]),
            ("routing.state-check", "Read workflow-state before routing.", ["workflow-state", "read", "context"]),
            ("routing.artifact-naming", "Name the artifact the next skill should create or update.", ["artifact", "create", "update"]),
            ("routing.track-selection", "Select quick-flow, product-flow, or enterprise-flow track.", ["track", "quick-flow", "product-flow"]),
        ],
        "traps_list": [
            ("routing.no-skill", "Not recommending a specific next skill."),
            ("routing.skip-state", "Routing without reading existing workflow state."),
            ("routing.vague-direction", "Giving vague process advice instead of next skill name."),
        ],
    },
    "write-steps": {
        "role": "specialist", "category": "planning",
        "files": ["relay_kit_v3/registry/skills.py", "relay_kit_public_cli.py"],
        "symbols": ["scrum_master", "story", "tech_spec", "implementation_step"],
        "terms": ["implementation steps", "verifiable", "buildable", "slicing", "done criteria"],
        "traps": ["steps without done criteria", "too large steps", "no verification signal"],
        "task": "slice approved work into small, buildable, verifiable implementation steps",
        "comps": [
            ("planning.step-size", "Keep steps small enough to complete in one focused pass.", ["small", "focused", "bounded"]),
            ("planning.done-criteria", "Every step must have explicit done criteria.", ["done", "criteria", "verification"]),
            ("planning.verification-signal", "Name the first verification command for each step.", ["verification", "command", "signal"]),
            ("planning.dependency-order", "Order steps by dependency, not by arbitrary sequence.", ["dependency", "order", "depends-on"]),
            ("planning.parallel-safety", "Mark which steps are safe to execute in parallel.", ["parallel", "safe", "wave"]),
        ],
        "traps_list": [
            ("planning.no-done-criteria", "Steps without explicit done criteria."),
            ("planning.too-large-step", "Steps that span multiple subsystems without decomposition."),
            ("planning.no-verification", "Missing first verification signal for each step."),
        ],
    },
}


def gen_competencies(skill_name, meta):
    now = datetime.now(timezone.utc).isoformat()
    return {
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
            for c in meta["comps"]
        ],
        "failure_traps": [
            {"id": ft[0], "description": ft[1]}
            for ft in meta["traps_list"]
        ],
        "unknown_domain_policy": "scout_first_without_expert_claim",
        "claim_policy": "competency-covered only when every core competency is present and battle evidence passes.",
        "generated_at": now,
    }


def gen_evals(skill_name, meta):
    """Generate 3 eval cases (test requires >= 3)"""
    return [
        {
            "id": f"{skill_name}-battle-read-first",
            "skill": skill_name,
            "repo_profile": f"Relay-kit offensive tool pack with {skill_name} domain expertise",
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
            "expected_evidence_terms": meta["terms"][:3] + ["residual risk", "weak evidence"],
            "bad_answer_traps": ["looks like", "usual checklist", "battle-max-on-suite without proof"],
        },
        {
            "id": f"{skill_name}-public-repo-benchmark-anchor",
            "skill": skill_name,
            "repo_profile": f"safe public repo benchmark clone; shallow, read-only, no install, no build, no tests",
            "task": f"Run a read-only battle benchmark style review for `{skill_name}` and explain what evidence is still missing.",
            "expected_files": meta["files"],
            "expected_symbols": meta["symbols"][:2],
            "expected_tests": [f"tests/test_{skill_name.replace('-', '_')}.py"],
            "expected_evidence_terms": meta["terms"][:3] + ["strict evidence", "read-only"],
            "bad_answer_traps": ["checklist only", "expert guarantee", "field-tested"],
        },
    ]


def gen_operator_contract(skill_name, meta):
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


def gen_good_output(skill_name, meta):
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


def gen_bad_output(skill_name, meta):
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


# Generate and write all files to BOTH locations:
# 1. relay_kit_v3/skill_resources/<skill>/  (for test_skill_resources.py)
# 2. .agent/skills/<skill>/  (for adapter parity)
# 3. .codex/skills/<skill>/  (for adapter parity)
# 4. .claude/skills/<skill>/  (for adapter parity)

ADAPTERS = [".agent", ".codex", ".claude"]

ok_count = 0
for skill_name in ALL_31:
    if skill_name not in SKILL_META:
        print(f"  SKIP {skill_name}: no meta")
        continue

    meta = SKILL_META[skill_name]
    comps_data = gen_competencies(skill_name, meta)
    evals_data = gen_evals(skill_name, meta)
    contract_text = gen_operator_contract(skill_name, meta)
    good_text = gen_good_output(skill_name, meta)
    bad_text = gen_bad_output(skill_name, meta)

    # Write to skill_resources (canonical source)
    res_root = REPO / "relay_kit_v3" / "skill_resources" / skill_name
    for subdir in ["competencies", "evals", "examples", "references"]:
        (res_root / subdir).mkdir(parents=True, exist_ok=True)

    (res_root / "competencies" / f"{skill_name}-competencies.json").write_text(
        json.dumps(comps_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (res_root / "evals" / f"{skill_name}-cases.json").write_text(
        json.dumps(evals_data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (res_root / "references" / f"{skill_name}-operator-contract.md").write_text(
        contract_text, encoding="utf-8"
    )
    (res_root / "examples" / f"{skill_name}-good-output.md").write_text(
        good_text, encoding="utf-8"
    )
    (res_root / "examples" / f"{skill_name}-bad-output.md").write_text(
        bad_text, encoding="utf-8"
    )

    # Sync to all 3 adapters
    for adapter in ADAPTERS:
        adapter_root = REPO / adapter / "skills" / skill_name
        for subdir in ["competencies", "evals", "examples", "references"]:
            src = res_root / subdir
            dst = adapter_root / subdir
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.iterdir():
                shutil.copy2(f, dst / f.name)

    ok_count += 1

print(f"\nDone: {ok_count}/{len(ALL_31)} skills regenerated with >= 5 competencies and >= 3 evals")
print(f"Resources written to: relay_kit_v3/skill_resources/ + .agent/ + .codex/ + .claude/")
