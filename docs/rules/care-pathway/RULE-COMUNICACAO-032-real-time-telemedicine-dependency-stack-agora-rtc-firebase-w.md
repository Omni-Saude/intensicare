# RULE-COMUNICACAO-032 — Real-time telemedicine dependency stack (Agora RTC + Firebase + websocket)

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | comunicacao |

## Rule
package.json pins agora-rtc-react ^1.1.1 (Agora.io real-time video/audio conferencing SDK for React), firebase ^8.7.1 (used for storage — see RULE-DATA-FE-09-004's firebasestorage.googleapis.com whitelist — and likely realtime DB/auth), and the raw websocket ^1.0.34 package, alongside chart.js/react-chartjs-2 (vitals/dashboard charting), downloadjs (report/ file downloads), antd-mask-input (masked form inputs, e.g. Brazilian document/phone formats), and nprogress (route-transition loading bar). Together these indicate the product ("teleUTI") supports live video/audio tele-consultation and real-time data synchronization as a core care-delivery workflow.

## Logic
```text
dependencies include: {
  "agora-rtc-react": "^1.1.1",   # live video/audio calls
  "firebase": "^8.7.1",          # storage/realtime/auth backend
  "websocket": "^1.0.34",        # additional realtime channel
  "chart.js"/"react-chartjs-2": "^3.9.1"/"^4.3.1",  # vitals/analytics charts
  "downloadjs": "^1.4.7",        # client-side file download (e.g. PDF reports)
  "antd-mask-input": "^2.0.7"    # masked inputs (e.g. CPF/phone)
}
```

## Edge cases (as implemented)
This is inferred purely from the dependency manifest; the actual call sites, video-call business rules (e.g. who can initiate a call, session limits), and mask patterns are implemented in files outside this partition's scope and were not examined here.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | package.json | 20-46 | f9656be2 | primary |
- Merged from: RULE-CAREPATH-FE-09-009
- Related rules: RULE-COMUNICACAO-016, RULE-COMUNICACAO-028, RULE-COMUNICACAO-029, RULE-COMUNICACAO-030

## Notes
Dependency-manifest-only evidence per task instructions ("dependency pins with business significance").

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
