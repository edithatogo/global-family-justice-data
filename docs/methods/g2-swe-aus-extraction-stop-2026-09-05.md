# Swedish/AUS extraction stop

Two agents were launched without conversation history, using separate
input-only workspaces. The orchestrator verified both source hashes and the
contract against the same input manifests before delegation. No expected
values or previous outputs were supplied.

Extractor B reported that its page-text selection included nearby prose
excluded by the frozen contract. It stopped without an output. The orchestrator
interrupted A on receipt of this finding and terminated the lineage.
There is no comparator result or successful dual extraction.

Supporting artifacts are retained under ignored `build/g2-swe-aus-extraction/`.
The fresh execution requires a new prospective scope if resumed. Recommended
remediation is to define whether surrounding page context may be inspected
while remaining excluded from output, or bind a verified table crop before
delegation. No historical failed output may be repaired or reused.
