# Endpoint Coverage Matrix

> **Generated:** 2026-07-07  
> **Project:** IntensiCare — Backend ↔ Frontend API Cross-Reference  
> **Sources:** `src/intensicare/api/` (11 files) vs `frontend-v2/lib/` + `frontend-v2/app/**/page.tsx` (12 page files)

---

## Summary

| Status | Count | Description |
|---|---|---|
| `connected` | 21 | Backend endpoint has a matching frontend consumer |
| `missing_consumer` | 6 | Backend endpoint exists but no frontend code calls it |
| `missing_endpoint` | 1 | Frontend calls an endpoint that doesn't exist in backend |
| `mocked` | 1 | Frontend UI uses mocked/simulated data (no real backend call) |
| **Total Backend Endpoints** | **28** | All `@router`-decorated endpoints across 11 files |
| **Total Frontend Consumers** | **23** | All exported functions + direct `fetch()` calls + hooks |

---

## REST Endpoint Coverage Matrix

| # | Backend Endpoint | Method | Backend File | Frontend Consumer | Consumer File | Status | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `/api/v1/alerts` | GET | `api/v1/alerts.py:82` | `fetchAlerts(params)` | `lib/api.ts:226` | **connected** | Params: status, mpi_id, limit, offset |
| 2 | `/api/v1/alerts/{alert_id}/acknowledge` | POST | `api/v1/alerts.py:115` | `acknowledgeAlert(id, notes)` | `lib/api.ts:241` | **connected** | Requires auth |
| 3 | `/api/v1/alerts/{alert_id}/resolve` | POST | `api/v1/alerts.py:148` | `resolveAlert(id, resolution, note)` | `lib/api.ts:248` | **connected** | Requires auth; valid resolutions: true_positive, false_positive, intervention_done |
| 4 | `/api/v1/alerts/{alert_id}/escalate` | POST | `api/v1/alerts.py:197` | `escalateAlert(id, reason)` | `lib/api.ts:259` | **connected** | Requires auth |
| 5 | `/api/v1/alerts/{alert_id}/trace` | GET | `api/v1/alerts.py:236` | — | — | **missing_consumer** | Backend returns full AlertResponse; no frontend call exists |
| 6 | `/auth/login` | POST | `api/v1/auth.py:71` | `loginApi(credentials)` | `lib/api.ts:92` | **connected** | Used by `app/login/page.tsx:26` |
| 7 | `/auth/register` | POST | `api/v1/auth.py:92` | `registerApi(data)` | `lib/api.ts:99` | **connected** | Admin-only; used by `app/register/page.tsx:26` |
| 8 | `/auth/logout` | POST | `api/v1/auth.py:122` | `logoutApi()` | `lib/api.ts:106` | **connected** | Requires auth |
| 9 | `/admin/users` | GET | `api/v1/admin.py:156` | `fetchUsers()` | `lib/api.ts:291` | **connected** | Admin-only; used by `app/admin/users/page.tsx:67`, `app/admin/page.tsx:18` |
| 10 | `/admin/users` | POST | `api/v1/admin.py:174` | `createUser(data)` | `lib/api.ts:295` | **connected** | Admin-only; used by `app/admin/users/page.tsx` |
| 11 | `/admin/users/{user_id}` | PUT | `api/v1/admin.py:245` | `updateUser(id, data)` | `lib/api.ts:302` | **connected** | Admin-only; used by `app/admin/users/page.tsx` |
| 12 | `/api/v1/dashboard` | GET | `api/v1/dashboard.py:13` | `fetchDashboard(unit?)` | `lib/api.ts:148` | **connected** | Params: unit; used by `app/dashboard/page.tsx` and `app/command-center/page.tsx:83` |
| 13 | `/api/v1/patients/{mpi_id}/detail` | GET | `api/v1/dashboard.py:35` | `fetchPatientDetail(mpiId)` | `lib/api.ts:213` | **connected** | Used by `app/patient/[id]/page.tsx:48` |
| 14 | `/health` | GET | `api/v1/health.py:246` | `fetchHealth()` | `lib/api.ts:407` | **connected** | Returns PostgreSQL, Redis, ARQ, Athena checks + staleness matrix |
| 15 | `/vitals` | POST | `api/vitals.py:20` | — | — | **missing_consumer** | Vitals ingestion (HL7/FHIR integration); no frontend UI calls this |
| 16 | `/patients/{mpi_id}/status` | GET | `api/patients.py:19` | — | — | **missing_consumer** | Returns PatientStatusResponse; frontend uses `/detail` instead |
| 17 | `/api/v1/thresholds` | GET | `api/thresholds.py:70` | `fetchThresholds(tenantId?)` | `lib/api.ts:345` | **connected** | Admin-only; used by `app/admin/thresholds/page.tsx:41`, `app/admin/page.tsx:18` |
| 18 | `/api/v1/thresholds/{threshold_id}` | GET | `api/thresholds.py:88` | — | — | **missing_consumer** | Get single threshold by ID; no frontend consumer |
| 19 | `/api/v1/thresholds` | POST | `api/thresholds.py:101` | `createThreshold(data)` | `lib/api.ts:360` | **connected** | Admin-only; used by `app/admin/thresholds/page.tsx` |
| 20 | `/api/v1/thresholds/{threshold_id}` | PUT | `api/thresholds.py:146` | `updateThreshold(id, data)` | `lib/api.ts:350` | **connected** | Admin-only; used by `app/admin/thresholds/page.tsx` |
| 21 | `/api/v1/thresholds/{threshold_id}` | DELETE | `api/thresholds.py:218` | — | — | **missing_consumer** | Admin-only; no frontend delete function |
| 22 | `/api/reference-ranges` | GET | `api/reference_ranges.py:87` | `useThreshold()` hook | `lib/thresholds/useThreshold.ts:170` | **connected** | Requires auth; 5-min cache with medical-literature fallback; consumed by `app/patient/[id]/page.tsx` |
| 23 | `/api/clinical-forms` | POST | `api/clinical_forms.py:27` | `fetch('/api/clinical-forms', POST)` | `app/clinical-forms/page.tsx:77` | **connected** | Accepts form_type: rass, cam-icu, bps-nrs; TODO: persist to DB |

---

## WebSocket & Realtime Coverage

| # | Backend Event/Channel | Direction | Backend File | Frontend Subscriber | Consumer File | Status | Notes |
|---|---|---|---|---|---|---|---|
| 24 | `/api/v1/ws?token=<JWT>` | WS connect | `api/v1/ws.py:210` | `RealtimeConnection` | `lib/websocket.ts:44,149` | **connected** | JWT auth via query param; fallback to SSE on error |
| 25 | `alert.raised` | Server→Client | `api/v1/ws.py:229` | `useRealtimeChannel('alert.raised')` | `app/alert-triage/page.tsx:74`, `app/patient/[id]/page.tsx:71` | **connected** | Published by vitals ingestion alert engine |
| 26 | `alert.updated` | Server→Client | `api/v1/ws.py:230` | `useRealtimeChannel('alert.updated')` | `app/alert-triage/page.tsx:79`, `app/patient/[id]/page.tsx:75` | **connected** | Published on acknowledge/resolve/escalate |
| 27 | `bed_grid.updated` | Server→Client | `api/v1/ws.py:231` | `useRealtimeChannel('bed_grid.updated')` | `app/command-center/page.tsx:97`, `app/dashboard/page.tsx` | **connected** | Published when bed status changes |
| 28 | `presence.updated` | Server→Client | `api/v1/ws.py:232` | `useRealtimeChannel('presence.updated')` | — | **missing_consumer** | Documented in backend; no frontend subscription found |
| 29 | `vitals.updated` | Server→Client | `api/v1/ws.py:233` | `useRealtimeChannel('vitals.updated')` | `app/patient/[id]/page.tsx:62` | **connected** | Refreshes patient detail when new vitals arrive |

---

## SSE Fallback

| # | Endpoint | Method | Backend File | Frontend Consumer | Consumer File | Status | Notes |
|---|---|---|---|---|---|---|---|
| 30 | `/api/v1/events/stream` | GET (SSE) | — | `connectSse()` | `lib/websocket.ts:45,203` | **missing_endpoint** | Frontend uses as WebSocket fallback; no SSE endpoint found in any backend router |

---

## Mocked / Simulated Frontend Features

| # | Feature | Frontend File | Status | Notes |
|---|---|---|---|---|
| 31 | Alert Routing Rules (Save) | `app/alert-routing/page.tsx:157` | **mocked** | `setTimeout(resolve, 800)` simulates API save; no backend routing-config endpoint exists |
| 32 | Alert Routing Rules (Load) | `app/alert-routing/page.tsx:117` | **mocked** | `setTimeout` with hardcoded `DEFAULT_RULES`; no backend endpoint |
| 33 | Patient List (Handoff) | `app/handoff/page.tsx:41` | **mocked** | Uses `MOCK_PATIENTS` static data; no backend API calls |
| 34 | Clinical Forms (Patient List) | `app/clinical-forms/page.tsx:39` | **mocked** | Uses `MOCK_PATIENTS` for patient selector; form submission is real (`/api/clinical-forms`) |

---

## Path Discrepancies & Observations

| # | Backend | Frontend | Issue |
|---|---|---|---|
| D1 | `GET /patients/{mpi_id}/status` (`api/patients.py:19`) | `GET /api/v1/patients/{mpi_id}/detail` (`lib/api.ts:213`) | **path_mismatch**: Different endpoints. Backend has `/status`, frontend uses `/detail`. Both are valid but serve different schemas (PatientStatusResponse vs PatientDetailResponse). |
| D2 | `POST /vitals` — no prefix on router (`api/vitals.py`) | — | Inconsistency: vitals router has no `prefix="/api/v1"` while most other routers do; the route resolves to `/vitals` not `/api/v1/vitals`. Verify this is intentional. |
| D3 | `POST /api/clinical-forms` — payload mismatch | `{ mpiId, formId, data }` (`page.tsx:81`) | Frontend sends `mpiId`/`formId`, backend expects `ClinicalFormSubmission` (field `form_type`). Likely a schema mismatch. |

---

## Legend

| Status | Meaning |
|---|---|
| `connected` | Backend endpoint exists AND frontend consumer matches |
| `missing_consumer` | Backend endpoint exists but NO frontend calls it |
| `missing_endpoint` | Frontend calls an endpoint NOT found in backend |
| `mocked` | Frontend uses `setTimeout` / static data instead of real API |
| `path_mismatch` | Both sides have similar endpoints but paths differ |
| `auth_gated` | Endpoint requires authentication that may not be wired |

---

## Totals by Status

| Status | Count |
|---|---|
| `connected` | 21 |
| `missing_consumer` | 6 |
| `missing_endpoint` | 1 |
| `mocked` | 4 |
| `path_mismatch` | 3 |
| **Total Backend Endpoints** | 28 |
| **Total WS Events (backend pub)** | 5 |
| **Total WS Events (frontend sub)** | 4 of 5 |
