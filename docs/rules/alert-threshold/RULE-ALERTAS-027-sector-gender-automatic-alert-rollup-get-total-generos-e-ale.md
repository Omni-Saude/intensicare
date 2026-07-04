# RULE-ALERTAS-027 — Sector gender + automatic-alert rollup (get_total_generos_e_alertas_automaticos)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | scoring |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | alertas |

## Rule

Sector-level (automatica/homecare) rollup KPI. For each occupied bed it inspects every automatic track's get_payload()["alerta"] and classifies the bed VERMELHO if ANY track is VERMELHO, else AMARELO if ANY is AMARELO, else NEUTRO; separately it tallies the patient gender into {M, F, N, O}. Returns (generos, alertas). Feeds setor/estabelecimento dashboards via the get_total_generos serializer (setor.py:184, estabelecimento.py:145).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| leitos | iterable[Leito] | - | only leito.ocupado beds counted |
| track get_payload()['alerta'] | string | - | {VERMELHO, AMARELO, NEUTRO, null} |
| trilha.ie_sexo (v1) / trilha.paciente.genero (v3) | string | - | {M, F, N, O} |

## Outputs

| Name | Type | Unit |
|---|---|---|
| generos | dict[str,int] | bed count |
| alertas {VERMELHO, AMARELO, NEUTRO} | dict[str,int] | bed count |

## Logic

```text
generos = {"M": 0, "F": 0, "N": 0, "O": 0}
alertas = {"VERMELHO": 0, "NEUTRO": 0, "AMARELO": 0}
for leito in leitos:
    trilhas = []
    if leito.ocupado:
        trilha = None
        for Trilha in Leito.get_trilhas_automaticas():
            trilha_temp = get_trilha(Trilha, leito, leito.tipo)
            if trilha_temp:
                trilha = trilha_temp                 # keeps the LAST truthy track
                trilhas.append(trilha.get_payload())
        trilhas_list = [t.get("alerta") for t in trilhas]
        if "VERMELHO" in trilhas_list:
            alertas["VERMELHO"] += 1
        elif "AMARELO" in trilhas_list:
            alertas["AMARELO"] += 1
        else:
            alertas["NEUTRO"] += 1
        # gender source differs by track version
        if not isinstance(trilha, tuple(Leito.get_trilhas_automaticas_v3())):
            if trilha and trilha.ie_sexo and (generos.get(trilha.ie_sexo) == 0 or generos.get(trilha.ie_sexo)):
                generos[trilha.ie_sexo] += 1
        else:
            if trilha and trilha.paciente.genero and (generos.get(trilha.paciente.genero) == 0 or generos.get(trilha.paciente.genero)):
                generos[trilha.paciente.genero] += 1
return generos, alertas
```

## Edge cases (as implemented)

A bed whose tracks all resolve to None leaves trilha=None: trilhas_list is empty so it falls through to the NEUTRO bucket, and the gender branch short-circuits on the falsy `trilha` (no increment, no crash). Gender is read from the LAST truthy track only (trilha is overwritten each loop), and that track's class decides v1 (ie_sexo) vs v3 (paciente.genero). The guard `generos.get(k) == 0 or generos.get(k)` increments only when k is one of M/F/N/O; any other gender key returns None from .get and is silently dropped. Bed color keys on get_payload()['alerta'] membership, so a null/unknown alerta is treated as NEUTRO.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 764-816 | `8166c07e` | primary |

- Merged from: RULE-gap6-01
- Related rules: RULE-ALERTAS-002, RULE-ALERTAS-028, RULE-TENANCY-ORGANIZACAO-034

## Notes

Sector KPI surfaced by the get_total_generos serializer (setor.py:184, estabelecimento.py:145) and consumed by setor/estabelecimento dashboards. The VERMELHO>AMARELO>NEUTRO precedence mirrors RULE-ALERTAS-002 but keys on each track's get_payload()['alerta'] rather than the four manual pathways. Previously uncited: RULE-TENANCY-ORGANIZACAO-034 cites only the serializer method, not this bed->sector severity-max rollup implementation.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
