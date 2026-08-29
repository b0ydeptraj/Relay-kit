---
name: kernel-driver-evasion
description: "Use when a payload needs Ring 0 evasion: BYOVD (Bring Your Own Vulnerable Driver), DKOM (Direct Kernel Object Manipulation), kernel callback suppression (ObRegisterCallbacks, PsSetCreateProcessNotifyRoutine), DSE bypass, PatchGuard (KPP) timer disarm, or PPL (Protected Process Light) bypass via EPROCESS .Protection field."
---

# Mission
Implement Ring 0 kernel evasion safely and precisely: exploit a signed vulnerable driver (BYOVD) or leverage direct kernel primitives to suppress EDR kernel callbacks, hide processes/threads via DKOM, disarm PatchGuard timers, or strip PPL protection from EDR processes.

## Mandatory scope
1. Confirm engagement_proof in workflow-state; block if missing.
2. Declare target kernel tier: BYOVD (use signed VD) | KDU (Kernel Driver Utility) | Manual DSE patch.
3. Identify the callback to disable: `ObRegisterCallbacks` (handle stripping) | `PsSetCreateProcessNotifyRoutine` (process events) | `PsSetLoadImageNotifyRoutine` (image load events) | MiniFilter altitude interception.
4. Enumerate vulnerable driver candidates: target CVE with IOCTL code for arbitrary memory r/w (e.g., RTCore64, gdrv, dbutil_2_3.sys, iqvw64e.sys); cross-check LOLDrivers list.
5. Implement kernel primitive: read/write arbitrary kernel memory via vulnerable IOCTL; never hardcode addresses — resolve dynamically via `NtQuerySystemInformation(SystemModuleInformation)` + pattern scan.
6. For DKOM: locate `EPROCESS` via `PsGetCurrentProcess()` + exported symbol offset; unlink from `ActiveProcessLinks` (doubly-linked list); also blank `UniqueProcessId` and `ImageFileName` in EPROCESS for full invisibility.
7. Cleanup contract: re-link EPROCESS before process exit; restore callback pointers; unload vulnerable driver; delete service key from registry.

## Kernel Callback Suppression Flow
```
Scan MmNonPagedPool for callback array ptr (PsSetCreateProcessNotifyRoutine table)
  -> Read array entries via IOCTL arbitrary-read
  -> Zero out target EDR callback entry
  -> Verify zero via re-read
  -> Log original ptr for restoration
```

## BYOVD Minimal Execution Chain
1. Drop VD to `%TEMP%` with randomized filename.
2. Create service via `ScCreateService` or `NtLoadDriver` (if SCM is monitored).
3. Open device handle via `CreateFile` on VD's device name.
4. Issue r/w IOCTL to kernel memory.
5. On cleanup: stop service → delete service key → delete file → verify handle closed.

## PatchGuard (KPP) Disarm Strategy
> PatchGuard periodically validates kernel code/data integrity. Wrong write target → BSOD `CRITICAL_STRUCTURE_CORRUPTION`.

### What KPP checks (avoid writing to these):
- SSDT (`KiServiceTable`) — **never patch on Win10+**.
- IDT entries directly.
- `MmSystemCallHandler` code pages.
- Kernel `.text` section byte patterns.

### Safe Zone (KPP-transparent operations):
- **Callback table entry zeroing** — KPP does NOT protect the `PsSetCreateProcessNotifyRoutine` array entries.
- **EPROCESS field manipulation** — `ActiveProcessLinks`, `UniqueProcessId`, `ImageFileName`, `.Protection` — **not KPP protected**.
- **EPT-level hooks** (via hypervisor) — invisible to KPP entirely.

### KPP Timer Disarm (advanced — use only when SSDT patch is required):
```
Technique: DPC Timer Manipulation
1. Locate KPP context structure via pattern scan in MmNonPagedPool
   (KPP obfuscates its context each boot — scan for known byte patterns per build).
2. Find the KPP DPC timer object (KTIMER) inside context.
3. Zero or redirect DPC routine pointer → KPP check never fires.
4. Alternatively: set DPC DueTime to maximum (MAXLONGLONG) to postpone indefinitely.

WARNING: Pattern changes every Windows Update. Maintain build-versioned pattern DB.
Reference: Fyyre's KPP research, TheCruZ/kdmapper approach.
```

### Version-Conditional KPP Pattern Offsets:
```
Windows 10 19041: KPP context pattern = {0x48, 0x83, 0xEC, 0x28, 0x48, 0x8B, 0x05} (+scan)
Windows 10 22000: Different obfuscation seed — rescan from ntoskrnl .text
Windows 11 22621+: Use kdmapper-based approach (map unsigned driver without KPP exposure)
```

## PPL (Protected Process Light) Bypass
> EDR processes (MsSense.exe, CSFalconService, MBAMService) run as PPL — cannot be opened/terminated from unprotected Ring 3 context even with SeDebugPrivilege.

### EPROCESS .Protection field layout (PS_PROTECTION struct at offset, build-specific):
```c
typedef struct _PS_PROTECTION {
    UCHAR Type   : 3;  // PS_PROTECTED_TYPE: 0=None, 1=Light, 2=Full
    UCHAR Audit  : 1;
    UCHAR Signer : 4;  // PS_PROTECTED_SIGNER: 0=None, 6=WinSystem, 7=WinTcb
} PS_PROTECTION;
```

### PPL Strip Flow (via kernel arbitrary write):
```
1. Resolve EPROCESS of target PPL process:
   NtQuerySystemInformation(SystemProcessInformation) → find PID
   → walk EPROCESS chain from current process EPROCESS
2. Locate .Protection offset in EPROCESS:
   WinDbg: dt nt!_EPROCESS → find Protection field offset per build
   Win11 22631: Protection at offset 0x87A (verify per build)
3. Write PS_PROTECTION{Type=0, Signer=0} via IOCTL arbitrary-write.
4. Now target process is unprotected → OpenProcess(PROCESS_ALL_ACCESS) succeeds.
5. Restore .Protection on cleanup.
```

### EPROCESS.Protection Offsets (verify with WinDbg per build):
| Windows Build | Protection Offset |
|---|---|
| 19041 (20H1) | 0x6FA |
| 22000 (Win11 21H2) | 0x87A |
| 22621 (Win11 22H2) | 0x87A |
| 22631 (Win11 23H2) | 0x87A |

## Evidence contract
- engagement_proof confirmed
- Vulnerable driver CVE + IOCTL code documented
- Kernel callback array location method documented (not hardcoded)
- DKOM offset source declared (WinDbg `dt nt!_EPROCESS` output for target build)
- KPP safe/unsafe write zones declared
- PPL target process and .Protection offset documented per build
- Cleanup sequence verified (driver unloaded, registry key deleted, EPROCESS restored)
- Tested on: Windows build version documented (19041 / 22000 / 22621 / 22631)

## Role
- kernel-evasion-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target Windows build (e.g., 22631.4169)
- EDR product to suppress (name + PPL signer type if known)
- engagement_proof

## Outputs
- BYOVD loader implementation (C++ / C)
- DKOM hide-process implementation
- Callback suppression implementation
- PPL strip routine
- KPP-safe write zone analysis
- Cleanup routine

## Reference skills and rules
- Never hardcode kernel structure offsets; always resolve dynamically or use version-conditional guards.
- LOLDrivers check mandatory before choosing a VD: https://www.loldrivers.io/
- KPP safe zone = callback array zeroing + EPROCESS field manipulation. KPP unsafe = SSDT patch, .text modification.
- DSE bypass via `ci.dll!g_CiEnabled` patch is PatchGuard-hostile on Win10 21H2+ — prefer kdmapper approach.
- PPL .Protection offset varies by build — always WinDbg-verify before hardcoding.
- Document PatchGuard implications explicitly before any kernel memory write.

## Likely next step
- hardware-assisted-re
- edr-evasion-tactics
- telemetry-blinding
- process-injection-techniques
- windows-native-internals
- field-journal-evolution


