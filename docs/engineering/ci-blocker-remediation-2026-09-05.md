# PR 159 blocker remediation

The hosted Python test matrices and coverage job rejected the newly supported
rich-text string because a regression test still required rejection of every
rich-text run. The test now asserts the supported lexical result and rejects
unknown run children, invalid whitespace controls and non-whitespace tails.
The reader enforces these restrictions instead of silently dropping content.

The static job failed because programme evidence counts had changed without
regenerating status. The generated status now includes the added records.

Historical replay fingerprints remain historical. Current rehearsal output
must be generated separately against the current implementation. These fixes
do not accept empirical evidence or programme gates.
