# G2 dashboard query evidence — 2026-08-22

The previously acquired Power BI HTML shell did not contain a numeric value.
Under the existing owner authorization for the four exact editions, a single
source-semantic query was therefore made against the dashboard's public query
endpoint. Only aggregate result data was retained.

## Bound query

- Packet: `data/methods/g2/G2DASH-GBR-EAW-20260822-01/packet.json`
- Visual: `Volumes` → `Regional/DFJ Volumes`, visual `7945851748`.
- Filters: `Period = Annually`; `Type = Orders applied for`; dates
  `2011-01-01` through `2026-03-02`; region/DFJ `All`.
- Models response SHA-256:
  `668b951bbba9853609ea08bacb1da514111b75183be3c819a44c2c5d3c52f648`.
- Conceptual schema response SHA-256:
  `f999b4daa44a40be1b52c1204b015d4f24153d5b6c4a2c797f38e7e329acbcf6`.
- Visual query SHA-256:
  `d03410feb453a3f1783ca9e836bb3db74b85ed497d45e4669955f3784cc5d98b`.
- Query response SHA-256:
  `e2fe74e71b4bee327e8e3044a1066f87a3af37761bf955ba8a70618980488e23`.

## Source-faithful result

The response contains an annual row labelled `2026` with value **4,917**.
Its count type is `Orders applied for`; the row is the aggregate England and
Wales visual series under the filters above. No case-level records were
retained.

This is now a factual dashboard result, but it is still quarantined supporting
evidence. It does not clear rights, establish comparability with the ODS or
other routes, authorize redistribution, or pass G2. The dashboard's annual
2026 value and the ODS's 2026-Q1 value must not be compared or pooled until
methods adjudication confirms that their periods and definitions align.
