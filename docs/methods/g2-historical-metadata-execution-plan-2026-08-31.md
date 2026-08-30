# Authorized one-shot historical metadata execution

Supports WI-G2-04/07; no gate or maturity acceptance.

- [x] Verify exact prospective bundle and clean source manifest; baseline
  `make check` passes on `ed7a892` before mutation.
- [x] Record the actual owner authorization in signed commit `080db21`, binding bundle
  SHA-256 `e166ea3785521bdcf1802bdc005383af40f054a1c349871d313c91e963107004`.
- [x] Delegate the frozen one-shot CLI to a fresh metadata registrar; preserve (`20feba9`)
  the unmodified receipt and attempt marker. No result URLs or sources opened.
- [x] Separate network-prohibited advisory review of the receipt, scope,
  exposure and next options; no failed evidence repair or retry.
- [~] Index the outcome in Conductor, validate, commit and deliver via checked
  PR with signed history; leave G2 and source-stage authority unchanged.

Any contract or transport failure terminates this lineage. A successful result
is metadata hypotheses only. No automatic successor or external request is
authorized. All subsequent validation is offline; post-execution inventory
growth must not be misrepresented as a reproducible pre-request snapshot.
