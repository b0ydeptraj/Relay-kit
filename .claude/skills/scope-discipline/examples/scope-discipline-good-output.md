# scope-discipline calibrated output

Request: add a wrapper, a second agent, and a new dependency to fix one failing parser test.

Evidence gathered:

- The existing parser already owns the behavior.
- The failing test names one missing case.
- No caller or invariant requires a wrapper, second agent, or dependency.

Decision:

- required: one parser change and one regression test
- removed: wrapper, second agent, dependency
- stopping rule: stop when the focused test and the existing suite pass
- residual risk: integration coverage remains to be checked by the normal test gate
