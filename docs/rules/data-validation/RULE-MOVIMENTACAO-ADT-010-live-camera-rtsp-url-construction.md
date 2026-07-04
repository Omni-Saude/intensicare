# RULE-MOVIMENTACAO-ADT-010 — Live camera RTSP URL construction

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
LiveCameraViewSet.list builds an RTSP stream URL from the establishment's camera credentials and the target bed's IP address.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| estabelecimento.login_camera | string |  |  |
| estabelecimento.senha_camera | string |  |  |
| leito.ip_camera | string |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| url | string, rtsp URI |  |

## Logic
```text
senha = estabelecimento.senha_camera
usuario = estabelecimento.login_camera
ip = Leito.objects.get(pk=kwargs["leitos__pk"]).ip_camera
url = f"rtsp://{usuario}:{senha}@{ip}"
```

## Edge cases (as implemented)
Credentials are embedded directly in the URL string (standard RTSP basic-auth-in-URL pattern); no escaping/encoding of special characters in usuario/senha is applied.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference exists. RTSP basic-auth-in-URL is the standard rtsp://user:pass@host convention (RFC 7826/2326 userinfo); a networking pattern, not a clinical rule. Verified against legacy source only.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/camera.py | 18-27 | 8166c07e | primary |
- Merged from: RULE-leito-BE-05-010
- Related rules: RULE-MOVIMENTACAO-ADT-027, RULE-MOVIMENTACAO-ADT-028

## Notes
Endpoint is protected by HasAPIKey rather than user JWT auth - a distinct authentication mechanism from the rest of the API surface in this partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
