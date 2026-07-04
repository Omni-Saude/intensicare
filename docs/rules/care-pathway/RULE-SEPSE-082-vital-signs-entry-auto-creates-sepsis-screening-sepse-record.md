# RULE-SEPSE-082 — Vital signs entry auto-creates sepsis-screening (Sepse) record linked to latest evolution

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every time a SinaisVitais record is created, the system automatically creates a linked Sepse (sepsis-screening) record for the same encounter, associated with the most recently created Formulario (clinical evolution document) for that encounter, or with no evolution if none exists yet.

## Inputs

- sinais_vitais (created instance) (object reference)
- nr_atendimento (string/integer (encounter number))
- most recent Formulario for nr_atendimento (object reference (nullable))

## Outputs

- Sepse record (object)

## Logic

```text
formulario = Formulario.objects
    .filter(nr_atendimento=sinais_vitais.balanco.nr_atendimento)
    .order_by("-criado_em")
    .first()
Sepse.objects.create(
    sinais_vitais=self.sinais_vitais,
    nr_atendimento=self.sinais_vitais.balanco.nr_atendimento,
    evolucao=formulario if formulario else None,
)
```

## Edge cases (as implemented)

"Most recent" is determined purely by Formulario.criado_em descending, with no filter on tipo or status — a Formulario of ANY professional type/status (even a still-draft one) can be linked as the "evolucao" for the new Sepse record. The actual sepsis scoring/threshold logic (if any) lives on the Sepse model, out of this partition's scope; only the creation trigger and the evolution-linking rule are visible here. A bare leito.save() call immediately follows (lines 146-149) with no field changes, presumably to bump a cache/signal — not itself a business rule.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/sinais_vitais.py` | 134-145 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-07-002`

**Related rules:**

- [RULE-SEPSE-082](RULE-SEPSE-082-vital-signs-entry-auto-creates-sepsis-screening-sepse-record.md)

## Notes

This is the key "trilha" (care-pathway) trigger for sepsis screening in the homecare module: it fires unconditionally on every vital-signs submission, not gated by any vital-sign threshold visible in this file.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
