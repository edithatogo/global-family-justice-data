# Digest-bound panel and owner adjudication — 2026-08-02

## Frozen packet

- Repository HEAD: `636806d57e3125be56214988526a8e9b18bea824`
- `MANIFEST.sha256` digest: `cbb365e8f16881819841e0225d547397a93eb6ef667cb54a408c191a5220200f`
- Product candidate manifest digest: `8e501194801c6f8d90029a82efabf04bb3158adc71f630f8fed3e9fe6e5c178b`

## Panel verdicts

| Panel | Verdict | Owner adjudication |
|---|---|---|
| Coverage/evidence | Packet integrity pass; readiness blocked | Accept audit; defer all coverage, access, second-review and enquiry closures |
| Product/accessibility | Conditional/blocked | Accept automated structural controls; defer human accessibility, localisation, usability and harms review |
| Rights/security/operations | Conditional/fail-closed | Accept automated security and lock checks; defer rights, custody, signing, hosting, support and funding decisions |

## Adjudication rules

- Automated controls are accepted as repository evidence only.
- All P1/external findings are **deferred**, not accepted as resolved.
- Unknown rights remain metadata-only or excluded.
- Inaccessible or unsecond-reviewed searches remain unresolved.
- No enquiry is closed before its documented response/no-response threshold.
- No publication, signing, deployment, custody or archive transition is authorized.

## Remediation recorded

The stale restore receipt was regenerated under the hardened schema. The new
local rehearsal receipt verifies successfully and remains explicitly unsigned
and local-only.

## Blocking outcome

No gate is promoted and no track is archive-eligible. The panel supplements but
does not replace human/legal/owner authority, local verification, consent,
publication approval or funding commitments.
