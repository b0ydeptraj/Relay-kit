---
name: hardware-assisted-re
description: "Use when analysis or evasion needs hypervisor-level (Ring -1) techniques: EPT hooking / NPT hooking (memory cloaking / page shadowing) on Intel VT-x AND AMD-V/SVM, hardware breakpoints via DR registers, VMEXIT storm mitigation, or bypassing integrity checkers (BattlEye, Vanguard, EAC) that validate code pages from kernel level."
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

## AMD-V / SVM — NPT Hook Flow
> AMD CPU (Ryzen, EPYC) sử dụng **SVM** và **NPT (Nested Page Tables)** thay vì VMX/EPT.
> Code VT-x không thể dùng trực tiếp trên AMD — cần SVM-specific init.

### Key API/Register Differences: Intel VT-x vs AMD-V
| Concept | Intel VT-x | AMD-V / SVM |
|---|---|---|
| VM control block | VMCS (per-CPU, via VMPTRLD) | VMCB (Virtual Machine Control Block, in memory) |
| Page table extension | EPT (Extended Page Tables) | NPT (Nested Page Tables) |
| VM enter/exit | `VMLAUNCH` / `VMRESUME` / `VMEXIT` | `VMRUN` / `#VMEXIT` |
| Save/restore state | `VMREAD` / `VMWRITE` | Direct struct fields in VMCB |
| Intercept config | VMCS control fields | VMCB intercept fields (offset-based) |

### SVM VMCB Key Fields for NPT Hook:
```c
// VMCB layout (AMD APM Vol. 2, Appendix B)
struct VMCB {
    // Control Area (offset 0x000)
    UINT16 intercept_cr_read;      // CR access intercepts
    UINT16 intercept_cr_write;
    UINT32 intercept_exceptions;   // Exception intercepts
    UINT64 intercept_misc1;        // Misc intercepts (HLT, CPUID, etc.)
    UINT64 intercept_misc2;
    // ...
    UINT64 ncr3;                   // Nested CR3 — NPT root page table
    UINT8  np_enable;              // [bit0] = 1 to enable NPT
    // Save Area (offset 0x400)
    // General purpose registers, segment descriptors, etc.
};
```

### NPT Shadow Page Setup (AMD-V):
```
1. Allocate VMCB for guest state.
2. Set ncr3 to point to custom nested page table root.
3. Split target 4KB physical page in NPT:
   - Shadow exec page (patched): Executable-only PTE in NPT
   - Original page (clean): Read/Write-only PTE in NPT
4. On NPT fault (#NPF VMEXIT):
   - Check fault type (read/write vs exec) from VMCB.exitinfo1
   - Swap PTE to appropriate page
   - VMRUN resumes guest
5. Use SimpleSvm or AMD's open-source SVM reference as init skeleton.
```

### CPUID Check for AMD-V:
```c
// Check SVM support before init
int regs[4];
__cpuid(regs, 0x80000001);
bool svm_supported = (regs[2] >> 2) & 1;  // ECX bit 2

// Check if SVM is disabled by BIOS (SVM_LOCK bit in MSR_EFER):
uint64_t vm_cr = __readmsr(0xC0010114);  // MSR_VM_CR
bool svm_disabled = (vm_cr >> 4) & 1;    // SVMDIS bit
```

## Anti-Cheat Evasion Considerations
| Anti-Cheat | Primary Detection Vector | EPT/NPT Counter-Technique |
|---|---|---|
| BattlEye | Kernel page hash scan + driver enumeration | EPT/NPT shadow page + callback suppression |
| Vanguard (Valorant) | Kernel mode with HVCI on some configs | Requires UEFI/Secure Boot disabled; HVCI blocks unsigned kernel code |
| EAC (Easy Anti-Cheat) | User mode scan + kernel driver stack walk | EPT/NPT + driver spoofing via DKOM |

> **HVCI (Hypervisor-Protected Code Integrity):** If target has HVCI enabled (`hvci.dll` loaded, `VsmProtectionInfo.HvciEnabled == 1`), EPT/NPT hooks on kernel pages are blocked — declare incompatibility explicitly.

## VMEXIT Storm Mitigation
> EPT/NPT hooks fire VMEXIT on every execute access to shadow page. Game engines with many threads = millions of VMEXIT/sec = severe FPS drop + anti-cheat latency anomaly detection.

### Root Causes of VMEXIT Storm:
- Hook on frequently-called function (e.g., `ntdll!NtUserGetMessage`, game render loop).
- Per-thread shadow page not isolated → all threads hit same VMEXIT handler.
- TLB not properly invalidated → stale translations re-fault repeatedly.

### Mitigation Strategies:

**1. Hook Placement — Choose Low-Frequency Targets:**
- Hook on initialization paths, not hot render/input loops.
- Profile with Intel VTune or AMD uProf first: identify call frequency before choosing hook site.
- Prefer hooking at function prologue of infrequently called validator functions.

**2. Per-Thread Shadow Page Mapping:**
```
On each VMEXIT: check guest CR3 (process context)
  → Maintain per-CR3 shadow page map
  → Don't swap global shadow page; swap per-context PTE
  → Reduces cross-thread interference
```

**3. TLB Invalidation Scope (use smallest scope):**
```c
// Intel: INVEPT types
INVEPT_SINGLE_CONTEXT = 1   // Invalidate TLB for single EPT pointer — prefer this
INVEPT_ALL_CONTEXT    = 2   // Full TLB flush — avoid in hot path

// AMD: INVLPGA instruction
INVLPGA [addr], ecx  // Invalidate single page in ASID context — use instead of full TLB flush
```

**4. VMEXIT Coalescing:**
- Batch shadow page swaps: process N pending VMEXIT reasons per VMRESUME instead of 1:1.
- Cache last-used shadow page per CPU core to avoid redundant PTE writes.

**5. Detection Avoidance:**
- Keep VMEXIT handler latency < 1μs — BattlEye measures execution timing anomalies.
- Zero `VMCS.VMX_PREEMPTION_TIMER` or set to max to avoid spurious timer exits adding noise.
- Monitor your own VMEXIT rate: > 500k VMEXIT/sec on a game thread is suspicious.

## Evidence contract
- engagement_proof confirmed
- CPU vendor detected (Intel VT-x vs AMD-V) — correct init path taken
- HVCI status on target documented
- EPT (Intel) or NPT (AMD) page split strategy documented (4KB granularity, RW vs exec separation)
- VMEXIT rate measured and within acceptable bounds (< 500k/sec on game thread)
- TLB invalidation scope documented (INVEPT type or INVLPGA)
- DR registers cleared on task completion
- Tested environment: Bare metal preferred (note: AMD nested SVM limited on some VMware versions)

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
- Always check HVCI status before attempting kernel code modification or EPT/NPT hooks on kernel pages.
- EPT/NPT hooks on user-mode pages do NOT require HVCI bypass — scope accordingly.
- **Intel VT-x ≠ AMD-V**: Always detect CPU vendor (`CPUID.0:EBX` = 'GenuineIntel' or 'AuthenticAMD') and branch to correct init path.
- Never implement full VMX/SVM from scratch — use Hvpp (Intel) or SimpleSvm (AMD) skeleton and extend.
- VMEXIT rate must be profiled before deployment; > 500k/sec on target thread = detectable.
- Document nested VT-x/SVM limitations clearly if running inside VMware/Hyper-V.
- Reference: Intel SDM Vol. 3C (VMX), AMD APM Vol. 2 (SVM), Tandasat's Hvpp (Intel), tandasat/SimpleSvm (AMD).

## Likely next step
- kernel-driver-evasion
- edr-evasion-tactics
- binary-reverse-methodology
- windows-native-internals
- field-journal-evolution
