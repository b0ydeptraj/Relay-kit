# edr-evasion-tactics Weak Output Anti-Example

Request: evade EDR detection through unhooking, direct syscalls, callback manipulation, and ETW blinding

Weak answer:

This looks like `edr-evasion-tactics`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `Relay-kit offensive tool pack with edr-evasion-tactics domain expertise` was inspected.
- No symbol such as `syscall_stub` was confirmed.
- No proof surface was named for `userland hook`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
