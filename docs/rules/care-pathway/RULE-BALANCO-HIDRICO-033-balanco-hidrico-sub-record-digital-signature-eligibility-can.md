# RULE-BALANCO-HIDRICO-033 — Balanco-hidrico sub-record digital-signature eligibility (can_assinar) - Entrada/Saida/SinaisVitais

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A fluid-intake record can be digitally signed by the current user only if that user has both a registered CPF and PIN, the record is not already signed, and the user is the original author of the record.

## Inputs

- user.cpf
- user.pin
- instance.assinatura.data_assinatura
- instance.preenchido_por

## Outputs

- can_assinar

## Logic

```text
if not user:
    return False
data_assinatura = bool(instance.assinatura.data_assinatura) if instance.assinatura else False
return bool(
    user.cpf AND user.pin AND (not data_assinatura) AND (user == instance.preenchido_por)
)
```

## Edge cases (as implemented)

instance.assinatura may be null (no signature attempted yet) — handled via the ternary.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/entradas.py` | 159-173 | `8166c07eae` | primary |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/saidas.py` | 160-174 | `8166c07eae` | duplicate |
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/sinais_vitais.py` | 189-203 | `8166c07eae` | duplicate |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-07-007`
- `RULE-balanco-BE-07-013b`
- `RULE-balanco-BE-07-015b`

**Related rules:**

- [RULE-BALANCO-HIDRICO-026](RULE-BALANCO-HIDRICO-026-balanco-hidrico-sub-record-delete-authorization-can-delete-e.md)
- [RULE-BALANCO-HIDRICO-042](RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md)
- [RULE-BALANCO-HIDRICO-045](RULE-BALANCO-HIDRICO-045-fluid-balance-record-signing-deletion-lifecycle.md)

## Notes

Byte-identical logic duplicated in saidas.py (RULE-balanco-BE-07-013b/get_can_assinar) and sinais_vitais.py (RULE-balanco-BE-07-015b).
Byte-identical logic across entradas.py:159-173, saidas.py:160-174, sinais_vitais.py:189-203: returns bool(user.cpf AND user.pin AND not data_assinatura AND user == instance.preenchido_por), or False if no user; data_assinatura derived via ternary on instance.assinatura. No divergence between the three copies -> status OK. Exposed to the frontend as item.can_assinar (RULE-BALANCO-HIDRICO-042).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
