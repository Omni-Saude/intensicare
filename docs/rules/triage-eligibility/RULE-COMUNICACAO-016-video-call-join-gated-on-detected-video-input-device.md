# RULE-COMUNICACAO-016 — Video-call join gated on detected video input device

| Field | Value |
|---|---|
| Category | triage-eligibility |
| Type | eligibility |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
The telemedicine room only offers an "Entrar na sala" (join call) button if at least one video input device is detected via the browser's media-devices enumeration at mount; otherwise a "Video Offline" warning result is shown instead, preventing the join action.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| navigator.mediaDevices.enumerateDevices() results | MediaDeviceInfo[] | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| hasVideoDevice | boolean | — |
| rendered control ("Entrar na sala" button vs. Result warning) | UI branch | — |

## Logic
```text
on mount: devices = await navigator.mediaDevices.enumerateDevices()
          videoDevices = devices.filter(d => d.kind === "videoinput")
          hasVideoDevice = videoDevices.length > 0
render:
  if hasVideoDevice: show "Entrar na sala" Button (calls join())
  else: show Result(status="warning", title="Video Offline", subTitle="... conecte um dispositivo de vídeo e recarregue a página.")
```

## Edge cases (as implemented)
The check only runs if navigator.mediaDevices exists at all (guards environments without the API); it does not verify that the device is functional/permitted, only that it is enumerable, and it does not re-check on device hot-plug (only at mount).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BuildVideoChat/BuildVideoChat.tsx | 53-65,91-110 | f9656be2 | primary |
- Merged from: RULE-video-FE-05-001
- Related rules: RULE-COMUNICACAO-032, RULE-COMUNICACAO-028, RULE-COMUNICACAO-029, RULE-COMUNICACAO-030

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
