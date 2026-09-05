# Hosted estate observations — 2026-09-05

Actual anonymous GET requests verified all five configured Hugging Face datasets as public. The source archive lists six source documents and serves its revision-bound inventory and safety metadata. The other four datasets contain only `.gitattributes`, `README.md` and `RIGHTS.md`.

The source archive inventory was retrieved at revision `3f534c86d7b72978963049f6007df1dccd27e601`; SHA-256 is `b2934a85551a89ef191f58025306daf52b7085ef69bda1af7256e10ada9dcd47`. Its published safety record references that same inventory digest. Safety assertions were not independently recomputed because this verification did not request source documents.

Anonymous GitHub retrieval of the project inventory at commit `f0ccb5e63ce5c48ef793b5e1f861f70c38191d32` also succeeded, but its SHA-256 is `afb95099ec70aac3b7a1307d747a3ee421b2127ce545a0217db0766c1ad9a632`. Therefore current matching inventory custody across providers is not established. Reconcile the exact intended inventory revision before publishing an update or asserting synchronization.

The configured Explorer Space API returned HTTP 401. The prospective `edithatogo/dataset-estate-registry` GitHub repository and tree endpoints returned HTTP 404. These observations leave anonymous availability and registration unverified; they do not prove that a private resource does not exist.

Recommended next actions: reconcile inventory versions; retrieve and verify already authorized exact source bytes separately; publish qualified products only through the applicable release controls; diagnose the Explorer identity with authenticated metadata inspection; identify the actual owner-controlled federation registry before attempting registration. No external repository submission or upload occurred.

The companion JSON records request times, immutable revisions, response hashes, statuses and limits. It is factual partial evidence for WI-G4-MED-04/05, not acceptance of either work item. Full response bodies were not retained; source payload restoration, standards interoperability and gate acceptance remain unproved by this receipt.

## Follow-up diagnosis

Owner-authenticated `hf spaces info edithatogo/gfjd-explorer` confirms that the Space exists, is running, and is **private**, at revision `e3d9e838765c70d9d070d9d4a0476aa27a638ee4`. Its files are `.gitattributes`, `README.md`, `index.html` and `style.css`. Private visibility explains anonymous unavailability. The actionable fix is to review the existing Space contents against its accepted-Gold/Platinum boundary, then apply the authorized public visibility policy when the publication controls permit it. Visibility was not changed during this verification.

The six inventory rows have identical source IDs, editions, paths and source SHA-256 values across GitHub and Hugging Face. Differences are all five policy/disposition fields: `rights_class`, `github_policy`, `huggingface_policy`, `publication_status` and `notes`. Hugging Face declares every row `owner_approved_public_archive`, both provider policies `public_exact_edition_archive`, and status `public_replicated`. GitHub declares GBR and USA-MN `review_required`, the other four `unknown`, both policies `metadata_and_receipt_only`, and status `local_metadata_only`. This is a policy-state conflict rather than a source-identity mismatch. Reconcile against the applicable owner decisions before regenerating the public inventory; do not infer rights clearance from the older hosted claim.

The registry target was not inferred solely from a partner name: `docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md:95` explicitly identifies `edithatogo/dataset-estate-registry`. No corresponding concrete registry configuration was found in `config/`, `portfolio/` or `.gfjd/`. Authenticated `gh repo view` also could not resolve that repository. The next implementation step is to establish the actual owner-controlled registry identity (including whether it was renamed), then create the registration against its real contract. No third-party repository permission is implicated by the currently documented owner namespace.
