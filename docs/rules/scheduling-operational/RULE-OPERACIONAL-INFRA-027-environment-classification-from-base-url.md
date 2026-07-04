# RULE-OPERACIONAL-INFRA-027 — Environment classification from base URL

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

Derives the runtime environment label from the API base URL: if the base URL contains the substring "homol" the environment is homologation/staging ("homol"), otherwise production ("prod").

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| baseURL | string | - | - |

## Outputs

| Name | Type | Unit |
|---|---|---|
| urlEnv | string | - |

## Logic

```text
urlEnv = baseURL.includes("homol") ? "homol" : "prod"
```

## Edge cases (as implemented)

Substring match anywhere in the URL. Any URL without "homol" is treated as production (default). Also defines JWT auth-header scheme in axios.ts: Authorization = "JWT <token>".

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/constants.ts` | 11 | `f9656be2` | primary |

- Merged from: RULE-ops-FE-02-001

## Notes

Deployment/environment gate. Low clinical weight but affects behavior toggles keyed on env.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
