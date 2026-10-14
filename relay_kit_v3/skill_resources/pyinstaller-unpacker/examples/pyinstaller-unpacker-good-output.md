# pyinstaller-unpacker - strong example

**Request:** a scoped, authorized task that matches `pyinstaller-unpacker`.

**Response shape that passes the contract:**

Scope check: the target matches `pyinstaller-unpacker` (use when a lane needs pyinstaller unpacker: fully automated pyinstaller extraction and decompilation pipeline); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to pyinstaller, unpacker, lane, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
