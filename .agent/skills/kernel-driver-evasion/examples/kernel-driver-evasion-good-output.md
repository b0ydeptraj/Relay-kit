# Good Output Example - Kernel Driver Evasion

## Scenario: BYOVD to disable EDR kernel callbacks

### Evidence
- engagement_proof: client-engagement-2024-001
- Target EDR: CrowdStrike Falcon sensor v7.x
- Vulnerable driver: RTCore64.sys (IOCTL privilege escalation)

### Step 1 - Identify BYOVD candidate
```\npython scripts/vuln_driver_loader.py --list-candidates\n# Output: RTCore64.sys - MSI Afterburner driver, IOCTL 0x80002048 allows arbitrary kernel R/W\n```\n
### Step 2 - Remove kernel callbacks
Using RTCore64 arbitrary read/write to zero out callback array entries.

### Cleanup
- Driver unloaded via sc stop/delete
- Original callback table restored from backup
- Kernel debugger log shows callback restored
