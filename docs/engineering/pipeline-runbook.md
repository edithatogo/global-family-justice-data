# Data pipeline runbook

The pipeline preserves four layers: raw source evidence and manifests; bronze source-native extractions; silver normalised observations; and gold release-eligible observations. Every transformation must retain source edition, extraction, transformation, review and provenance locators.

The controlled sequence is: acquire; verify checksum and rights route; extract without altering source labels; map using versioned rules; validate against JSON Schema; review and adjudicate; promote eligible rows; quarantine all failures with machine-readable reasons; build lineage; compare release diff; and publish only from immutable release artefacts.

Pipeline failures are never repaired by editing gold output. Corrections are made upstream and rebuilt.
