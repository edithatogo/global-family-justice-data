# Proposed service and maintenance levels for v1

These are target operating commitments to be adopted or amended by the institutional host before release. They are not claims about the current scaffold.

## Source currency

- Each source has an expected publication frequency or review class.
- High-priority annual and more frequent sources are checked after their expected publication window.
- Irregular sources receive at least annual verification.
- A source not checked by its next-review date is visibly marked review due.
- Changed, unavailable, or superseded sources enter a named triage queue.

## Incident and correction targets

| Severity | Example | Initial action target | Release implication |
|---|---|---|---|
| 1 — Critical | privacy exposure, compromised release, systemic corruption | immediate escalation and containment | withdraw or block affected output |
| 2 — High | material error affecting a jurisdiction/indicator family | prompt triage and owner assignment | block release; patch or scoped withdrawal |
| 3 — Moderate | bounded error with no material conclusion impact | acknowledge and schedule correction | may release only with documented limitation |
| 4 — Low | editorial or cosmetic issue | backlog and routine maintenance | does not block release |

The host should publish concrete business-day targets appropriate to its staffing and time zones. It must not promise a response speed it cannot sustainably meet.

## Availability and recovery

- Static release downloads and documentation are the authoritative service; dynamic dashboards are secondary views.
- The project defines recovery objectives for repository, release storage, source manifests, and public site.
- Candidate releases require a full restore test; production operations require periodic restore sampling.
- A last known good release remains available unless safety or legal concerns require withdrawal.

## Transparency metrics

Publish at least annually:

- sources overdue for review;
- retrieval success and source changes;
- open corrections/incidents by severity and age;
- release timeliness against the declared schedule;
- coverage and review completeness;
- backup/restore test status;
- unresolved accessibility or reproducibility issues.
