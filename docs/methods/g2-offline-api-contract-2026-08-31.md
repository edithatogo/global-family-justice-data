# Separate offline GOV.UK metadata contract

This is a prospective parser and synthetic qualification bundle, not a request
packet or evidence of a successful deployed API response. Frozen predecessors,
their consumed attempts and failed outputs remain unchanged.

## Recommended disposition

Use the new contract for repository-owned preparation. Do not connect it to
the old capture command or pass historical failed evidence through it. The
named incidental presenter fields may contain any bounded JSON type, but their
values are discarded. Unknown fields stop; accepting documented extras does
not become acceptance of arbitrary future root or result-row fields. Nested
keys inside a named incidental container are structurally bounded and discarded.
The semantic fields retain explicit types: nonempty string title and locator,
allowed string format, nullable date strings, and integer enumeration fields
excluding booleans. Titles reject whitespace-only and C0/C1 controls. Populated
dates require full seconds with optional fractions and an explicit Z or signed
HH:MM timezone; valid lexical text is preserved without normalization.
This is a narrow project contract, not a complete publisher
schema; optional incidental keys need not be present.

Passing output contains only validated locators and separately named update
and first-publication dates. Titles and incidental values are never retained.
Dates may be null; missing first-publication evidence does not inherit an
update date. Neither date establishes exact-edition identity or unseen status.
Strict response enumeration checks do not prove completeness of the publisher
index or project exposure history.

After a bounded parse, string-link fingerprints account for observed locators
even on a later contract failure. These hash exact returned link-string UTF-8
bytes, not canonical URL identities, and cannot replace cumulative exposure
accounting. Fingerprints are not anonymization. Parse or
structural-budget failure cannot claim complete exposure. No partial passing
observation list survives a failed evaluation; diagnostics contain fixed codes,
not source values, unknown field names or untrusted exceptions.

`exposure_complete` means only that every returned row has a string link whose
bytes were hashed after bounded parsing. It may be true despite a failed
enumeration/schema check; it does not establish total/start consistency,
publisher-index completeness, safe locators or historical exposure completeness.

## Advisory review

The role-separated `api_contract_advice` reviewer endorsed the distinct offline
design, identified the key-scope and fingerprint-identity clarifications above,
and then reviewed the implemented parser with 47 synthetic tests passing.
No blocking code defect was found. This is agent advice, not deployed response
evidence or independent assurance. The orchestrator retains the exact detached
bindings and the owner retains all accountable decisions.

## Options, trade-offs and contingency

The implemented option resolves a known interface mismatch without consuming
another request. A documentation-only option would be cheaper but leave the
parser untested. A permissive arbitrary-key parser would hide schema drift and
is rejected. Conservative locator/format/date rules may reject legitimate
publisher rows: stop and inspect the contract through a new prospective
decision, never repair, retry or relax it against the failed response.

The contract JSON and detached bundle list exact bindings. No transport is
implemented. Before any future request, a separate execution packet must bind
the exact query and scope, current cumulative exposure, byte/result budgets,
one-attempt consumption and receipt controls, fresh roles and owner authority.
No additional owner decision is needed for this offline slice. Those later
execution decisions should be grouped after the remaining safe preparation.

Zero requests, source acquisitions, extractions or publication operations are
authorized by these files. Metadata-shape success is not G2 acceptance, rights
clearance, maturity promotion, selection permission or release readiness.
