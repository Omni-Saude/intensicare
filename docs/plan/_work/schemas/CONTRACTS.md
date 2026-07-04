# Agent Operating Contracts — IntensiCare v2 Build Plan

Every agent working on this plan MUST follow this contract. Your final message is a data receipt,
not prose for a human. Gates verify your files on disk; an unverifiable claim equals no work.

## General rules (all agents)

1. **Write fence.** Write ONLY the file(s) your task names, under `docs/plan/` or `docs/plan/_work/`.
   Never touch `src/`, `tests/`, or any existing `docs/` file outside `docs/plan/`.
2. **Atomic + incremental.** Write incrementally (append records as you go). For rewrites, write
   `<file>.tmp` then rename.
3. **Evidence discipline — zero silent invention.** Every clinical threshold, coefficient, or cutoff
   you write cites a published reference (guideline/paper) or a `RULE-<CLUSTER>-<NNN>` catalog ID, or
   both. If you cannot source a number, do not write it — record an open question instead.
4. **PT-BR clinical vocabulary** adopted from the legacy catalog is preserved verbatim, accents
   included. Deliverable prose is English.
5. **Precedence when sources conflict:** ADR-001 platform constraints ≻ vision docs ≻ orchestrator
   directives ≻ audit-extracted legacy knowledge. Record conflicts; never resolve one silently.
6. **No status/progress files.** Only your named deliverable(s).
7. **Authoritative rule IDs** come from `docs/rules/extraction/phase2/catalog/*.yaml` (959 IDs).
   `docs/rules/catalog-index.json` is stale — never use it.

## Source brief schema (`_work/briefs/<name>.json`)

```json
{
  "brief_id": "vision",
  "authority": "adr-001|vision|directive|audit",
  "source": {"path": "docs/product/vision.md", "lines": 428, "read_complete": true},
  "source_files": [{"path": "...", "line_ranges": "1-428"}],
  "facts": [
    {"id": "VIS-3.1-01", "claim": "one precise fact, numbers verbatim",
     "kind": "threshold|metric|vocabulary|entity|policy|other", "source_ref": "vision.md §3.1"}
  ],
  "constraints": [
    {"id": "VIS-C-01", "text": "MUST …", "type": "invariant|slo|policy|unit|naming|regulatory",
     "source_ref": "…"}
  ],
  "open_questions": ["…"]
}
```
Target ≤ 10 KB (alert-catalog / design briefs ≤ 24 KB). Facts are for downstream designers who will
NOT read your source — include every load-bearing number with its unit and source_ref.

## Rule-disposition policy + record schema (`_work/dispositions/<shard>.yaml`)

Every rule gets EXACTLY ONE disposition:
- `ADOPT` — verification verdict VERIFIED, fits the vision → carried with citation + test vectors.
- `ADOPT-CORRECTED` — verdict DISCREPANCY → the reference-correct form is designed; legacy deviation
  documented. Never port known-broken behavior. Disputed clinical intent → RATIFY instead.
- `ADAPT` — sound intent, wrong mechanism (e.g. 07:00–07:00 shift windows with month-boundary bugs →
  correct temporal windowing, same clinical semantics).
- `SUPERSEDE` — replaced by a vision-mandated mechanism. Record what supersedes and what is lost.
- `RETIRE` — obsolete with the platform change (Tasy-direct ETL, PM2/uwsgi, legacy-app plumbing). Justify.
- `RATIFY` — cannot be decided by agents. MANDATORY for any rule with escalation band P0, P1, or
  UNVERIFIABLE; for AMBIGUOUS rules worth keeping; and for disputed clinical intent.

```yaml
records:
  - rule_id: RULE-SEPSE-014
    cluster: sepse
    category: care-pathway                # from the catalog entry
    catalog_echo: {status: DISCREPANCY, verdict: "DISCREPANCY (high)"}   # copy EXACTLY from catalog
    source_quote: "verbatim >=20-char substring of the rule's logic/description/edge_cases"
    disposition: ADOPT-CORRECTED
    justification: ">=120 chars; discriminating — a different rule would get a different sentence"
    evidence: ["SSC-2021", "RULE-SEPSE-014"]          # >=1; guideline/paper and/or RULE id
    target: "clinical/domains/sepsis.md#screening"    # required for ADOPT*/ADAPT/SUPERSEDE;
                                                      # RATIFY -> "RATIFICATION.md#<anchor>"; RETIRE -> null
    supersedes_note: null                             # SUPERSEDE only: {replaced_by: "...", lost: "..."}
    escalations: [{item_id: ESC-P1-020, band: P1}]    # echo the bands embedded in your shard input
    ratify_ref: null                                  # RATIFY only: RAT-<CLUSTER>-<NN>
```
`verification.verdict` in the catalog is under each rule's `verification:` key; echo its `verdict`
value (string). If a rule has no verification block, echo `verdict: "NOT_APPLICABLE"`.

## Alert entry schema (`_work/alerts/<domain>.yaml`)

```yaml
domain: sepsis
alerts:
  - alert_id: ALERT-SEPSIS-SCREEN-01     # ALERT-<DOMAIN>-<SLUG>-<NN>
    name: "Triagem de sepse — qSOFA + lactato"
    severity: critical                   # normal|watch|urgent|critical (clinical.* scale)
    trigger: {logic: "explicit boolean logic with thresholds+units", window: PT1H}
    inputs:
      - {name: lactato_arterial, type: quantity, unit: "mmol/L",
         source: "AMH Gold lab_result (LOINC 2524-7)", staleness_max: PT4H}
    evidence:
      - {citation: "Singer M et al. JAMA 2016;315(8):801-810 (Sepsis-3)", rule_refs: [RULE-SEPSE-014]}
    suppression: {dedup_key: "patient_id+alert_id", cooldown: PT6H, rate_limit: "4/24h/patient",
                  maintenance_window_aware: true}
    ppv_budget: {target_ppv: 0.60, est_volume_per_100_beds_day: 6, rationale: "…"}
    response: {required: "avaliação médica beira-leito", ack_sla: PT15M}
    test_vectors:                        # >=3; >=1 with kind: boundary
      - {id: TV-1, kind: fire, inputs: {lactato_arterial: 2.4, qsofa: 2}, expected: fire, note: ""}
      - {id: TV-2, kind: no-fire, inputs: {...}, expected: no-fire, note: ""}
      - {id: TV-3, kind: boundary, inputs: {lactato_arterial: 2.0}, expected: no-fire,
         note: "boundary exact-threshold"}
    reconciliation: {existing_id: SEP-002, status: aligned,   # aligned|extended|changed|new|dropped
                     note: "vs docs/clinical/alert-catalog.md"}
```
Every input `unit` must exist in `_work/units/registry.yaml` (canonical or declared alias). Every
`rule_refs` ID must have disposition ADOPT / ADOPT-CORRECTED / ADAPT.

## Domain doc machine block

Every `docs/plan/clinical/domains/<domain>.md` embeds exactly one fenced block tagged
` ```yaml domain-inputs ` containing: `domain`, `inputs: [{name, type, unit, source}]`,
`alerts: [ALERT-…]` (the IDs this domain defines), `rule_refs: [RULE-…]` (all catalog rules the doc
draws on), `interfaces: {emits_events: [...], consumes: [...]}`.

## Receipts

Your workflow return value is a JSON receipt (schema given per task). Counts in the receipt MUST
match what you wrote to disk — gates re-count.
