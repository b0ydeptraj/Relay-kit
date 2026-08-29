---
name: hardware-assisted-re
description: "Use when analysis or evasion needs hypervisor-level (Ring -1) techniques: EPT hooking (memory cloaking / page shadowing), VT-x/AMD-V hypervisor implementation, hardware breakpoints via DR registers, or bypassing integrity checkers (BattlEye, Vanguard, EAC) that validate code pages from kernel level."
---

# Mission
Implement or reverse hypervisor-assisted techniques for memory cloaking, code integrity bypass, and hardware-level stealth analysis. Operates at Ring -1 (VMX root mode) below kernel and EDR reach.

## Mandatory scope
1. Confirm engagement_proof in workflow-state; block if missing.
2. Declare target tier:
   - **EPT Hook (Shadow Paging):** Present different page content to the integrity checker vs. the executing CPU — classic technique against BattlEye/Vanguard page hash checks.
   - **Hardware Breakpoint (DR0-DR3):** Single-step arbitrary kernel code without touching software hooks or INT3 (bypasses HWBP detection loops by resetting DR after each hit).
   - **Hypervisor Introspection:** Inspect guest VM memory from VMM without modifying guest.
3. For EPT Hooking: understand the EPT violation exit handler cycle:
   - Guest executes → EPT RW violation → VMEXIT → VMM presents shadow page → VMENTRY resumes.
   - Shadow page has patched bytes; actual physical page remains clean for hash checks.
4. Document CPU feature dependencies: `CPUID.1:ECX.VMX[bit5]` (VT-x) or `CPUID.80000001h:ECX.SVM[bit2]` (AMD-V); abort with clear error if not present.
5. For existing hypervisor frameworks: prefer Hvpp, KasperskyHV, or SimpleSvm as reference; do NOT reinvent VMX initialization from scratch unless specifically required.

## EPT Hook Minimal Flow
```
Init VMX → Set up EPT tables → Split target 4KB page into:
  Shadow_exec_page (contains hook/patch) → marked Execute-only in EPT
  Original_page (clean bytes) → marked RW-only in EPT (for integrity scanner reads)
EPT Read/Write violation → VMEXIT → swap to Original_page temporarily → VMENTRY
EPT Execute violation → VMEXIT → swap to Shadow_exec_page → VMENTRY
```

## Hardware Breakpoint Usage
- Set DR0–DR3 to target address; set DR7 condition bits (execute / read / write, length).
- Handle `#DB` exception in IDT hook or VMEXIT (if under hypervisor).
- Reset DR registers immediately after single-step if evading HWBP scanners.
- Never leave DRx set across suspicious call boundaries (BattlEye walks DRx on thread entry).

## Anti-Cheat Evasion Considerations
| Anti-Cheat | Primary Detection Vector | EPT Counter-Technique |
|---|---|---|
| BattlEye | Kernel page hash scan + driver enumeration | EPT shadow page + callback suppression |
| Vanguard (Valorant) | Kernel mode with HVCI on some configs | Requires UEFI/Secure Boot disabled; HVCI blocks unsigned kernel code |
| EAC (Easy Anti-Cheat) | User mode scan + kernel driver stack walk | EPT + driver spoofing via DKOM |

> **HVCI (Hypervisor-Protected Code Integrity):** If target has HVCI enabled (`hvci.dll` loaded, `VsmProtectionInfo.HvciEnabled == 1`), EPT hooks on kernel pages are blocked — declare incompatibility explicitly.

## Evidence contract
- engagement_proof confirmed
- CPU VMX/SVM feature check result documented
- HVCI status on target documented
- EPT page split strategy documented (4KB granularity, RW vs exec separation)
- DR registers cleared on task completion
- Tested environment: Bare metal or Type-1 hypervisor (VMware nested VT-x supported; Hyper-V requires expose-virt flag)

## Role
- hypervisor-re-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target Windows build
- anti-cheat / integrity checker product
- engagement_proof
- hardware (bare metal preferred; note nested VT-x limitation)

## Outputs
- EPT hook implementation (or reference to Hvpp-based implementation)
- Hardware breakpoint handler
- HVCI compatibility report
- Cleanup routine (unhook EPT, reset DRx, disable VMX)

## Reference skills and rules
- Always check HVCI status before attempting kernel code modification or EPT hooks on kernel pages.
- EPT hooks on user-mode pages do NOT require HVCI bypass — scope accordingly.
- Never implement full VMX from scratch for a single engagement — use Hvpp/SimpleSvm skeleton and extend.
- Document nested VT-x limitations clearly if running inside VMware/Hyper-V.
- Reference: Intel SDM Vol. 3C (VMX), AMD APM Vol. 2 (SVM), Tandasat's Hvpp project.

## Likely next step
- kernel-driver-evasion
- edr-evasion-tactics
- binary-reverse-methodology
- windows-native-internals
- field-journal-evolution
