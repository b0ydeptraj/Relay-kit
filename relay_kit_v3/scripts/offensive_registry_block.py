
OFFENSIVE_TOOL_PACK_SKILLS: Dict[str, SkillSpec] = {
    "advanced-python-engineering": SkillSpec(
        name="advanced-python-engineering",
        description="Use when Python work requires advanced patterns: async I/O, ctypes/cffi interop, metaprogramming, C extension modules, performance optimization, or large-scale automation architecture.",
        role="python-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "story or tech-spec",
            "Python version target",
            "existing codebase if present",
        ],
        outputs=[
            "Python implementation",
            "dependency list",
            "error handling docs",
        ],
        references=[
            "Never mix async and sync I/O in the same call chain without explicit bridging.",
            "Document ctypes signatures with the original C header.",
            "Use type hints for all public interfaces.",
            "Pin dependency versions — floating requirements cause reproducibility failures.",
            "Open `references/advanced-python-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/advanced-python-engineering-good-output.md` and `examples/advanced-python-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/advanced-python-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/advanced-python-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "mmo-llm-automation",
            "mmo-http-api-automation",
            "antibot-challenge-solving",
            "terminal-operator-ui",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement robust, performant, and idiomatic Python for automation, interop, or large-scale scripting with explicit architecture and error discipline.
            
            ## Mandatory scope
            1. Declare Python version and async model (asyncio/trio/anyio or sync).
            2. For ctypes/cffi: document C signature, calling convention, and error propagation.
            3. For async: identify event loop, cancellation points, and timeout strategy.
            4. For metaprogramming: document __dunder__ contracts and descriptor protocol usage.
            5. Name external dependencies with version pins.
            6. Include error hierarchy: which exceptions are recoverable vs fatal.
            
            ## Evidence contract
            - Python version and async model declared
            - ctypes signatures documented with C source
            - Error hierarchy written explicitly
            - Dependency list with versions
            """
        ).strip(),
        allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
    ),
    "antibot-challenge-solving": SkillSpec(
        name="antibot-challenge-solving",
        description="Use when automation hits bot detection challenges: Cloudflare Turnstile/Bot Fight Mode, Datadome, PerimeterX, reCAPTCHA v2/v3/Enterprise, hCaptcha, or custom JS challenges.",
        role="antibot-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "challenge URL / challenge type",
            "automation context",
            "fingerprint profile if available",
        ],
        outputs=[
            "challenge bypass implementation",
            "clearance cookies or tokens",
            "verification result",
        ],
        references=[
            "Never call this skill from inside mmo-browser-fleet-automation — layer separation is mandatory.",
            "Document solve-rate throttle to protect API keys from bans.",
            "Verify bypass with actual HTTP response, not assumption.",
            "If challenge is unsolvable, escalate to protocol-fingerprint-spoofing or browser-fingerprint-engineering first.",
            "Open `references/antibot-challenge-solving-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/antibot-challenge-solving-good-output.md` and `examples/antibot-challenge-solving-bad-output.md` to calibrate output quality.",
            "Use `evals/antibot-challenge-solving-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/antibot-challenge-solving-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "browser-fingerprint-engineering",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Bypass or solve bot detection challenges while preserving automation flow integrity.
            
            ## Mandatory scope
            1. Identify challenge type: CAPTCHA (reCAPTCHA/hCaptcha/Turnstile), JS challenge (Cloudflare 5-second), behavioral score, or bot fingerprint gate.
            2. Choose solving approach:
               - CAPTCHA: 2captcha/CapMonster API (paid solver) or in-process ML model
               - JS challenge: Cloudflare clearance cookie via headless with correct fingerprint
               - Behavioral score: humanized interaction sequence
               - Fingerprint gate: protocol-fingerprint-spoofing + browser-fingerprint-engineering
            3. Rate limit: implement solve-rate throttle to avoid solver API bans.
            4. Layer separation: this skill is called from OUTSIDE mmo-browser-fleet-automation, not from inside (fleet has evasion prohibition rule).
            5. Verify bypass: HTTP 200 with expected content, no redirect to challenge page.
            
            ## Evidence contract
            - challenge type identified
            - solving approach documented
            - bypass verified (HTTP 200 or cookie extracted)
            - solve-rate throttle configured
            - layer separation from fleet maintained
            """
        ).strip(),
    ),
    "attack-chain-orchestration": SkillSpec(
        name="attack-chain-orchestration",
        description="Use when planning or orchestrating a multi-phase authorized attack chain: from initial recon through execution, persistence, lateral movement, collection, and cleanup.",
        role="attack-chain-planner",
        layer="layer-3-utility-providers",
        inputs=[
            "engagement scope and objective",
            "current foothold and constraints",
            "engagement_proof",
        ],
        outputs=[
            "attack chain plan (mermaid diagram)",
            "per-phase action list",
            "cleanup runbook",
        ],
        references=[
            "Never claim operation complete without cleanup verification.",
            "Every phase must have an alternative path if primary is blocked.",
            "OPSEC risk tier must be documented per action.",
            "engagement_proof required; block if missing.",
            "Open `references/attack-chain-orchestration-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/attack-chain-orchestration-good-output.md` and `examples/attack-chain-orchestration-bad-output.md` to calibrate output quality.",
            "Use `evals/attack-chain-orchestration-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/attack-chain-orchestration-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "offensive-security-engagement",
            "edr-evasion-tactics",
            "process-injection-techniques",
            "network-stealth-c2",
            "telemetry-blinding",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Plan and sequence an authorized multi-phase attack chain with explicit path planning, OPSEC discipline, and mandatory cleanup gate.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Map 7-phase kill chain: Recon -> Initial Access -> Execution -> Persistence -> Privilege Escalation -> Lateral Movement -> Collection/Exfil -> Cleanup.
            3. For each phase: current foothold + goal + constraints -> next 3 actions ranked by risk and detectability.
            4. Per-phase technique selection: call appropriate Phase 2+ specialists for implementation.
            5. Blocked-path replanning: if one path is blocked, automatically propose 2 alternatives.
            6. Cleanup-mandatory gate: do not claim operation complete until cleanup is verified.
            
            ## Evidence contract
            - engagement_proof confirmed
            - kill chain phases mapped with ATT&CK technique IDs
            - per-phase action ranking documented
            - cleanup plan written
            - blocked-path alternatives documented
            """
        ).strip(),
    ),
    "binary-reverse-methodology": SkillSpec(
        name="binary-reverse-methodology",
        description="Use when reverse engineering a binary: PE/ELF/Mach-O analysis, disassembly, decompilation, protocol reconstruction, anti-analysis bypass, or understanding undocumented behavior.",
        role="reverse-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "binary to analyze",
            "analysis goal (protocol / protection / behavior)",
            "engagement_proof if offensive sample",
        ],
        outputs=[
            "reverse engineering report",
            "annotated binary/IDB",
            "protocol or algorithm doc",
        ],
        references=[
            "Rename functions before writing the report — sub_XXXX references are not useful findings.",
            "Document anti-analysis techniques explicitly — they are often the most important finding.",
            "Protocol reconstruction requires both code analysis and traffic capture correlation.",
            "Decompiler output is pseudocode — verify against disassembly for critical paths.",
            "Open `references/binary-reverse-methodology-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/binary-reverse-methodology-good-output.md` and `examples/binary-reverse-methodology-bad-output.md` to calibrate output quality.",
            "Use `evals/binary-reverse-methodology-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/binary-reverse-methodology-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "malware-analysis-workflows",
            "binary-stealth-obfuscation",
            "frontend-crypto-reverse",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Systematically reverse engineer a binary to understand its behavior, protocol, or protection scheme.
            
            ## Mandatory scope
            1. Tool selection: IDA Pro / Ghidra / Binary Ninja / radare2 — document which and why.
            2. Entry point analysis: identify main, WinMain, TLS callbacks, anti-debug checks.
            3. Anti-analysis handling: detect and bypass anti-debug (IsDebuggerPresent, timing checks, checksum), anti-vm, and packer.
            4. Protocol reconstruction: if network binary, capture traffic and correlate with code paths.
            5. Function naming: rename identified functions before documenting — avoid generic sub_XXXX in reports.
            6. Document findings: algorithm identified, key material location, C2 protocol, persistence mechanism.
            
            ## Evidence contract
            - tool documented
            - entry point and anti-analysis techniques identified
            - anti-debug bypassed or documented
            - key findings renamed and documented
            - protocol or algorithm reconstructed
            """
        ).strip(),
    ),
    "binary-stealth-obfuscation": SkillSpec(
        name="binary-stealth-obfuscation",
        description="Use when a binary payload, shellcode, or PE needs to evade static analysis, signature detection, AV/EDR scanning, or YARA rules through obfuscation, packing, or mutation.",
        role="obfuscation-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "binary/shellcode/PE artifact",
            "target AV/EDR product if known",
            "engagement_proof from offensive-security-engagement",
        ],
        outputs=[
            "obfuscated binary",
            "detection surface analysis",
            "sandbox result",
        ],
        references=[
            "Never claim evasion without sandbox execution evidence.",
            "Entropy above 7.5 is a detection signal — document entropy control strategy.",
            "Preserve original behavior exactly — functionality must be verified after obfuscation.",
            "engagement_proof required; block if missing.",
            "Open `references/binary-stealth-obfuscation-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/binary-stealth-obfuscation-good-output.md` and `examples/binary-stealth-obfuscation-bad-output.md` to calibrate output quality.",
            "Use `evals/binary-stealth-obfuscation-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/binary-stealth-obfuscation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "process-injection-techniques",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Apply binary obfuscation techniques to reduce static signature surface while preserving correct runtime behavior.
            
            ## Mandatory scope
            1. Engagement proof required: confirm offensive-security-engagement has cached engagement_proof.
            2. Identify detection surface: YARA rules, PE header heuristics, import table, string patterns, entropy.
            3. Choose obfuscation approach: encryption (XOR/AES), packing, polymorphism, import obfuscation, section renaming.
            4. Verify runtime behavior preserved: test in isolated sandbox BEFORE claiming detection evasion.
            5. Document entropy delta: high entropy is itself a detection signal — balance obfuscation with entropy control.
            6. Cleanup gate: document how the obfuscated artifact is removed from target after use.
            
            ## Evidence contract
            - engagement_proof confirmed
            - detection surface identified (YARA rules, strings, imports)
            - sandbox execution result (behavior unchanged)
            - entropy delta documented
            - cleanup path written
            """
        ).strip(),
    ),
    "browser-fingerprint-engineering": SkillSpec(
        name="browser-fingerprint-engineering",
        description="Use when browser-based automation needs to defeat canvas fingerprinting, WebGL fingerprinting, AudioContext fingerprinting, font detection, or behavioral biometrics.",
        role="browser-fingerprint-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target platform fingerprint detection signals",
            "browser automation framework",
            "mmo-identity-infrastructure profile",
        ],
        outputs=[
            "fingerprint spoofing implementation",
            "consistency audit",
            "test site results",
        ],
        references=[
            "Never spoof values in isolation — all signals must be internally consistent.",
            "Dynamic noise must be per-session, not static — static noise is as detectable as no noise.",
            "Behavioral biometrics matter as much as technical fingerprints.",
            "Verify against test sites before deployment — assumption-based spoofing fails.",
            "Open `references/browser-fingerprint-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/browser-fingerprint-engineering-good-output.md` and `examples/browser-fingerprint-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/browser-fingerprint-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/browser-fingerprint-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "antibot-challenge-solving",
            "mmo-identity-infrastructure",
            "mmo-browser-fleet-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement code-level browser fingerprint spoofing that survives advanced platform behavioral analysis.
            
            ## Mandatory scope
            1. Map fingerprint vectors targeted by platform: Canvas, WebGL, AudioContext, fonts, navigator properties, screen resolution, timezone, battery API, device memory.
            2. Implement spoofing at the correct level: CDP override, JS injection before page load, custom browser build, or anti-detect browser configuration.
            3. Consistency rule: all spoofed values must be internally consistent (timezone == geolocation region == language == locale).
            4. Dynamic noise: add small random noise to Canvas/WebGL outputs per session to prevent cross-session linking.
            5. Behavioral biometrics: mouse movement entropy, typing cadence, scroll patterns — use humanization library.
            6. Verify against fingerprinting test sites: fingerprintjs.com, browserleaks.com, pixelscan.net.
            
            ## Evidence contract
            - fingerprint vectors listed and addressed
            - consistency check passed (timezone/locale/language aligned)
            - dynamic noise implemented
            - behavioral humanization documented
            - test site results captured
            """
        ).strip(),
    ),
    "cpp-systems-engineering": SkillSpec(
        name="cpp-systems-engineering",
        description="Use when implementing or debugging C++ systems code: Windows/Linux native, RAII, memory management, Win32 API, COM, WTL, STL, multithreading, performance-critical paths, or driver-adjacent code.",
        role="cpp-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "story or tech-spec",
            "target platform (Windows/Linux/cross)",
            "existing C++ codebase if present",
        ],
        outputs=[
            "C++ implementation with documented ownership",
            "compile command",
            "test evidence",
        ],
        references=[
            "Prefer RAII wrappers over manual new/delete.",
            "Never use raw C-style casts where static_cast/reinterpret_cast is more explicit.",
            "Document every Win32 API call with its error-check pattern.",
            "Use /analyze or clang-tidy as static analysis gate before claiming done.",
            "Open `references/cpp-systems-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/cpp-systems-engineering-good-output.md` and `examples/cpp-systems-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/cpp-systems-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/cpp-systems-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "windows-native-internals",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "desktop-imgui-development",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Produce correct, memory-safe, idiomatic C++ systems code with explicit ownership, RAII discipline, and documented Win32/POSIX API usage.
            
            ## Mandatory scope
            1. Declare ownership model before writing: raw pointer vs unique_ptr vs shared_ptr vs RAII wrapper.
            2. Use RAII for all resource acquisition: handles, sockets, file descriptors, locks.
            3. Name the Win32/POSIX API surface explicitly: function signatures, error codes, and cleanup paths.
            4. Document any UB risk: pointer arithmetic, reinterpret_cast, uninitialized memory, data races.
            5. For multithreaded code: identify shared state, synchronization primitive, and lock ordering.
            6. Capture compile + link command with exact flags (-std=c++17, /W4, /analyze if MSVC).
            
            ## Evidence contract
            - compiles cleanly with named flags
            - RAII ownership documented for every resource
            - UB risks explicitly called out or eliminated
            - Win32 error handling shown (GetLastError / HRESULT checked)
            """
        ).strip(),
        allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
    ),
    "desktop-imgui-development": SkillSpec(
        name="desktop-imgui-development",
        description="Use when building a desktop GUI with Dear ImGui (C++ or bindings): operator panels, real-time dashboards, debug overlays, game cheats UI, or tool UIs embedded in a render loop.",
        role="imgui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec or wireframe",
            "backend (DirectX/OpenGL/Vulkan)",
            "C++ project context",
            "MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data",
        ],
        outputs=[
            "ImGui implementation",
            "render loop integration",
            "state management code",
        ],
        references=[
            "Never put business logic inside the render loop — it runs every frame.",
            "UI state must be a separate struct, not global variables.",
            "Font atlas must be built once at init, not per-frame.",
            "For overlay injection, document cleanup on process exit or eject.",
            "Open `references/desktop-imgui-development-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/desktop-imgui-development-good-output.md` and `examples/desktop-imgui-development-bad-output.md` to calibrate output quality.",
            "Use `evals/desktop-imgui-development-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/desktop-imgui-development-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "cpp-systems-engineering",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build functional, well-structured Dear ImGui interfaces with correct render loop integration and layout discipline.
            
            ## Mandatory scope
            1. Declare backend: OpenGL3+GLFW, DirectX11/12, Vulkan, or SDL2 — each has a different backend setup.
            2. Render loop structure: NewFrame -> layout logic -> Render -> present — no business logic inside render loop.
            3. State separation: UI state lives in a dedicated struct, not scattered in render functions.
            4. Font loading: custom fonts loaded in ImGui_ImplXxx_CreateFontsTexture, not per-frame.
            5. DPI awareness: implement ImGui::GetIO().DisplayFramebufferScale or DPI scale factor.
            6. For overlay injection (game cheats): document hook point (Present hook, manual map) and cleanup.
            
            ## Evidence contract
            - backend declared
            - render loop structure documented
            - state struct defined
            - compiles and renders correct layout
            - DPI handling documented
            """
        ).strip(),
    ),
    "desktop-python-ui": SkillSpec(
        name="desktop-python-ui",
        description="Use when building a desktop Python GUI: PyQt6/PySide6, Tkinter, wxPython, or customtkinter for operator tools, automation dashboards, or config panels.",
        role="python-ui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec",
            "Python framework preference",
            "target OS (Windows/Linux/macOS)",
            "MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data",
        ],
        outputs=[
            "Python UI implementation",
            "threading model docs",
            "packaging spec",
        ],
        references=[
            "Never block the main UI thread with slow operations.",
            "Signals/slots for PyQt — never call UI methods directly from background threads.",
            "Use layout managers — absolute positioning breaks on different screen sizes.",
            "Provide packaging spec if operator needs a standalone .exe.",
            "Open `references/desktop-python-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/desktop-python-ui-good-output.md` and `examples/desktop-python-ui-bad-output.md` to calibrate output quality.",
            "Use `evals/desktop-python-ui-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/desktop-python-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "terminal-operator-ui",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build clean, functional Python desktop UIs with correct event loop integration, threading discipline, and packaging.
            
            ## Mandatory scope
            1. Declare framework: PyQt6/PySide6, Tkinter, customtkinter — each has different signal/slot or callback model.
            2. Threading: UI updates must happen on main thread; background work in QThread/threading.Thread with signals.
            3. Layout: use layout managers (QVBoxLayout, QHBoxLayout, grid) — never fixed pixel positioning.
            4. Packaging: specify PyInstaller or cx_Freeze spec for standalone executable if needed.
            5. State management: separate model from view — no business logic in widget callbacks.
            6. Error handling: show user-friendly error dialogs for all recoverable exceptions.
            
            ## Evidence contract
            - framework declared
            - threading model documented (background work separated from UI thread)
            - layout uses layout managers
            - packaging spec documented if needed
            - runs without console window if GUI-only
            """
        ).strip(),
    ),
    "edr-evasion-tactics": SkillSpec(
        name="edr-evasion-tactics",
        description="Use when a payload or tool needs to evade EDR runtime detection: hook bypass, AMSI bypass, ETW patching, direct syscall, or AV memory scanning evasion.",
        role="edr-evasion-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target EDR product",
            "payload or tool to protect",
            "engagement_proof",
        ],
        outputs=[
            "hook-bypass implementation",
            "AMSI/ETW bypass",
            "sandbox evidence",
        ],
        references=[
            "Never claim bypass without controlled sandbox monitoring evidence.",
            "Document which EDR version was tested — bypass techniques are version-specific.",
            "Unhooking must restore original bytes on cleanup.",
            "engagement_proof required; block if missing.",
            "Open `references/edr-evasion-tactics-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/edr-evasion-tactics-good-output.md` and `examples/edr-evasion-tactics-bad-output.md` to calibrate output quality.",
            "Use `evals/edr-evasion-tactics-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/edr-evasion-tactics-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "telemetry-blinding",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement EDR/AV runtime evasion with explicit hook bypass, syscall strategy, and OPSEC discipline.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Identify EDR target: CrowdStrike / Defender / SentinelOne / Carbon Black — hook surface differs.
            3. Choose syscall strategy: direct syscall (Syswhispers2/3), indirect syscall, or unhooking (overwrite ntdll from fresh copy).
            4. Handle AMSI: patch AmsiScanBuffer / AmsiOpenSession in-process.
            5. Handle ETW: patch EtwEventWrite / disable provider via NtTraceControl.
            6. Verify no hook fires: use a controlled sandbox with ETW/kernel callback monitoring.
            
            ## Evidence contract
            - engagement_proof confirmed
            - EDR target named
            - syscall strategy documented with method (direct/indirect/unhook)
            - AMSI + ETW bypass verified in sandbox
            - No hook fired in monitoring trace
            """
        ).strip(),
    ),
    "field-journal-evolution": SkillSpec(
        name="field-journal-evolution",
        description="Use when a task is complete, a pitfall is found, a new technique is discovered, or a routing gap is identified. Writeback experience to the field journal to evolve skill quality over time.",
        role="knowledge-writeback",
        layer="layer-3-utility-providers",
        inputs=[
            "completed task context",
            "pitfall or solution discovered",
            "skill execution chain used",
        ],
        outputs=[
            ".relay-kit/state/field-journal.md entry",
            "experience index update",
        ],
        references=[
            "Code-first: key-code field is mandatory in every entry.",
            "No fluff: reject generic summaries — require actionable specifics.",
            "No repeat: check existing entries before adding similar content.",
            "Check field-journal BEFORE starting a similar task — reuse over rediscovery.",
            "Open `references/field-journal-evolution-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/field-journal-evolution-good-output.md` and `examples/field-journal-evolution-bad-output.md` to calibrate output quality.",
            "Use `evals/field-journal-evolution-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/field-journal-evolution-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "workflow-router",
            "cook",
            "developer",
            "attack-chain-orchestration",
        ],
        body=dedent(
            """\
            # Mission
            Capture and index actionable experience from completed tasks so future lanes can reuse solutions, avoid pitfalls, and improve routing accuracy.
            
            ## Mandatory scope
            1. Writeback triggers: task complete, pitfall encountered, new technique proven, routing gap identified, code pattern reused.
            2. Writeback template per entry:
               - scenario: one sentence
               - goal: what was being built or fixed
               - execution-chain: which skills were used in order
               - pitfall-table: what failed and why
               - toolchain: exact tools and versions
               - key-code: the minimal working code or config
               - improvement: what to do differently next time
            3. No fluff: every record must contain actionable info — no generic summaries.
            4. No repeat: only add a variant if it differs substantially from existing entries.
            5. Code-first: key-code field is required — text-only entries are rejected.
            6. Check index before new tasks: when starting a similar task, search field-journal first for prior experience.
            
            ## Evidence contract
            - writeback entry written with all required fields
            - key-code field populated
            - entry indexed by category
            - prior experience searched before starting similar task
            """
        ).strip(),
    ),
    "frontend-crypto-reverse": SkillSpec(
        name="frontend-crypto-reverse",
        description="Use when web applications use client-side cryptography, obfuscated JS, WASM, or signing parameters that must be reversed to replicate API calls without a browser.",
        role="crypto-reverse-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target web application",
            "captured network traffic (HAR)",
            "JS bundle or WASM",
        ],
        outputs=[
            "signing implementation",
            "deobfuscation analysis",
            "verification comparison",
        ],
        references=[
            "Never claim signature replication without byte-exact comparison to browser output.",
            "Document key derivation — hardcoded keys may rotate.",
            "WASM decompilation output should be treated as pseudocode, not exact code.",
            "If signing keys are device-fingerprint-derived, integrate with browser-fingerprint-engineering.",
            "Open `references/frontend-crypto-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/frontend-crypto-reverse-good-output.md` and `examples/frontend-crypto-reverse-bad-output.md` to calibrate output quality.",
            "Use `evals/frontend-crypto-reverse-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/frontend-crypto-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "browser-fingerprint-engineering",
            "mmo-http-api-automation",
            "mmo-data-harvesting",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Reverse-engineer frontend signing, encryption, and obfuscation to replicate API calls programmatically.
            
            ## Mandatory scope
            1. Map signing pipeline: identify where request signature, timestamp, nonce, or token is computed (JS bundle, WASM, ServiceWorker).
            2. Deobfuscate JS: use AST transformation (babel-plugin-deobfuscator, js-beautify) or manual analysis.
            3. For WASM: extract and decompile (wasm-decompile, Ghidra WASM plugin) to identify crypto primitives.
            4. Replicate in Python/Go/Node: implement signing logic outside browser without CDP.
            5. Verify: compare replicated signature against browser-captured signature for same input.
            6. Document key material: where signing keys are embedded (hardcoded, derived from device fingerprint, fetched at runtime).
            
            ## Evidence contract
            - signing pipeline mapped
            - deobfuscation method documented
            - replication implemented and verified (signatures match)
            - key material source documented
            - works without browser dependency
            """
        ).strip(),
    ),
    "malware-analysis-workflows": SkillSpec(
        name="malware-analysis-workflows",
        description="Use when analyzing suspicious binaries, malware samples, or unknown executables: static analysis, dynamic analysis, sandbox detonation, IOC extraction, and behavioral mapping.",
        role="malware-analyst",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "suspicious binary or sample hash",
            "engagement context or IR authorization",
            "sandbox environment",
        ],
        outputs=[
            "malware analysis report",
            "IOC list",
            "ATT&CK mapping",
        ],
        references=[
            "Never detonate samples outside isolated VM with snapshot.",
            "Document isolation environment explicitly — analysis on host = contamination.",
            "IOC extraction is mandatory before any network-based hunting.",
            "ATT&CK mapping must reference technique IDs, not just names.",
            "Open `references/malware-analysis-workflows-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/malware-analysis-workflows-good-output.md` and `examples/malware-analysis-workflows-bad-output.md` to calibrate output quality.",
            "Use `evals/malware-analysis-workflows-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/malware-analysis-workflows-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "binary-reverse-methodology",
            "edr-evasion-tactics",
            "binary-stealth-obfuscation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Produce a structured malware analysis report with static properties, behavioral evidence, IOCs, and ATT&CK mapping.
            
            ## Mandatory scope
            1. Engagement proof required for offensive samples; for defensive/IR context, document authorization separately.
            2. Static analysis first: file type, hash (MD5/SHA1/SHA256), PE headers, imports, strings, entropy, packer detection.
            3. Dynamic analysis in isolated environment: VM snapshot before detonation, network monitoring (FakeNet/INetSim), process monitor.
            4. Extract IOCs: C2 domains/IPs, mutex names, registry keys, dropped files, scheduled tasks.
            5. Map to ATT&CK: technique IDs for each observed behavior.
            6. Do not run samples on production systems — document isolation environment.
            
            ## Evidence contract
            - isolation environment documented
            - static analysis output (hash, imports, strings, entropy)
            - dynamic analysis result (process tree, network, registry)
            - IOC list
            - ATT&CK mapping
            """
        ).strip(),
    ),
    "mmo-llm-automation": SkillSpec(
        name="mmo-llm-automation",
        description="Use when MMO operations need AI-assisted content generation, behavioral variance, Sybil evasion through LLM diversity, or LLM API integration for bulk content tasks.",
        role="llm-automation-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "content task specification",
            "LLM provider credentials",
            "diversity requirements",
        ],
        outputs=[
            "LLM integration implementation",
            "prompt templates",
            "content validation pipeline",
        ],
        references=[
            "Never exceed token budget without explicit approval — LLM costs scale rapidly.",
            "Diversity metric must be measured, not assumed — compute n-gram similarity.",
            "Output validation must run before publishing — LLM hallucinations contaminate MMO accounts.",
            "Local models (Ollama) preferred for sensitive content to avoid API logging.",
            "Open `references/mmo-llm-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mmo-llm-automation-good-output.md` and `examples/mmo-llm-automation-bad-output.md` to calibrate output quality.",
            "Use `evals/mmo-llm-automation-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mmo-llm-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "mmo-content-factory",
            "mmo-reup-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Integrate LLM APIs into MMO operations for content diversity, behavioral humanization, and AI-assisted task automation.
            
            ## Mandatory scope
            1. Declare LLM provider and model: OpenAI GPT-4o, Anthropic Claude, Gemini, or local (Ollama/LM Studio).
            2. Prompt engineering: system prompt, diversity parameters, content constraints — document all.
            3. Output validation: define acceptance criteria for generated content (length, language, topic compliance).
            4. Rate limit and cost management: document token budget per task, batch size, retry strategy.
            5. Behavioral variance: if used for Sybil evasion, document diversity metrics (n-gram similarity threshold).
            6. Content safety: define prohibited content filters and fallback strategy when model refuses.
            
            ## Evidence contract
            - LLM provider and model declared
            - prompt template documented
            - output acceptance criteria defined
            - rate limit and cost budget documented
            - diversity metric defined if used for Sybil evasion
            """
        ).strip(),
    ),
    "mmo-onchain-security-audit": SkillSpec(
        name="mmo-onchain-security-audit",
        description="Use when MMO crypto operations involve on-chain script execution, smart contract interaction, or wallet automation that requires security audit before deployment.",
        role="onchain-auditor",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "smart contract addresses",
            "automation script",
            "chain (ETH/BSC/ARB/etc)",
        ],
        outputs=[
            "security audit report",
            "simulation result",
            "risk assessment",
            "emergency procedures",
        ],
        references=[
            "Never deploy wallet automation without fork simulation first.",
            "Unlimited approvals are always high-risk — document and recommend alternatives.",
            "Wallet isolation is mandatory — one signing key per strategy.",
            "Emergency stop procedure must be documented before deployment.",
            "Open `references/mmo-onchain-security-audit-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mmo-onchain-security-audit-good-output.md` and `examples/mmo-onchain-security-audit-bad-output.md` to calibrate output quality.",
            "Use `evals/mmo-onchain-security-audit-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mmo-onchain-security-audit-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "mmo-crypto-wallet-farming",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Audit on-chain scripts and smart contract interactions for security vulnerabilities before any wallet or funds are committed.
            
            ## Mandatory scope
            1. Static analysis: read all contract functions being called; identify reentrancy, approval abuse, infinite approve risk.
            2. Simulation first: dry-run all transactions with fork simulation (Tenderly / Hardhat mainnet fork / Foundry fork) before live execution.
            3. Approval audit: identify any approve() or setApprovalForAll() calls; flag unlimited approvals as high-risk.
            4. Slippage and MEV: document slippage tolerance and MEV exposure for swap transactions.
            5. Wallet isolation: confirm 1-wallet-per-strategy rule — never reuse signing key across strategies.
            6. Emergency stop: document how to revoke approvals or pause automation if anomaly detected.
            
            ## Evidence contract
            - static analysis of all called functions documented
            - fork simulation result captured
            - approval risk documented (unlimited vs limited)
            - slippage and MEV tolerance documented
            - emergency revocation procedure written
            """
        ).strip(),
    ),
    "mobile-app-reverse": SkillSpec(
        name="mobile-app-reverse",
        description="Use when MMO mobile operations need to reverse-engineer APK or IPA apps: find API endpoints, signing keys, certificate pinning bypass, or replicate app behavior without the app.",
        role="mobile-reverse-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "APK or IPA file or app package name",
            "target functionality to replicate",
            "mobile device or emulator",
        ],
        outputs=[
            "API endpoint map",
            "signing implementation",
            "Python client",
            "certificate pinning bypass script",
        ],
        references=[
            "Certificate pinning bypass must be verified with actual traffic capture.",
            "API endpoint map must include all request headers and signing parameters.",
            "Signing replication must produce byte-exact results compared to app output.",
            "Document app version — APIs change across versions.",
            "Open `references/mobile-app-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mobile-app-reverse-good-output.md` and `examples/mobile-app-reverse-bad-output.md` to calibrate output quality.",
            "Use `evals/mobile-app-reverse-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mobile-app-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "frontend-crypto-reverse",
            "protocol-fingerprint-spoofing",
            "mmo-http-api-automation",
            "mmo-mobile-app-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Reverse-engineer mobile apps to extract API endpoints, signing logic, and protocol details for programmatic replication.
            
            ## Mandatory scope
            1. Platform: Android (APK) or iOS (IPA) — document platform and app version.
            2. Decompilation: APK -> jadx/apktool; IPA -> frida-ios-dump + class-dump or Ghidra.
            3. Certificate pinning bypass: Frida script for Android (SSLContext.getDefault / OkHttp) or iOS (SecTrustEvaluate / AFNetworking).
            4. API endpoint extraction: intercept traffic with mitmproxy/Burp after pin bypass; map all endpoints.
            5. Signing parameter reverse: identify request signing (HMAC, timestamp, nonce, device fingerprint).
            6. Replicate in Python: implement API client without app dependency; verify responses match.
            
            ## Evidence contract
            - platform and app version documented
            - decompilation output captured
            - certificate pinning bypassed (traffic visible in proxy)
            - API endpoints mapped
            - signing logic reversed and replicated
            - Python client verified against app responses
            """
        ).strip(),
    ),
    "network-stealth-c2": SkillSpec(
        name="network-stealth-c2",
        description="Use when building or operating C2 infrastructure that needs traffic blending, domain fronting, protocol mimicry, redirectors, or beaconing that evades network detection.",
        role="c2-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "engagement scope",
            "target network environment",
            "C2 framework if specified",
        ],
        outputs=[
            "C2 implementation",
            "traffic profile docs",
            "redirector topology",
        ],
        references=[
            "Never use default C2 framework signatures — customize all beacons, certificates, and user-agents.",
            "Jitter is mandatory — fixed intervals are trivially detected.",
            "Redirectors must not expose backend C2 IP directly.",
            "engagement_proof required; block if missing.",
            "Open `references/network-stealth-c2-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/network-stealth-c2-good-output.md` and `examples/network-stealth-c2-bad-output.md` to calibrate output quality.",
            "Use `evals/network-stealth-c2-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/network-stealth-c2-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "protocol-fingerprint-spoofing",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Design and implement C2 communication that blends with legitimate traffic and evades network-level detection.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Choose C2 protocol: HTTPS, DNS, SMB, ICMP, custom — document traffic profile.
            3. Document domain fronting or CDN relay if used: fronting domain, host header, backend.
            4. Configure beacon jitter: randomized interval (base +/- jitter %) to avoid periodic traffic patterns.
            5. Implement redirectors: separate C2 server from direct operator contact.
            6. Network traffic profile: document legitimate service being mimicked (Office365, Slack, etc.).
            
            ## Evidence contract
            - engagement_proof confirmed
            - protocol and traffic profile documented
            - beacon jitter configured and documented
            - redirector topology drawn
            - network capture shows traffic blends with legitimate baseline
            """
        ).strip(),
    ),
    "offensive-security-engagement": SkillSpec(
        name="offensive-security-engagement",
        description="Use when a request contains offensive, red-team, evasion, injection, stealth, C2, payload, syscall, hollowing, or bypass keywords, or when authorization_risk >= medium. Gate + context provider for all offensive lanes.",
        role="engagement-gate",
        layer="layer-3-utility-providers",
        inputs=[
            "user request with offensive keywords",
            "workflow-state",
            "authorization scope if provided",
        ],
        outputs=[
            "workflow-state.engagement_proof",
            "workflow-state.lane_mode = offensive",
            "risk-tier annotation",
        ],
        references=[
            "Never proceed without engagement_proof — if authorization is missing, block and prompt.",
            "Do not own the lane; return control after caching proof.",
            "Distinguish fail-closed (policy-guard) from fail-open-for-authorized (this skill).",
            "ATT&CK mapping is required for every offensive lane.",
            "Open `references/offensive-security-engagement-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/offensive-security-engagement-good-output.md` and `examples/offensive-security-engagement-bad-output.md` to calibrate output quality.",
            "Use `evals/offensive-security-engagement-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/offensive-security-engagement-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "attack-chain-orchestration",
            "cpp-systems-engineering",
            "edr-evasion-tactics",
            "process-injection-techniques",
            "network-stealth-c2",
            "binary-stealth-obfuscation",
            "policy-guard",
        ],
        body=dedent(
            """\
            # Mission
            Activate authorized offensive context, cache engagement proof, enforce OPSEC ordering, and map ATT&CK phase so offensive lanes have a clear authorization record before any specialist runs.
            
            ## Mandatory scope
            1. Confirm engagement authorization: check workflow-state for engagement_proof; if missing, prompt for scope, target, and authorization before proceeding.
            2. Cache engagement_proof with: authorized-by, scope, target, risk-tier (low/medium/high/critical), ATT&CK phase.
            3. Set lane mode to offensive in workflow-state.
            4. Enforce OPSEC ordering: recon -> initial-access -> execution -> persistence -> privesc -> lateral -> collection -> exfil -> cleanup.
            5. After caching proof, return control to the calling hub or cook — do not own the lane.
            6. Distinguish from policy-guard: policy-guard is fail-closed for secrets/shell/path. This skill is fail-open-for-authorized for offensive techniques. Run policy-guard AFTER execution as post-gate.
            
            ## Evidence contract
            - engagement_proof written to workflow-state with all required fields
            - risk-tier set explicitly before specialist is called
            - ATT&CK phase mapped for current task
            """
        ).strip(),
    ),
    "process-injection-techniques": SkillSpec(
        name="process-injection-techniques",
        description="Use when a payload needs to run in the context of another process: classic injection, reflective DLL, process hollowing, APC injection, thread hijacking, or shellcode runners.",
        role="injection-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target process or criteria",
            "payload shellcode or DLL",
            "engagement_proof",
        ],
        outputs=[
            "injection implementation",
            "memory management docs",
            "cleanup runbook",
        ],
        references=[
            "Never leave RWX memory pages after payload execution — change to RX.",
            "Document cleanup: close handles, free memory, restore target thread state.",
            "Handle WOW64 explicitly when injecting cross-arch.",
            "engagement_proof required; block if missing.",
            "Open `references/process-injection-techniques-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/process-injection-techniques-good-output.md` and `examples/process-injection-techniques-bad-output.md` to calibrate output quality.",
            "Use `evals/process-injection-techniques-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/process-injection-techniques-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "windows-native-internals",
            "binary-stealth-obfuscation",
            "network-stealth-c2",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement process injection techniques with correct memory management, error handling, and cleanup discipline.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Choose injection method: CreateRemoteThread, APC queue, SetWindowsHookEx, reflective DLL, process hollowing, early-bird, thread hijacking.
            3. Document memory allocation: VirtualAllocEx permissions (RWX -> RX after write), cleanup on failure.
            4. Handle 32-bit / 64-bit mismatch: WOW64 constraints for cross-arch injection.
            5. Verify target process selection: PPID spoofing if needed, handle privileges required.
            6. Cleanup gate: document how the injected memory and handles are cleaned up after operation.
            
            ## Evidence contract
            - engagement_proof confirmed
            - injection method declared with rationale
            - memory permissions and cleanup documented
            - arch mismatch handled (WOW64 if applicable)
            - PPID spoofing documented if used
            """
        ).strip(),
    ),
    "protocol-fingerprint-spoofing": SkillSpec(
        name="protocol-fingerprint-spoofing",
        description="Use when HTTP/HTTPS/TLS traffic needs to spoof or match a specific protocol fingerprint to evade network inspection, bot detection, or TLS fingerprinting (JA3/JA4/HTTP2).",
        role="protocol-fingerprint-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target protocol (TLS version, HTTP version)",
            "reference client fingerprint",
            "target platform",
        ],
        outputs=[
            "protocol implementation",
            "fingerprint comparison",
            "detection test result",
        ],
        references=[
            "Never claim fingerprint match without scanner verification.",
            "Document GREASE values — they are part of Chrome fingerprint.",
            "HTTP/2 SETTINGS frame order matters — match exactly.",
            "TLS extension order is as important as cipher suite choice.",
            "Open `references/protocol-fingerprint-spoofing-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/protocol-fingerprint-spoofing-good-output.md` and `examples/protocol-fingerprint-spoofing-bad-output.md` to calibrate output quality.",
            "Use `evals/protocol-fingerprint-spoofing-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/protocol-fingerprint-spoofing-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "browser-fingerprint-engineering",
            "antibot-challenge-solving",
            "network-stealth-c2",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Match target protocol fingerprints (TLS, HTTP/2, TCP) precisely so traffic is indistinguishable from a legitimate client.
            
            ## Mandatory scope
            1. Identify fingerprint target: JA3/JA3S, JA4, HTTP/2 SETTINGS, TCP window size, User-Agent.
            2. Collect reference fingerprint from legitimate client (Chrome 120+, Firefox 121+, curl).
            3. Implement spoofing: custom TLS stack (utls/tls-client), HTTP/2 SETTINGS frame order, header order.
            4. Verify match: run fingerprint scanner (tls.peet.ws, Scapy, Wireshark) against implementation.
            5. Document cipher suite order, TLS extensions, and GREASE values used.
            6. Test against target platform's detection (Cloudflare, Akamai, Datadome) in controlled env.
            
            ## Evidence contract
            - reference fingerprint captured
            - spoofed fingerprint matches (JA3/JA4 match documented)
            - cipher suite and extension order documented
            - verified against target detection platform
            """
        ).strip(),
    ),
    "telemetry-blinding": SkillSpec(
        name="telemetry-blinding",
        description="Use when operations need to suppress, redirect, or corrupt security telemetry: ETW providers, Sysmon, WEF, audit logs, or kernel callbacks.",
        role="telemetry-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target environment telemetry stack",
            "operation scope",
            "engagement_proof",
        ],
        outputs=[
            "telemetry blinding implementation",
            "verification result",
            "restoration runbook",
        ],
        references=[
            "Never delete logs without explicit engagement scope including log suppression.",
            "Document restoration path — cleanup is mandatory after authorized operations.",
            "Verify blinding with actual log monitoring, not assumption.",
            "engagement_proof required; block if missing.",
            "Open `references/telemetry-blinding-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/telemetry-blinding-good-output.md` and `examples/telemetry-blinding-bad-output.md` to calibrate output quality.",
            "Use `evals/telemetry-blinding-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/telemetry-blinding-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "network-stealth-c2",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Suppress or redirect security telemetry channels so offensive operations produce minimal forensic footprint.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Map active telemetry channels: ETW providers, Sysmon config, WEF subscriptions, audit policy.
            3. Choose blinding approach: ETW provider disable, Sysmon filter bypass, audit log suppression, kernel callback removal.
            4. Verify blinding in controlled environment: confirm target events no longer appear in SIEM/log.
            5. Document restoration path: how telemetry is re-enabled after operation.
            6. Anti-forensics scope: document which artifacts are wiped (prefetch, event logs, MFT timestamps).
            
            ## Evidence contract
            - engagement_proof confirmed
            - telemetry channels mapped
            - blinding verified (events absent in controlled log)
            - restoration path documented
            - anti-forensics scope listed
            """
        ).strip(),
    ),
    "terminal-operator-ui": SkillSpec(
        name="terminal-operator-ui",
        description="Use when building a rich terminal UI (TUI) for operator control panels, automation dashboards, or CLI tools: Rich, Textual, blessed, curses, prompt_toolkit, or similar.",
        role="tui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec or wireframe",
            "framework preference",
            "Python version",
        ],
        outputs=[
            "TUI implementation",
            "keyboard shortcut map",
            "live update docs",
        ],
        references=[
            "Never mix print() with a live TUI — it corrupts the layout.",
            "Define explicit terminal size handling — TUIs break when terminal is too narrow.",
            "Input blocking operations must run in threads with TUI-safe update callbacks.",
            "Test in the actual target terminal (Windows Terminal vs xterm differ).",
            "Open `references/terminal-operator-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/terminal-operator-ui-good-output.md` and `examples/terminal-operator-ui-bad-output.md` to calibrate output quality.",
            "Use `evals/terminal-operator-ui-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/terminal-operator-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "desktop-python-ui",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build functional, navigable terminal UIs with correct layout, input handling, and live update discipline.
            
            ## Mandatory scope
            1. Declare framework: Rich (static), Textual (reactive TUI), blessed, curses, prompt_toolkit.
            2. Layout: define panels, tables, progress bars, and input areas with explicit dimensions and overflow behavior.
            3. Live updates: use Live context (Rich) or reactive state (Textual) — never print() to a live TUI.
            4. Input handling: define keyboard shortcuts, navigation, and exit path explicitly.
            5. Color and styling: define palette and use named styles, not inline ANSI codes.
            6. Error display: show error state visually in a status bar or panel, not as raw exception text.
            
            ## Evidence contract
            - framework declared
            - layout documented (panels, tables, inputs)
            - live update mechanism specified
            - keyboard shortcuts documented
            - runs in target terminal (Windows cmd/PowerShell/Linux term)
            """
        ).strip(),
    ),
    "windows-native-internals": SkillSpec(
        name="windows-native-internals",
        description="Use when work requires Windows-internal knowledge: NT APIs, PEB/TEB, kernel structures, SSDT, ETW, driver interaction, object manager, undocumented syscalls, or memory manager internals.",
        role="windows-internals-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target Windows version",
            "NT API surface needed",
            "existing code context",
        ],
        outputs=[
            "Windows-native implementation",
            "API documentation",
            "version-conditional guards",
        ],
        references=[
            "Always declare which Windows version the code targets — offsets change.",
            "Never hardcode structure offsets without a version guard.",
            "Document whether ETW or PatchGuard is affected.",
            "Use ntdll imports or direct syscall — never assume high-level API availability in injected context.",
            "Open `references/windows-native-internals-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/windows-native-internals-good-output.md` and `examples/windows-native-internals-bad-output.md` to calibrate output quality.",
            "Use `evals/windows-native-internals-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/windows-native-internals-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "cpp-systems-engineering",
            "process-injection-techniques",
            "edr-evasion-tactics",
            "telemetry-blinding",
            "binary-stealth-obfuscation",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Apply Windows NT internals knowledge to implement, debug, or bypass Windows-native subsystems safely and correctly.
            
            ## Mandatory scope
            1. Identify the Windows version target: XP/7/10/11/Server — kernel structures change across versions.
            2. Name the NT API or structure being used: NtAllocateVirtualMemory, PEB, LDR_DATA_TABLE_ENTRY, etc.
            3. Declare whether the technique uses documented API, undocumented API, or direct syscall.
            4. Document SSDT/ETW/Callback implications for any kernel-touching operation.
            5. For usermode-kernel transitions: document syscall number, calling convention, and version dependency.
            6. Include version-conditional code where kernel structures differ across Windows releases.
            
            ## Evidence contract
            - Windows version target declared
            - API tier declared (documented / undocumented / direct syscall)
            - Structure offsets verified against target version
            - SSDT/ETW impact documented
            """
        ).strip(),
    ),
}
