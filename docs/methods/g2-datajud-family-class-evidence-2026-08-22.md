# G2 DataJud family-class evidence — 2026-08-22

This record closes the factual API-target blocker for the known-source pilot.
The request was made under the existing owner authorization for the four exact
editions and retained only as aggregate supporting evidence. It does not
accept rights, promote a row, authorize publication, or pass G2.

## Source-faithful class definition

The official CNJ Tabelas Processuais Unificadas materials identify class
`1389` as **Ação de Alimentos**. The class definition is bound to the CNJ
public class consultation and the official state-justice class table:

- <https://www.cnj.jus.br/sgt/consulta_publica_classes.php>
- <https://www.cnj.jus.br/wp-content/uploads/2011/02/tabela-de-classes-justia-estadual.pdf>

No class code was inferred from the earlier unfiltered bucket list.

## Bounded request and result

- Packet: `data/methods/g2/G2API-BRA-TJSP-20260822-01/packet.json`
- Endpoint: `https://api-publica.datajud.cnj.jus.br/api_publica_tjsp/_search`
- Request: `size: 0`, `match` on `classe.codigo = 1389`, and a `case_classes`
  terms aggregation.
- Request SHA-256: `77c4f319cce37387236a7c19f9a1827ec78d070a4aba7255ce475bd0695e7979`.
- Response SHA-256: `626d18292c23ffe5e369b3c82c5477f9265686dca86f195021bc8f100c903da3`.
- HTTP status: `200`; response size: `258` bytes; retained hit count: `0`.
- The aggregate contains a matching class bucket with document count `2`.

The result establishes a source-defined aggregate for the selected class. It
does not establish a time basis, denominator, geography, outcome measure or
comparability with the ODS, dashboard or PDF rows. The value therefore remains
quarantined and descriptive-only until the methods, rights/security and
owner-adjudication work is complete.

## Disposition

This is factual known-source evidence for G2-C02 preparation. It is not an
extraction, methods adjudication, rights clearance, independent assurance,
publication, release or G2 acceptance. The API key is not recorded here.
