# IntensiCare v2 Build Plan — How to Read This

**Status:** complete, awaiting human ratification (this PR). Built 2026-07-04 by an orchestrated
multi-agent effort (~200 specialist agent runs across 5 gated phases) from the mission prompt
`docs/prompts/intensicare-build-plan-orchestrator-prompt.md`, fusing the 959-rule legacy audit
(`docs/rules/`), the 351-item escalation queue, the 18 legacy design ADRs, and the product vision
(AMH Data Platform consumer, ADR-001).

## Reading order

1. **[executive-summary.md](executive-summary.md)** — the whole plan in two pages.
2. **[RATIFICATION.md](RATIFICATION.md)** — every decision a human must make (start with the 12 P0
   items and the five audit asks). The design proceeds on recommended defaults marked `pending RAT-*`.
3. **[traceability-matrix.md](traceability-matrix.md)** — all 959 rules + 351 escalations + 18 design
   ADRs with their dispositions. *Generated* from `_work/dispositions/` — regenerate, never hand-edit.
4. **product/** — [product-spec.md](product/product-spec.md) (stories × personas × metrics),
   [journey-maps.md](product/journey-maps.md) (MOT-01..20).
5. **clinical/** — [units-registry.md](clinical/units-registry.md) (67 canonical parameters),
   [alert-catalog.md](clinical/alert-catalog.md) (*generated*; 50 alerts, 266 test vectors),
   [domains/](clinical/domains/) (9 specs), [hazard-log.md](clinical/hazard-log.md) (ISO 14971, 34 hazards).
6. **architecture/** — [system-architecture.md](architecture/system-architecture.md),
   [alert-engine.md](architecture/alert-engine.md), [data-model.md](architecture/data-model.md),
   [api/](architecture/api/) (OpenAPI 3.1 + AsyncAPI), [security-lgpd.md](architecture/security-lgpd.md),
   [observability-slo.md](architecture/observability-slo.md), [adr/](architecture/adr/) (ADR-002..005).
7. **design/** — [design-language.md](design/design-language.md), [design-tokens.md](design/design-tokens.md),
   [component-library.md](design/component-library.md), [accessibility-standard.md](design/accessibility-standard.md),
   [screens/](design/screens/) (7 flow specs).
8. **delivery/** — [roadmap.md](delivery/roadmap.md), [test-strategy.md](delivery/test-strategy.md),
   [validation-plan.md](delivery/validation-plan.md), [regulatory-plan.md](delivery/regulatory-plan.md),
   **[build-orchestrator-blueprint.md](delivery/build-orchestrator-blueprint.md)** (execution guide,
   BUILD-ADR-001, WO-001..040) and **[build-kickoff-prompt.md](delivery/build-kickoff-prompt.md)**
   (paste-ready prompt that starts the build phase).

## Decision log

- Rule dispositions: `_work/dispositions/` (machine truth behind the matrix); escalation resolutions:
  `_work/escalations/`.
- Contested-design judge panels (3 topics × 3 concepts × 2 scorers + safety veto):
  `_work/panels/*/decision.yaml`.
- Reconciliation barriers C1–C3 (11 conflicts, all decided + safety-countersigned):
  `_work/barriers/*/decisions.yaml`.
- Adversarial review (2 rounds, 39 CONFIRMED findings: 36 fixed, 3 accepted-risk — listed in
  RATIFICATION): `_work/redteam/`.

## Re-verify everything

```bash
python3 docs/plan/_work/scripts/gate_dod.py --phase E
```

Gate results ship in `_work/gates/` (machine-readable, one JSON per gate).

## Provenance notes

- `docs/implementation-plan.md` and `docs/review-queue.md` were retired from the worktree by a
  parallel work stream after extraction; citations resolve at commit `aa5e786`, and their full
  extracted content lives in `_work/briefs/` (hash-pinned in `_work/gates/inputs-manifest.json`).
- `docs/rules/catalog-index.json` is stale (947 of 959) — the phase-2 catalog YAMLs are the only
  authoritative rule-ID source.
- Process economy (token budget, user-directed): panel scoring used 2 standing judges instead of 5;
  adversarial review capped at 2 rounds (cap + accepted-risk path recorded in the ledger); final
  editorial pass was performed by the orchestrator at shutdown; the numeric-provenance advisory
  sweep is delegated to the build phase (blueprint §6 traceability duty).
