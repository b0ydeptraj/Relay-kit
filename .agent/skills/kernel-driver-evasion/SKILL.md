---
name: kernel-driver-evasion
description: "Use when a payload needs Ring 0 evasion: BYOVD (Bring Your Own Vulnerable Driver), DKOM (Direct Kernel Object Manipulation), kernel callback suppression (ObRegisterCallbacks, PsSetCreateProcessNotifyRoutine), DSE bypass, or IOCTL-based memory r/w against protected processes."
---

# Mission
Implement Ring 0 kernel evasion safely and precisely: exploit a signed vulnerable driver (BYOVD) or leverage direct kernel primitives to suppress EDR kernel callbacks, hide processes/threads via DKOM, or bypass Driver Signature Enforcement (DSE) for unsigned driver loading.

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

## Evidence contract
- engagement_proof confirmed
- Vulnerable driver CVE + IOCTL code documented
- Kernel callback array location method documented (not hardcoded)
- DKOM offset source declared (WinDbg `dt nt!_EPROCESS` output for target build)
- Cleanup sequence verified (driver unloaded, registry key deleted)
- Tested on: Windows build version documented (19041 / 22000 / 22621 / 22631)

## Role
- kernel-evasion-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target Windows build (e.g., 22631.4169)
- EDR product to suppress
- engagement_proof

## Outputs
- BYOVD loader implementation (C++ / C)
- DKOM hide-process implementation
- Callback suppression implementation
- Cleanup routine

## Reference skills and rules
- Never hardcode kernel structure offsets; always resolve dynamically or use version-conditional guards.
- LOLDrivers check mandatory before choosing a VD: https://www.loldrivers.io/
- If PatchGuard (KPP) is active: do NOT patch SSDT or kernel code pages — use callback-table zeroing instead (avoids KPP trigger).
- DSE bypass via `ci.dll!g_CiEnabled` patch is PatchGuard-hostile on Win10 21H2+ — use test-signing mode or UEFI Secure Boot disabled environment only.
- Document PatchGuard implications explicitly before any kernel memory write.

## Likely next step
- hardware-assisted-re
- edr-evasion-tactics
- telemetry-blinding
- process-injection-techniques
- windows-native-internals
- field-journal-evolution
