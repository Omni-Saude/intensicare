# Judge-Panel Rubric — IntensiCare v2 contested designs

Three topics: `home-surface`, `timeline-model`, `alert-routing`. Three concepts each (a/b/c).
Scorers: clinical-ux-researcher, clinical-safety-officer (holds veto), one persona-proxy per topic
(home-surface → Dra. Fernanda; timeline-model → Dr. Carlos + Enf. Ana; alert-routing → Dr. Rafael).

## Scoring — anchored 1–5, one scorecard file per (scorer × concept)

Write `docs/plan/_work/panels/<topic>/score-<role>-<concept>.yaml`:

```yaml
panel: home-surface
concept: b
scorer: clinical-safety-officer     # clinical-ux-researcher | clinical-safety-officer | persona-proxy
scores:
  safety: 4          # 1 = introduces plausible patient-harm path; 3 = safe with mitigations; 5 = actively hazard-reducing
  persona_fit: 3     # 1 = fails a stated persona criterion; 3 = meets all; 5 = exceeds with measurable gains
  feasibility: 4     # 1 = fights the fixed stack/realtime/token architecture; 5 = falls out of it naturally
  alarm_fatigue_a11y: 4  # 1 = adds noise or fails WCAG/severity triple-encoding; 5 = reduces noise, AAA-critical clean
  innovation: 3      # 1 = pure legacy port; 5 = best-in-class mechanism absent from both sources
veto: false          # clinical-safety-officer ONLY; true disqualifies the concept (state the hazard)
must_fix: ["..."]    # conditions on adoption if this concept wins
salvage: ["..."]     # ideas worth grafting even if this concept loses
rationale: "3-6 lines, cite persona criteria (PER-*) and hazards (HAZ-*) by id"
```

Weights (fixed): safety .30 · persona_fit .25 · feasibility .20 · alarm_fatigue_a11y .15 · innovation .10.
Decision is computed mechanically by `panel_decide.py`; synthesis owner then merges winner + salvage.
Scores are per-concept absolute (not ranked); do not calibrate against the other concepts' scores.
