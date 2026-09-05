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

Receipt audit found two manually transcribed size errors in the September 4
retrieval receipt: South Africa is 6,577,186 bytes and Minnesota is 1,402,492
bytes. Both retained provider copies agree with the original custody inventory.
The receipt sizes were corrected; its previous contents remain in Git history.
