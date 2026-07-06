# Traceability Matrix — IntensiCare v2 Build Plan

Generated mechanically from `docs/plan/_work/dispositions/` and `docs/plan/_work/escalations/`. Do not hand-edit below the marker; regenerate with `python3 docs/plan/_work/scripts/build_matrix.py`.

<!-- BEGIN GENERATED -->

## Summary

| Disposition | Count |
|---|---:|
| ADOPT | 194 |
| ADOPT-CORRECTED | 57 |
| ADAPT | 209 |
| SUPERSEDE | 66 |
| RETIRE | 229 |
| RATIFY | 204 |
| **Total** | **959** |

| Escalation band | Items |
|---|---:|
| P0 | 12 |
| P1 | 45 |
| P2 | 35 |
| P3 | 99 |
| UNVERIFIABLE | 101 |
| AMBIGUOUS | 56 |
| ADDENDUM | 3 |

## Rules (959)

| Rule | Name | Cluster | Verdict | Disposition | Target | Bands |
|---|---|---|---|---|---|---|
| RULE-ALERTAS-001 | Count triggered criteria (contar_qtd_criterios_alerta) | alertas | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-alertas-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-ALERTAS-002 | Aggregate alert counts across movimentacoes | alertas | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-alertas-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-ALERTAS-003 | Criteria-count -> alert color mapping (define_tipo_alerta) + | alertas | NOT_APPLICABLE | ADOPT-CORRECTED | [alert-engine.md §alert-color-mapping](architecture/alert-engine.md) | P3 |
| RULE-ALERTAS-004 | Single-criterion alert flag (esta_alerta) | alertas | NOT_APPLICABLE | ADOPT | [alert-engine.md §alert-color-mapping](architecture/alert-engine.md) | — |
| RULE-ALERTAS-005 | Bed-level alert rollup util (define_tipo_alerta_leito) - DEA | alertas | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ALERTAS-006 | Bed alert color aggregation (get_alerta_leito, with sepse LA | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §bed-alert-rollup](architecture/alert-engine.md) | — |
| RULE-ALERTAS-007 | Automatic-bed alert ignoring attendance (alerta_nao_assistid | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §unattended-severity](architecture/alert-engine.md) | — |
| RULE-ALERTAS-008 | Homecare-bed alert ignoring attendance (PioraClinica + Sepse | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §unattended-severity](architecture/alert-engine.md) | — |
| RULE-ALERTAS-009 | Bed 'attended' (assistido) determination | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §acknowledgement](architecture/alert-engine.md) | — |
| RULE-ALERTAS-010 | Automatic-bed payload alert + attendance flag | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §acknowledgement](architecture/alert-engine.md) | — |
| RULE-ALERTAS-011 | Assistido-overrides-alerta status color precedence (frontend | alertas | NOT_APPLICABLE | ADAPT | [clinical-forms.md §status-precedence](design/screens/clinical-forms.md) | — |
| RULE-ALERTAS-012 | conteudo_trilha_criterios - RED-alert content extraction for | alertas | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §alert-payload-schema](architecture/alert-engine.md) | — |
| RULE-ALERTAS-013 | conteudo_trilha_automatica_criterios - RED-alert content ext | alertas | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §alert-payload-schema](architecture/alert-engine.md) | — |
| RULE-ALERTAS-014 | conteudo_observacao_criterios - tipo-dependent whitelist fil | alertas | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-alertas-03](RATIFICATION.md) | AMBIGUOUS |
| RULE-ALERTAS-015 | conteudo_trilha_homecare_criterios - RED-alert content extra | alertas | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §alert-payload-schema](architecture/alert-engine.md) | — |
| RULE-ALERTAS-016 | Bed observation dispatch with VERMELHO de-duplication (envia | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §suppression](architecture/alert-engine.md) | — |
| RULE-ALERTAS-017 | Assist-action trilha resolution: dual Movimentacao/Leito mod | alertas | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ALERTAS-018 | Mensageiro.enviar_observacao - hardcoded RED-level system al | alertas | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ALERTAS-019 | Mensageiro.enviar_observacao_automatica_e_homecare - hardcod | alertas | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ALERTAS-020 | NEUTRO alert resets assistido flag on save (shared behavior) | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §acknowledgement](architecture/alert-engine.md) | — |
| RULE-ALERTAS-021 | Trilha (care-pathway) model mapping per bed type, with v3 mo | alertas | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ALERTAS-022 | Marking a trilha as assistido - bulk update for v3 models, i | alertas | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail](architecture/security-lgpd.md) | — |
| RULE-ALERTAS-023 | AssistidoPor audit snapshot created only when marking as ass | alertas | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail](architecture/security-lgpd.md) | — |
| RULE-ALERTAS-024 | Care-pathway (trilha) status severity color palette (statusT | alertas | NOT_APPLICABLE | ADAPT | [clinical-forms.md §severity-palette](design/screens/clinical-forms.md) | — |
| RULE-ALERTAS-025 | Semantic status color tokens (success/info/warning/danger/er | alertas | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-ALERTAS-026 | Record lifecycle status to icon/color mapping (handleIconByS | alertas | NOT_APPLICABLE | ADOPT | [clinical-forms.md §record-status](design/screens/clinical-forms.md) | — |
| RULE-ALERTAS-027 | Sector gender + automatic-alert rollup (get_total_generos_e_ | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §sector-dashboard-kpis](architecture/alert-engine.md) | — |
| RULE-ALERTAS-028 | Sector automatic-alert count keyed on alerta_nao_assistido ( | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §sector-dashboard-kpis](architecture/alert-engine.md) | — |
| RULE-ALERTAS-029 | Sector assisted-bed counts (get_total_assistidos_automatica  | alertas | NOT_APPLICABLE | ADAPT | [alert-engine.md §sector-dashboard-kpis](architecture/alert-engine.md) | — |
| RULE-ANTIMICROBIANO-001 | Antimicrobiano alert color (active - calcular_alerta_v2) | antimicrobiano | NOT_APPLICABLE | SUPERSEDE | [pharmaco-interaction.md §antimicrobial-alert-severity](clinical/domains/pharmaco-interaction.md) | — |
| RULE-ANTIMICROBIANO-002 | Antimicrobiano alert color (legacy unused - calcular_alerta) | antimicrobiano | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-ANTIMICROBIANO-003 | Antimicrobial stewardship criteria catalog (12 criteria: dur | antimicrobiano | VERIFIED | ADAPT | [pharmaco-interaction.md §antimicrobial-stewardship-criteria](clinical/domains/pharmaco-interaction.md) | — |
| RULE-AUDITORIA-LOGS-001 | Date-range filter boundary formula (start-of-day / end-of-da | auditoria-logs | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-auditoria-logs-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-AUDITORIA-LOGS-002 | request_body capture (GET vs write methods, JSON fallback) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-003 | response_body capture (JSON then raw-text fallback) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-004 | Device classification from user agent (dispositivo) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-005 | Log retention / purge threshold (2 weeks, hard delete) | auditoria-logs | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §retention](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-006 | Default and selectable page size for log list | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-007 | Top-4 most-accessed-routes limit | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-008 | 'Problematic routes' selection: one path per status code, to | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-009 | 'Undesirable status codes' chart exclude is a no-op (AND ins | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-010 | Status-code badge color mapping (get_status_style) — 399 bou | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-011 | HTTP method badge color mapping (get_method_style) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-012 | Device icon mapping (get_icon) missing branches for tablet/e | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-013 | is_status_code validity check — 599 boundary, unused (dead c | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-014 | pretty_json double-encodes string-typed JSON values instead  | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-015 | Log-detail field rendering rules (skip falsy, JSON/HTML/plai | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-016 | Request/response log-capture payload | auditoria-logs | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-017 | Asynchronous log persistence dispatch | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-018 | Unconditional what-gets-logged predicate (every response) | auditoria-logs | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-019 | Client IP and public/private classification | auditoria-logs | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-020 | Geolocation enrichment via GeoIP2 (async stage) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-021 | Soft-delete mixin present but not exercised for logs | auditoria-logs | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-022 | Log dashboard access control (authenticated-only, no staff/o | auditoria-logs | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-auditoria-logs-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-023 | Default log list ordering (most recent first) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-024 | Dead nested duplicate of EstadoLogView | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-025 | UUID-in-path anonymization is display-only, not applied to r | auditoria-logs | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-026 | LogModel *_tag() HTML-table helper methods are dead code | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-027 | request.META sanitization for log storage | auditoria-logs | NOT_APPLICABLE | ADAPT | [security-lgpd.md §data-minimization](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-028 | Authenticated-user attribution on log entries | auditoria-logs | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-029 | Log persistence validation gate | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-030 | Allowed log-list filter fields whitelist | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-031 | Geo cascade endpoints use a narrower filter whitelist than t | auditoria-logs | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUDITORIA-LOGS-032 | is_html heuristic (broad false-positive risk) | auditoria-logs | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-033 | Log field-exposure scoping (LogSimpleSerializer vs LogSerial | auditoria-logs | NOT_APPLICABLE | ADAPT | [security-lgpd.md §data-minimization](architecture/security-lgpd.md) | — |
| RULE-AUDITORIA-LOGS-034 | Country -> region -> city cascading filter (city not re-scop | auditoria-logs | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUDITORIA-LOGS-035 | geolocalizacao field defaults to empty dict, never null in p | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUDITORIA-LOGS-036 | History-skip on non-substantive field changes | auditoria-logs | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-001 | GrupoAcesso permission catalog payload computation | auth-usuarios | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-auth-usuarios-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-AUTH-USUARIOS-002 | User cargos (roles) empresa-scoped lookup | auth-usuarios | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-auth-usuarios-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-AUTH-USUARIOS-003 | Super-admin (chatbot) permission predicate | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §privileged-service-accounts](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-004 | Partner-required permission predicate | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-005 | Owner-organization object permission predicate | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §object-level-authorization](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-006 | Authenticated-user predicate (IsAuthenticated) | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §authenticated-dependency](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-007 | Empresa read vs read-write permissions are identical | auth-usuarios | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §read-write-permission-separation](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-008 | Hierarchical permission cascade (get_permissoes_empresa/esta | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §hierarchical-rbac-cascade](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-009 | Scope-based RBAC permission dispatch | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §scope-based-authorization](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-010 | GrupoAcesso hierarchical scope resolution | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §scope-priority-resolution](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-011 | Permission lookup hierarchical scope resolution | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §scope-priority-resolution](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-012 | GrupoAcesso usuarios field suppressed on list/destroy action | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-013 | User representation scopes setores list to current empresa | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-scoped-serialization](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-014 | User queryset restricted to active users scoped to empresa | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-scoped-queryset](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-015 | GET and PATCH bypass can_manage_usuario permission | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §explicit-per-method-permissions](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-016 | Permission gate for rejecting/closing SEPSE protocol | auth-usuarios | NOT_APPLICABLE | ADAPT | [sepsis.md §protocol-rejection-permission](clinical/domains/sepsis.md) | — |
| RULE-AUTH-USUARIOS-017 | Sector-card click and audit-button permission gating | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-gated-audit-access](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-018 | Settings-gear header icon visibility | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-019 | Company-switch dropdown visibility | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-020 | Permission-string SSR route guard (validateRoute), incl. dea | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §deny-by-default-ssr-gate](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-021 | Bed-management page reuses access-group permission | auth-usuarios | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUTH-USUARIOS-022 | Automatica-only shortcuts not enforced server-side | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-side-tenant-type-enforcement](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-023 | Redirect authenticated user away from login page | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §authenticated-login-redirect](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-024 | Post-login company-selection redirect decision tree | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §post-login-routing](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-025 | Professional profile self-or-permission access gate | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §object-level-authorization](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-026 | Homecare-only "Gestão de Pacientes" tab | auth-usuarios | NOT_APPLICABLE | ADAPT | [clinical-forms.md §homecare-tenant-gating](design/screens/clinical-forms.md) | — |
| RULE-AUTH-USUARIOS-027 | Admin sidebar menu-item visibility gating | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-based-navigation](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-028 | Per-professional evolution-form authoring eligibility | auth-usuarios | NOT_APPLICABLE | ADAPT | [clinical-forms.md §role-based-authoring](design/screens/clinical-forms.md) | — |
| RULE-AUTH-USUARIOS-029 | Login cascade - local auth first (incl. HTTP 202 status) | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §authentication](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-030 | External SSO fallback with auto-provisioning | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §sso-entitlement-check](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-031 | Auto-hash plaintext password on user save | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §authentication](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-032 | User-company membership grants 'u' access and cascades group | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §membership-cascade-cleanup](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-033 | Establishment membership auto-creates company membership; de | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenancy-hierarchy](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-034 | Sector membership auto-creates establishment membership; del | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenancy-hierarchy](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-035 | GrupoAcesso update() replaces entire permission set | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §permission-assignment](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-036 | GrupoAcesso update() replaces entire usuarios membership | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §permission-assignment](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-037 | Full permission catalog exposure | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-038 | User creation links to current empresa and syncs setores/gru | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §user-provisioning](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-039 | User update performs diff-based setor sync scoped to current | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §user-provisioning](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-040 | User deletion is a soft-delete (is_active flag) | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §user-deactivation](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-041 | Session cookie lifetimes and token verify/refresh workflow | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §session-management](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-042 | Effective-permission intersection computation | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §effective-permissions](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-043 | API key name uniqueness | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-044 | Clinical/administrative role (cargo) enumeration — backend m | auth-usuarios | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §cargos](design/screens/clinical-forms.md) | P3 |
| RULE-AUTH-USUARIOS-045 | User access-role codes (proprietario/usuario/monitor) — back | auth-usuarios | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-auth-usuarios-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-AUTH-USUARIOS-046 | Professional council (conselho) and state-of-council enumera | auth-usuarios | NOT_APPLICABLE | ADOPT | [clinical-forms.md §conselho](design/screens/clinical-forms.md) | — |
| RULE-AUTH-USUARIOS-047 | Access-level enumeration (read vs read-write) — dormant | auth-usuarios | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUTH-USUARIOS-048 | Access group must belong to exactly one scope (empresa XOR e | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §scope-exclusivity](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-049 | Company-context required for request | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-context-required](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-050 | GrupoAcesso incoming permissoes payload rewrite | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-051 | User must belong to a group's scope before joining that acce | auth-usuarios | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §group-scope-membership-check](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-052 | LoginSerializer required-field validation never enforced | auth-usuarios | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §login-input-validation](architecture/security-lgpd.md) | P3 |
| RULE-AUTH-USUARIOS-053 | User payload field renames with empty-list edge case | auth-usuarios | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-AUTH-USUARIOS-054 | CPFValidator — Brazilian CPF check-digit validation | auth-usuarios | NOT_APPLICABLE | ADOPT | [security-lgpd.md §cpf-validation](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-055 | Username normalization before login submit | auth-usuarios | NOT_APPLICABLE | ADOPT | [security-lgpd.md §username-normalization](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-056 | exceto_metodo misspells PATCH as PATH across write viewsets | auth-usuarios | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-AUTH-USUARIOS-057 | Authorization header format | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §auth-token-scheme](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-058 | RBAC permission catalog | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-catalog](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-059 | Access group aggregates the full permission map | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §permission-catalog](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-060 | Company monitoring-modality enumeration (duplicate of LeitoT | auth-usuarios | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-config](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-061 | Context-switch destinations exclude bed level | auth-usuarios | NOT_APPLICABLE | RETIRE | — | — |
| RULE-AUTH-USUARIOS-062 | JWT token expiration/refresh policy | auth-usuarios | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §token-lifetime](architecture/security-lgpd.md) | — |
| RULE-AUTH-USUARIOS-063 | Shared default signing PIN (Usuario.pin defaults to settings | auth-usuarios | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-auth-usuarios-02](RATIFICATION.md) | ADDENDUM |
| RULE-BALANCO-HIDRICO-001 | Balanco Hidrico acumulado (cumulative fluid balance) | balanco-hidrico | VERIFIED | ADOPT | [hemodynamics.md §fluid-balance-cumulative](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-002 | Balanco Hidrico ganhos (daily intake total) | balanco-hidrico | VERIFIED | ADOPT | [hemodynamics.md §fluid-intake-daily](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-003 | Balanco Hidrico perdas (daily output total) | balanco-hidrico | VERIFIED | ADOPT | [hemodynamics.md §fluid-output-daily](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-004 | Balanco Hidrico diurno (day-shift balance 07:00-19:00) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-005 | Balanco Hidrico noturno (night-shift balance by subtraction) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-006 | 24h fluid balance = intake minus output over the 07:00-07:00 | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-03](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-007 | Ganhos (fluid intake) summed over the 07:00-07:00 nursing da | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-04](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-008 | Diureses (urine output) summed over the 07:00-07:00 nursing  | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-05](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-009 | Evacuacoes (bowel movements) summed over the 07:00-07:00 nur | balanco-hidrico | DISCREPANCY | ADAPT | [hemodynamics.md §gi-output-nursing-day](clinical/domains/hemodynamics.md) | P2 |
| RULE-BALANCO-HIDRICO-010 | Maximum temperature over the 07:00-07:00 nursing day | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-06](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-011 | Maximum HGT (capillary blood glucose) over the 07:00-07:00 n | balanco-hidrico | DISCREPANCY | ADAPT | [hemodynamics.md §hgt-max-nursing-day](clinical/domains/hemodynamics.md) | P2 |
| RULE-BALANCO-HIDRICO-012 | Formulario - agregacoes de 24h (evolucao) incl. balanco hidr | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-013 | Fluid-balance visao-geral 2-hour time-bucketing (08:00-start | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-08](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-014 | Fluid balance 24h accrual on intake (entrada) | balanco-hidrico | VERIFIED | ADAPT | [hemodynamics.md §fluid-balance-accrual](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-015 | Fluid balance 24h accrual on output (saida) | balanco-hidrico | VERIFIED | ADAPT | [hemodynamics.md §fluid-balance-accrual](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-016 | tempo_criacao - horas desde a criacao (shared helper) | balanco-hidrico | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-09](RATIFICATION.md) | P1 |
| RULE-BALANCO-HIDRICO-017 | SinaisVitais.anterior - leitura anterior de sinais vitais | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-10](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-018 | Blood-pressure display composition (systolic/diastolic) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-11](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-019 | Fluid-balance pain-scale conditional (NRS 0-10 / BPS 3-12) | balanco-hidrico | VERIFIED | ADOPT-CORRECTED | [neuro-sedation.md §pain-assessment-nrs-bps](clinical/domains/neuro-sedation.md) | P3 |
| RULE-BALANCO-HIDRICO-020 | Default volume for enteral diet intake entry | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-12](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-021 | Default volume for spontaneous presence output | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-13](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-022 | Presence-level to volume mapping for evacuacao/vomito output | balanco-hidrico | DISCREPANCY | ADAPT | [hemodynamics.md §output-volume-semiquantitative](clinical/domains/hemodynamics.md) | P3 |
| RULE-BALANCO-HIDRICO-023 | Default clinical-day cutoff (07:00) for balanco hidrico | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-14](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-024 | Fixed clinical shift window for fluid balance (07:00-07:00) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-15](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-025 | Fluid-balance overview cell visibility threshold (grid vs mo | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-BALANCO-HIDRICO-026 | Balanco-hidrico sub-record delete authorization (can_delete) | balanco-hidrico | NOT_APPLICABLE | ADAPT | [security-lgpd.md §delete-authorization](architecture/security-lgpd.md) | P3 |
| RULE-BALANCO-HIDRICO-027 | 07:00 shift boundary assigns pre-07:00 entries to previous d | balanco-hidrico | NOT_APPLICABLE | ADOPT | [hemodynamics.md §nursing-day-assignment](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-028 | Medical-evolution 24h-indicator gate vs value source mismatc | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-16](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-029 | Fluid-balance intake type decision tree | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fluid-intake-form](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-030 | Oral-diet acceptance conditional volume | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §oral-diet-acceptance](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-031 | Fluid-balance output type decision tree | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fluid-output-form](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-032 | Fluid-balance vital-sign ventilation conditional | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §ventilation-o2-fio2-conditional](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-033 | Balanco-hidrico sub-record digital-signature eligibility (ca | balanco-hidrico | NOT_APPLICABLE | ADAPT | [security-lgpd.md §digital-signature-eligibility](architecture/security-lgpd.md) | — |
| RULE-BALANCO-HIDRICO-034 | Fluid-balance action authorization (manage / delete permissi | balanco-hidrico | NOT_APPLICABLE | ADAPT | [security-lgpd.md §action-permission-gating](architecture/security-lgpd.md) | — |
| RULE-BALANCO-HIDRICO-035 | List endpoint required-day + auto-create with mismatched day | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-BALANCO-HIDRICO-036 | Balanco hidrico auto-provisioning, no direct write endpoints | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | — |
| RULE-BALANCO-HIDRICO-037 | Daily fluid-balance auto-creation for occupied homecare beds | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | — |
| RULE-BALANCO-HIDRICO-038 | Entrada soft-delete adjusts 24h fluid balance and logs audit | balanco-hidrico | VERIFIED | ADAPT | [hemodynamics.md §fluid-balance-recompute-on-delete](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-039 | Saida soft-delete adjusts 24h fluid balance and logs audit a | balanco-hidrico | VERIFIED | ADAPT | [hemodynamics.md §fluid-balance-recompute-on-delete](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-040 | Entrada/Saida write manage_data payload injection (balanco i | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | — |
| RULE-BALANCO-HIDRICO-041 | Fluid-balance (balanco hidrico) row type-label resolution an | balanco-hidrico | NOT_APPLICABLE | ADAPT | [clinical-forms.md §fluid-row-display-labels](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-042 | Fluid-balance record signature eligibility | balanco-hidrico | NOT_APPLICABLE | ADAPT | [security-lgpd.md §signature-eligibility-gating](architecture/security-lgpd.md) | — |
| RULE-BALANCO-HIDRICO-043 | Saida record sign posts to the "entrada" route (bug) | balanco-hidrico | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §fluid-record-sign-action](design/screens/clinical-forms.md) | P3 |
| RULE-BALANCO-HIDRICO-044 | Fluid-balance module navigation/state routes | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fluid-balance-navigation](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-045 | Fluid-balance record signing/deletion lifecycle | balanco-hidrico | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-17](RATIFICATION.md) | AMBIGUOUS |
| RULE-BALANCO-HIDRICO-046 | Fluid-balance PDF export with optional signatures | balanco-hidrico | NOT_APPLICABLE | ADAPT | [clinical-forms.md §pdf-export-with-signatures](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-047 | Entrada always marked checado on creation | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | — |
| RULE-BALANCO-HIDRICO-048 | Entrada/Saida quantidade fallback to zero before persist | balanco-hidrico | NOT_APPLICABLE | ADAPT | [hemodynamics.md §fluid-quantity-null-handling](clinical/domains/hemodynamics.md) | — |
| RULE-BALANCO-HIDRICO-049 | Entrada/Saida default display name from tipo | balanco-hidrico | NOT_APPLICABLE | ADAPT | [clinical-forms.md §fluid-record-default-name](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-050 | Explicit 'dia' parameter parsing/validation for balanco hidr | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | — |
| RULE-BALANCO-HIDRICO-051 | Entrada/Saida listing includes soft-deleted records | balanco-hidrico | NOT_APPLICABLE | ADAPT | [security-lgpd.md §soft-delete-exclusion-default](architecture/security-lgpd.md) | P3 |
| RULE-BALANCO-HIDRICO-052 | Vital-signs field set and units (sinais vitais) | balanco-hidrico | NOT_APPLICABLE | ADAPT | [clinical-forms.md §vital-signs-field-units](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-053 | Fluid intake/output field set and volume unit (entrada/saida | balanco-hidrico | NOT_APPLICABLE | ADAPT | [clinical-forms.md §fluid-io-field-units](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-054 | Empty-state for fluid-balance overview tab | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fluid-overview-empty-state](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-055 | IV hydration solution vocabulary | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §iv-hydration-solutions](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-056 | Drugs/hydration-in-BI vocabulary | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-18](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-057 | Antibiotic vocabulary (fluid balance) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-19](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-058 | Electrolyte replacement vocabulary | balanco-hidrico | UNVERIFIABLE | ADAPT | [clinical-forms.md §electrolyte-replacement-vocabulary](design/screens/clinical-forms.md) | P3 |
| RULE-BALANCO-HIDRICO-059 | Fluid-balance consciousness level enum (AVDI-like) | balanco-hidrico | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-balanco-hidrico-20](RATIFICATION.md) | UNVERIFIABLE |
| RULE-BALANCO-HIDRICO-060 | Fluid-balance complaint conditional | balanco-hidrico | NOT_APPLICABLE | ADOPT | [clinical-forms.md §complaint-conditional](design/screens/clinical-forms.md) | — |
| RULE-BALANCO-HIDRICO-061 | Required HH:MM 24h event-time (fluid balance) | balanco-hidrico | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §horario-required-validation](design/screens/clinical-forms.md) | P3 |
| RULE-BALANCO-HIDRICO-062 | Balanco hidrico day filter (unused) | balanco-hidrico | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-CADASTROS-UI-001 | FilterLeitos tri-state occupancy filter sent as literal stri | cadastros-ui | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-CADASTROS-UI-002 | Leito/Estabelecimento name and code locked for non-manual co | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §synced-record-field-lock](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-003 | Delete-professional action gated on edit mode + permission | cadastros-ui | NOT_APPLICABLE | ADAPT | [security-lgpd.md §rbac-delete-gating](architecture/security-lgpd.md) | — |
| RULE-CADASTROS-UI-004 | Camera credential fields gated on can_manage_camera permissi | cadastros-ui | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-gated-field-visibility](architecture/security-lgpd.md) | — |
| RULE-CADASTROS-UI-005 | New-user password auto-filled from CPF | cadastros-ui | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-cadastros-ui-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-CADASTROS-UI-006 | Hardcoded default signature PIN for all users | cadastros-ui | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-cadastros-ui-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-CADASTROS-UI-007 | Group-edit autosave guards partial "usuarios" updates | cadastros-ui | NOT_APPLICABLE | RETIRE | — | — |
| RULE-CADASTROS-UI-008 | Company "tipo" only settable at creation; hex color round-tr | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §empresa-tipo-immutable](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-009 | CPF input mask and unformatting | cadastros-ui | NOT_APPLICABLE | ADOPT | [clinical-forms.md §cpf-mask](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-010 | FormUsuario submit-value normalization | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §user-submit-normalization](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-011 | FormUsuario required fields only enforced in modal (creation | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §required-field-consistency](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-012 | Default required-field rule | cadastros-ui | NOT_APPLICABLE | ADOPT | [clinical-forms.md §required-field-message](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-013 | Email format validation | cadastros-ui | NOT_APPLICABLE | ADOPT | [clinical-forms.md §email-validation](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-014 | Patient sex/gender code labels | cadastros-ui | NOT_APPLICABLE | ADOPT | [clinical-forms.md §sexo-labels](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-015 | Brazilian federative-unit (UF) enumeration | cadastros-ui | NOT_APPLICABLE | ADOPT | [clinical-forms.md §uf-enum](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-016 | Brazilian document and number formatting masks | cadastros-ui | DISCREPANCY | ADOPT-CORRECTED | [clinical-forms.md §document-masks-corrected](design/screens/clinical-forms.md) | P3 |
| RULE-CADASTROS-UI-017 | Length-heuristic date/datetime formatting | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §date-formatting](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-018 | Date-field detection convention (data_ / dt_ key prefixes) | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §date-field-detection](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-019 | Image-file extension whitelist | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §image-extension-whitelist](design/screens/clinical-forms.md) | — |
| RULE-CADASTROS-UI-020 | Single image-or-PDF file constraint on avatar/logo uploader | cadastros-ui | NOT_APPLICABLE | ADAPT | [clinical-forms.md §file-upload-constraint](design/screens/clinical-forms.md) | — |
| RULE-CLINICAL-SCORING-001 | SOFA total score (sum of six organ sub-scores) | clinical-scoring | VERIFIED | ADOPT | [early-warning-scores.md §sofa-total-score](clinical/domains/early-warning-scores.md) | — |
| RULE-CLINICAL-SCORING-002 | SOFA respiratory sub-score (PaO2/FiO2) | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-01](RATIFICATION.md) | P0 |
| RULE-CLINICAL-SCORING-003 | SOFA coagulation sub-score (platelets) | clinical-scoring | VERIFIED | ADOPT | [early-warning-scores.md §sofa-coagulation-sub-score](clinical/domains/early-warning-scores.md) | — |
| RULE-CLINICAL-SCORING-004 | SOFA liver sub-score (bilirubin) | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-02](RATIFICATION.md) | P1 |
| RULE-CLINICAL-SCORING-005 | SOFA cardiovascular sub-score (vasopressors/MAP) | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-03](RATIFICATION.md) | P0 |
| RULE-CLINICAL-SCORING-006 | SOFA CNS sub-score (Glasgow) | clinical-scoring | VERIFIED | ADOPT | [early-warning-scores.md §sofa-cns-sub-score](clinical/domains/early-warning-scores.md) | — |
| RULE-CLINICAL-SCORING-007 | SOFA renal sub-score (creatinine/urine output) | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-04](RATIFICATION.md) | P0 |
| RULE-CLINICAL-SCORING-008 | PaO2/FiO2 ratio (relacao PO2/FiO2) | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-05](RATIFICATION.md) | P0 |
| RULE-CLINICAL-SCORING-009 | Mean arterial pressure (PAM) from PAS/PAD | clinical-scoring | VERIFIED | ADOPT | [hemodynamics.md §mean-arterial-pressure](clinical/domains/hemodynamics.md) | — |
| RULE-CLINICAL-SCORING-010 | Patient age from birthdate (integer days // 365) | clinical-scoring | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §patient-age-years](clinical/domains/neuro-sedation.md) | P2 |
| RULE-CLINICAL-SCORING-011 | SOFA attribute sourcing from prontuario (model.save) | clinical-scoring | VERIFIED | ADAPT | [early-warning-scores.md §sofa-input-sourcing](clinical/domains/early-warning-scores.md) | — |
| RULE-CLINICAL-SCORING-012 | SOFA score input assembly (first movimentacao) | clinical-scoring | VERIFIED | ADAPT | [early-warning-scores.md §sofa-input-assembly](clinical/domains/early-warning-scores.md) | — |
| RULE-CLINICAL-SCORING-013 | Glasgow Coma Scale valid range (3-15) | clinical-scoring | VERIFIED | ADOPT | [clinical-forms.md §gcs-range-3-15](design/screens/clinical-forms.md) | — |
| RULE-CLINICAL-SCORING-014 | RASS (Richmond Agitation-Sedation Scale) enumeration | clinical-scoring | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-clinical-scoring-06](RATIFICATION.md) | P2 |
| RULE-CLINICAL-SCORING-015 | Escala de Dor numerica - faixa valida (0-10) | clinical-scoring | VERIFIED | ADOPT | [clinical-forms.md §pain-nrs-0-10](design/screens/clinical-forms.md) | — |
| RULE-CLINICAL-SCORING-016 | Sinais de Dor (escala comportamental) - faixa valida (3-12) | clinical-scoring | VERIFIED | ADOPT | [clinical-forms.md §bps-behavioral-pain-3-12](design/screens/clinical-forms.md) | — |
| RULE-CLINICAL-SCORING-017 | SDRA (ARDS) severity enumeration | clinical-scoring | VERIFIED | ADAPT | [respiratory.md §ards-severity-enumeration](clinical/domains/respiratory.md) | P3 |
| RULE-CLINICAL-SCORING-018 | FOIS (Functional Oral Intake Scale) enumeration | clinical-scoring | VERIFIED | ADOPT | [clinical-forms.md §fois-7-level](design/screens/clinical-forms.md) | — |
| RULE-COMUNICACAO-001 | Reaction-count-by-emoji aggregation — SQL-correct vs order-d | comunicacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-COMUNICACAO-002 | Current user's own reaction id on an observation | comunicacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-COMUNICACAO-003 | AcaoHomecare balanco_hidrico method-reference bug | comunicacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-COMUNICACAO-004 | send_qtd_mensagens_to_firebase — per-user unread-message cou | comunicacao | NOT_APPLICABLE | SUPERSEDE | [product-spec.md §unread-counter-mechanism](product/product-spec.md) | — |
| RULE-COMUNICACAO-005 | reduzir_qtd (mensageiro) — eligibility to decrement an obser | comunicacao | NOT_APPLICABLE | ADAPT | [product-spec.md §unread-decrement-eligibility](product/product-spec.md) | — |
| RULE-COMUNICACAO-006 | Firebase unread-count decrement when an observation checagem | comunicacao | NOT_APPLICABLE | ADAPT | [product-spec.md §checagem-triggered-decrement](product/product-spec.md) | — |
| RULE-COMUNICACAO-007 | Firebase message-count notification suppressed for reply mes | comunicacao | NOT_APPLICABLE | ADAPT | [product-spec.md §reply-suppression-logic](product/product-spec.md) | — |
| RULE-COMUNICACAO-008 | Chat message retention window - 48h default, 96h when filter | comunicacao | NOT_APPLICABLE | ADAPT | [product-spec.md §chat-retention-window](product/product-spec.md) | — |
| RULE-COMUNICACAO-009 | Popup notification throttled to one per 2 seconds | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-010 | Notification alert color only applied for leito-type message | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-011 | Notification click-through decision tree | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-012 | Patient snapshot in observation branches by leito type | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-013 | Observation dual-mode movimentacao/leito resolution | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-014 | Protocol-checklist item toggle authorization | comunicacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §checklist-item-toggle-lock](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-015 | Chat reaction removal restricted to its own author | comunicacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §own-resource-deletion-guard](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-016 | Video-call join gated on detected video input device | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-017 | Notification fan-out to all sector users on creation | comunicacao | NOT_APPLICABLE | ADAPT | [alert-engine.md §staff-notification-fanout](architecture/alert-engine.md) | — |
| RULE-COMUNICACAO-018 | Record interaction indicator on first notification view | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-019 | Observation auto-creates a notification and routes by target | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-020 | Real-time notifications filter out the current user's own me | comunicacao | NOT_APPLICABLE | ADAPT | [product-spec.md §self-message-notification-filter](product/product-spec.md) | — |
| RULE-COMUNICACAO-021 | Chat message list pagination | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-022 | Auto-select first sector conversation | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-023 | Unread-message badge sourced from Firestore, reset on open | comunicacao | NOT_APPLICABLE | SUPERSEDE | [product-spec.md §unread-counter-mechanism](product/product-spec.md) | — |
| RULE-COMUNICACAO-024 | WebSocket-driven feed auto-refresh policy | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-025 | Feed pagination thresholds | comunicacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §activity-feed-pagination](design/screens/clinical-forms.md) | — |
| RULE-COMUNICACAO-026 | Hardcoded neutral-alert mock pathways in feed drawer | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-01](RATIFICATION.md) | P3 |
| RULE-COMUNICACAO-027 | Reaction hard-delete override | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-02](RATIFICATION.md) | — |
| RULE-COMUNICACAO-028 | Online-call roster filtered to users currently in call | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-029 | Video call auto-leaves on route change | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-030 | Single-join guard and forced reload after leaving a call | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-031 | Video-call room exit confirmation guard | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-032 | Real-time telemedicine dependency stack (Agora RTC + Firebas | comunicacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §realtime-telemedicine-stack](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-033 | checado_por_id always forced to the requesting user | comunicacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-derived-identity-fields](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-034 | Validacao de leito para acao de feed homecare | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-03](RATIFICATION.md) | P3 |
| RULE-COMUNICACAO-035 | Homecare feed action-type vocabulary — acaoDict render map v | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-04](RATIFICATION.md) | P3 |
| RULE-COMUNICACAO-036 | Chat/feed emoji-reaction enumeration | comunicacao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §reaction-emoji-enum](design/screens/clinical-forms.md) | — |
| RULE-COMUNICACAO-037 | One reaction per user per observation + unread-counter side  | comunicacao | NOT_APPLICABLE | ADAPT | [correlation-engine.md §reaction-counter-eligibility](clinical/domains/correlation-engine.md) | — |
| RULE-COMUNICACAO-038 | Reaction usuario/observacao always server-injected | comunicacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-derived-identity-fields](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-039 | Message scope enumeration | comunicacao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §message-scope-enum](design/screens/clinical-forms.md) | — |
| RULE-COMUNICACAO-040 | Conditional rendering of trilha-criteria checklist in send-o | comunicacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §trilha-criteria-checklist](design/screens/clinical-forms.md) | — |
| RULE-COMUNICACAO-041 | Observation setor_id is always forced from the URL | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-05](RATIFICATION.md) | AMBIGUOUS |
| RULE-COMUNICACAO-042 | Observation responsavel_id is always forced to the authentic | comunicacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-derived-identity-fields](architecture/security-lgpd.md) | — |
| RULE-COMUNICACAO-043 | Observation reply field rename | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-044 | Video-call online-presence flag derivation | comunicacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-COMUNICACAO-045 | FilePicker only reconciles local file list on removal | comunicacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-comunicacao-06](RATIFICATION.md) | AMBIGUOUS |
| RULE-COMUNICACAO-046 | Unread-counter decrement eligibility predicate (reduzir_qtd) | comunicacao | NOT_APPLICABLE | ADAPT | [correlation-engine.md §unread-counter-decrement-eligibility](clinical/domains/correlation-engine.md) | — |
| RULE-DOCUMENTACAO-FATURAMENTO-001 | Prescricao PDF display date formatting | documentacao-faturamento | VERIFIED | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-002 | Glosa-Zero automatic alert engine — 16-criteria billing/docu | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-003 | combinar_documentos — all-or-nothing PDF validation gate bef | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-004 | Signed vs unsigned balanco hidrico PDF template selection | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-005 | PDF report dt_entrada lookup (admission date) | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-006 | Prescricao PDF export - priority ordering and soft-delete ex | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-007 | Cryptocubo __get_formato_assinatura — signature-format mappi | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-008 | Cryptocubo PIN/ALIAS fallback — inconsistent 'or'-fallback s | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-009 | Cryptocubo __check_response_status — non-200 response audit  | documentacao-faturamento | NOT_APPLICABLE | ADAPT | [security-lgpd.md §integration-failure-audit-logging](architecture/security-lgpd.md) | — |
| RULE-DOCUMENTACAO-FATURAMENTO-010 | Digital-signature eligibility - user must have CPF and PIN | documentacao-faturamento | NOT_APPLICABLE | ADAPT | [security-lgpd.md §credential-completeness-gating](architecture/security-lgpd.md) | — |
| RULE-DOCUMENTACAO-FATURAMENTO-011 | Bulk-download button requires a non-empty selection | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-012 | Leito file-send requires image(s) or a PDF plus category/obs | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-013 | Leito upload tab gated on can_upload_files_amhdocs permissio | documentacao-faturamento | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-gated-ui](architecture/security-lgpd.md) | — |
| RULE-DOCUMENTACAO-FATURAMENTO-014 | Double-gated evolution report access | documentacao-faturamento | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-documentacao-faturamento-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-DOCUMENTACAO-FATURAMENTO-015 | Auto-post released evolution to Tasy (lancamento code 501) | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-DOCUMENTACAO-FATURAMENTO-016 | "Agrupar PDFs e baixar" workflow response-validation chain | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-017 | Leito arquivos list default sort order | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-DOCUMENTACAO-FATURAMENTO-018 | PDF report filename pattern | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-019 | Evolution-note count-by-type with Total row | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-020 | Uploaded medical-record/document category code catalog — thr | documentacao-faturamento | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §document-category-codes](design/screens/clinical-forms.md) | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-021 | PDF export base64 flag uses raw truthy string check | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-022 | Prescricao PDF export has no explicit validation for missing | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-023 | Prescricao PDF export - unguarded first() access for dt_entr | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-DOCUMENTACAO-FATURAMENTO-024 | Prescription/CPOE signature-inconsistency record | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-DOCUMENTACAO-FATURAMENTO-025 | Report filter date-prefix formatting convention | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-026 | PDF upload MIME-type validation | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-027 | AMHDocs external file lookup keyed by bed's nr_atendimento | documentacao-faturamento | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-documentacao-faturamento-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-DOCUMENTACAO-FATURAMENTO-028 | AMHDocs pagination links rewritten to proxy's own URL | documentacao-faturamento | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-documentacao-faturamento-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-DOCUMENTACAO-FATURAMENTO-029 | PDF grouping (agrupar-pdf) requires a non-empty array of ids | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-030 | PDF grouping response status-code decision tree | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-031 | Arquivo filter end-date must not precede start date | documentacao-faturamento | NOT_APPLICABLE | RETIRE | — | — |
| RULE-DOCUMENTACAO-FATURAMENTO-032 | Default electronic-signature configuration for CryptoCubo do | documentacao-faturamento | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-documentacao-faturamento-add-01](RATIFICATION.md) | ADDENDUM |
| RULE-EFICIENCIA-001 | Eficiencia v3 alert aggregation (calcular_alerta_v2, wired) | eficiencia | NOT_APPLICABLE | ADAPT | [early-warning-scores.md §eficiencia-alert-aggregation](clinical/domains/early-warning-scores.md) | — |
| RULE-EFICIENCIA-002 | Eficiencia v3 criterio_3 - unjustified RBC transfusion at Hb | eficiencia | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-eficiencia-01](RATIFICATION.md) | P1 |
| RULE-EFICIENCIA-003 | Eficiencia v3 criterio_4 - RBC transfusion at Hb 6-7, 2 unit | eficiencia | DISCREPANCY | ADOPT-CORRECTED | [hemodynamics.md §rbc-transfusion-6-7-2unit](clinical/domains/hemodynamics.md) | P2 |
| RULE-EFICIENCIA-004 | Eficiencia v3 criterio_5 - platelet transfusion at Plt>25000 | eficiencia | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-eficiencia-02](RATIFICATION.md) | P1 |
| RULE-EFICIENCIA-005 | Eficiencia v3 criterio_9 - coma without sedation (defined, u | eficiencia | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-eficiencia-03](RATIFICATION.md) | P0 |
| RULE-EFICIENCIA-006 | Eficiencia v3 criterio_10 - mechanical restraint without agi | eficiencia | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-eficiencia-04](RATIFICATION.md) | P1 |
| RULE-EFICIENCIA-007 | Eficiencia v3 criterio_1 - repeated exams within minimum-rep | eficiencia | NOT_APPLICABLE | ADAPT | [correlation-engine.md §redundant-exam-ordering](clinical/domains/correlation-engine.md) | — |
| RULE-EFICIENCIA-008 | Eficiencia v3 criterio_2 - ICU discharge readiness (defined, | eficiencia | DISCREPANCY | ADAPT | [early-warning-scores.md §icu-discharge-readiness](clinical/domains/early-warning-scores.md) | P3 |
| RULE-EFICIENCIA-009 | Eficiencia v3 criterio_6 - frailty / palliative-appropriaten | eficiencia | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-eficiencia-05](RATIFICATION.md) | UNVERIFIABLE |
| RULE-EFICIENCIA-010 | Eficiencia v3 criterio_7 - delirium/agitation risk bundle (d | eficiencia | DISCREPANCY | ADAPT | [neuro-sedation.md §delirium-risk-bundle](clinical/domains/neuro-sedation.md) | P3 |
| RULE-EFICIENCIA-011 | Eficiencia v3 criterio_8 - low-support step-down readiness ( | eficiencia | DISCREPANCY | ADAPT | [respiratory.md §step-down-readiness](clinical/domains/respiratory.md) | P3 |
| RULE-EFICIENCIA-012 | Eficiencia active alert-text payload catalog (get_payload_tr | eficiencia | VERIFIED | ADOPT | [hemodynamics.md §transfusion-thresholds](clinical/domains/hemodynamics.md) | — |
| RULE-EQUILIBRIO-001 | Fluid balance - positive fluid balance and maintenance-fluid | equilibrio | NOT_APPLICABLE | ADAPT | [aki.md §fluid-balance-titration](clinical/domains/aki.md) | — |
| RULE-EQUILIBRIO-002 | Renal-function drug substitution, morphine avoidance, and hy | equilibrio | VERIFIED | ADAPT | [electrolyte.md §hypernatremia-na160-correction](clinical/domains/electrolyte.md) | — |
| RULE-EQUILIBRIO-003 | Equilibrio trilha alert-color aggregation (v1, TrilhaEquilib | equilibrio | NOT_APPLICABLE | SUPERSEDE | [aki.md §alert-severity-mapping](clinical/domains/aki.md) | — |
| RULE-EQUILIBRIO-004 | Severe hyperkalemia (K>6) rescue protocol with 4h reassessme | equilibrio | DISCREPANCY | ADOPT-CORRECTED | [electrolyte.md §hyperkalemia-rescue-protocol](clinical/domains/electrolyte.md) | P2 |
| RULE-ESTABILIDADE-001 | Estabilidade v3 criterio_5 - vasopressor with negative cumul | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-01](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-002 | Estabilidade v3 criterio_6 - shock index with beta-blocker/v | estabilidade | VERIFIED | ADAPT | [early-warning-scores.md §shock-index-vasopressor-absence](clinical/domains/early-warning-scores.md) | — |
| RULE-ESTABILIDADE-003 | Estabilidade v3 criterio_1 - hypoperfusion on vasopressor | estabilidade | VERIFIED | ADAPT | [sepsis.md §hypoperfusion-on-vasopressor](clinical/domains/sepsis.md) | — |
| RULE-ESTABILIDADE-004 | Estabilidade v3 criterio_2 - new vasopressor missing sepsis  | estabilidade | VERIFIED | ADAPT | [sepsis.md §new-vasopressor-missing-workup](clinical/domains/sepsis.md) | — |
| RULE-ESTABILIDADE-005 | Estabilidade v3 criterio_3 - lactate elevation with sepsis t | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-02](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-006 | Estabilidade v3 criterio_4 - persistent shock on low-dose va | estabilidade | VERIFIED | ADAPT | [sepsis.md §persistent-shock-spontaneous-ventilation](clinical/domains/sepsis.md) | — |
| RULE-ESTABILIDADE-007 | Estabilidade v3 criterio_7 - high-dose noradrenaline without | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-03](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-008 | Estabilidade v3 criterio_8 - refractory shock triple therapy | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-04](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-009 | Estabilidade v3 criterio_9 - dobutamine with high-dose norad | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-05](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-010 | Estabilidade v3 criterio_10 - antihypertensive with active v | estabilidade | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-estabilidade-06](RATIFICATION.md) | UNVERIFIABLE |
| RULE-ESTABILIDADE-011 | Estabilidade v3 criterio_11 - bicarbonate despite compensate | estabilidade | DISCREPANCY | ADOPT-CORRECTED | [electrolyte.md §bicarbonate-stewardship-sepsis](clinical/domains/electrolyte.md) | P2 |
| RULE-ESTABILIDADE-012 | Estabilidade v3 criterio_12 - antihypertensive with recurren | estabilidade | NOT_APPLICABLE | ADAPT | [hemodynamics.md §recurrent-hypotension-antihypertensive-conflict](clinical/domains/hemodynamics.md) | P3 |
| RULE-ESTABILIDADE-013 | Estabilidade v3 criterio_13 - recurrent hypertension off vas | estabilidade | NOT_APPLICABLE | ADAPT | [hemodynamics.md §recurrent-hypertension-off-vasopressor](clinical/domains/hemodynamics.md) | P3 |
| RULE-ESTABILIDADE-014 | Estabilidade v3 alert level (calcular_alerta == calcular_ale | estabilidade | NOT_APPLICABLE | ADOPT | [hemodynamics.md §shock-alert-tiering](clinical/domains/hemodynamics.md) | — |
| RULE-ESTABILIDADE-015 | Estabilidade facade alert-text - perfusion/shock triggers &  | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-07](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-016 | Estabilidade facade alert-text - vasopressor/inotrope escala | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-08](RATIFICATION.md) | P0 |
| RULE-ESTABILIDADE-017 | Estabilidade manual C1 - slow capillary refill on noradrenal | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-09](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-018 | Estabilidade manual C2 - noradrenaline started in last 24h | estabilidade | NOT_APPLICABLE | ADOPT | [hemodynamics.md §vasopressor-initiation-window](clinical/domains/hemodynamics.md) | — |
| RULE-ESTABILIDADE-019 | Estabilidade manual C3 - high noradrenaline without rescue t | estabilidade | DISCREPANCY | ADOPT-CORRECTED | [hemodynamics.md §high-dose-noradrenaline-without-adjuncts](clinical/domains/hemodynamics.md) | P2 |
| RULE-ESTABILIDADE-020 | Estabilidade manual C4 - elevated arterial lactate | estabilidade | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §hyperlactatemia-threshold](clinical/domains/sepsis.md) | P2 |
| RULE-ESTABILIDADE-021 | Estabilidade manual C5 - antihypertensive with adequate pres | estabilidade | NOT_APPLICABLE | ADOPT | [hemodynamics.md §antihypertensive-adequate-pressure-conflict](clinical/domains/hemodynamics.md) | — |
| RULE-ESTABILIDADE-022 | Estabilidade manual C6 - dobutamine with exact noradrenaline | estabilidade | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-estabilidade-10](RATIFICATION.md) | UNVERIFIABLE |
| RULE-ESTABILIDADE-023 | Estabilidade manual pathway alert level | estabilidade | NOT_APPLICABLE | ADAPT | [hemodynamics.md §manual-pathway-alert-tiering](clinical/domains/hemodynamics.md) | — |
| RULE-ESTABILIDADE-024 | Estabilizacao (trilha2) - shock work-up & vasopressor escala | estabilidade | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-estabilidade-11](RATIFICATION.md) | P1 |
| RULE-ESTABILIDADE-025 | Estabilizacao v1 alert with criterio_6 combination clause | estabilidade | NOT_APPLICABLE | RETIRE | — | — |
| RULE-ESTABILIDADE-026 | Auto start-time default (now) for noradrenaline & cardiac ar | estabilidade | NOT_APPLICABLE | ADOPT | [hemodynamics.md §vasopressor-start-time-default](clinical/domains/hemodynamics.md) | — |
| RULE-EVOLUCOES-001 | Medical-record clinical parameter panel with pre-computed SO | evolucoes | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-EVOLUCOES-002 | SOFA score display threshold | evolucoes | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-EVOLUCOES-003 | RASS field type mismatch across models | evolucoes | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §rass-scale](clinical/domains/neuro-sedation.md) | P2 |
| RULE-EVOLUCOES-004 | Cardiac-arrest occurrence tracking shape | evolucoes | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-EVOLUCOES-005 | Company evolutions - patient name resolved by attendance num | evolucoes | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-EVOLUCOES-006 | Leito resolution precedence for form endpoints | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-007 | Form visibility rule - own draft or released | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §draft-document-visibility](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-008 | Signed PDF takes precedence over draft PDF | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §signed-document-precedence](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-009 | Evolution release (liberar) gated by registered evolution ty | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-010 | Registered evolution types eligible for Tasy release, and th | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-011 | Evolution release eligibility composite check (can_liberar) | evolucoes | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-EVOLUCOES-012 | AMH Docs category-code mapping per evolution type | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-013 | Conditional PDF rendering of assessment sections based on fi | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §conditional-section-rendering](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-014 | Medical evolution displays most recent vital signs at/before | evolucoes | NOT_APPLICABLE | ADOPT | [correlation-engine.md §vitals-snapshot-linkage](clinical/domains/correlation-engine.md) | — |
| RULE-EVOLUCOES-015 | Nutritionist PDF displays pressure-injury (LPP) records from | evolucoes | NOT_APPLICABLE | ADOPT | [correlation-engine.md §lpp-cross-form-lookup](clinical/domains/correlation-engine.md) | — |
| RULE-EVOLUCOES-016 | get_base_evolucao_context — admission date included only if  | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-017 | Medico form bundles vital-signs creation tied to daily balan | evolucoes | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-05](RATIFICATION.md) | AMBIGUOUS |
| RULE-EVOLUCOES-018 | Company-wide evolutions queryset filter with possible instan | evolucoes | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-EVOLUCOES-019 | Author-only edit / inactivate / re-sign eligibility | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §author-only-edit-eligibility](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-020 | Evolução drawer OK-button gating | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-021 | Conditional sub-fields driven by selected option (conditions | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §conditional-fields](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-022 | Single-checkbox conditions key mismatch | evolucoes | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-EVOLUCOES-023 | Dynamic clinical-form field-type vocabulary (declared union  | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §field-type-vocabulary](design/screens/clinical-forms.md) | P3 |
| RULE-EVOLUCOES-024 | criar_sepse_evolucao / get_ultimos_sinais_vitais — sepsis no | evolucoes | NOT_APPLICABLE | ADOPT | [sepsis.md §vitals-auto-link](clinical/domains/sepsis.md) | — |
| RULE-EVOLUCOES-025 | Evolution signing workflow and signature-date assignment | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §signature-timestamp-integrity](architecture/security-lgpd.md) | P3 |
| RULE-EVOLUCOES-026 | Auto sign-and-release on create when status is "liberado" | evolucoes | NOT_APPLICABLE | ADAPT | [security-lgpd.md §auto-sign-on-release](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-027 | Auto sign-and-release on update when status is "liberado", g | evolucoes | NOT_APPLICABLE | ADAPT | [security-lgpd.md §auto-sign-on-release](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-028 | Form manage_data - required identifiers and content wrapping | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-029 | anterior_indicadores aggregation (previous form/vitals/24h i | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §previous-form-visibility-parity](architecture/security-lgpd.md) | P3 |
| RULE-EVOLUCOES-030 | Form destroy() does not call validar_inativacao (dead valida | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §inactivation-guard](architecture/security-lgpd.md) | P3 |
| RULE-EVOLUCOES-031 | Medico form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §medico-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-032 | Enfermagem form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §enfermagem-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-033 | Tecnico de enfermagem form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §tecnico-enfermagem-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-034 | Fisioterapeuta form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fisioterapeuta-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-035 | Farmaceutico clinico form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §farmaceutico-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-036 | Fonoaudiologo form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §fonoaudiologo-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-037 | Musicoterapeuta form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §musicoterapeuta-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-038 | Nutricionista form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nutricionista-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-039 | Psicologo form content composition | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §psicologo-form-sections](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-040 | Terapeuta form content composition | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §terapeuta-form-content](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-041 | Intercorrencia form content composition | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §intercorrencia-form-content](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-042 | Evolution/progress-note lifecycle status | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §evolution-lifecycle-tristate](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-043 | Evolution status state machine (salvo / liberado / inativo) | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §lifecycle-status-indicators](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-044 | Liberar/assinar sets status=liberado and assinar=true | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §liberar-assinar-workflow](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-045 | Evolução save-vs-save-and-release workflow | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §save-vs-save-and-release](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-046 | New evolution prefilled from last form; dt_registro defaults | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §prefill-from-last-form](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-047 | Previous-form-indicators carry-forward endpoint | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §anterior-indicadores-endpoint](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-048 | Dual query-parameter encoding on evolution-report fetch | evolucoes | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-EVOLUCOES-049 | Annullable (anulavel) group nullification on submit | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §annulment-nullify-on-submit](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-050 | Checkable (checavel) subgroup toggle and null-on-disable | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §checkable-subgroup-toggle](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-051 | Cannot update an inactive evolution | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §no-update-inactive-record](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-052 | Only the original author can edit an evolution | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §author-only-edit](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-053 | CPF required to release an evolution | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §cpf-required-to-release](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-054 | CPF and PIN required to sign an evolution | evolucoes | NOT_APPLICABLE | ADOPT | [security-lgpd.md §cpf-pin-required-to-sign](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-055 | Cannot inactivate a released (liberado) form - validation ru | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §cannot-inactivate-released-enforced](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-056 | Nutritionist evolution mandates global, nutritional-therapy, | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nutricionista-required-assessments](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-057 | dispositivos_invasivos_novo declared but excluded from Meta. | evolucoes | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-EVOLUCOES-058 | atualizar_campos_evolucao — required 'id' field per sub-form | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §subform-update-requires-id](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-059 | Registration datetime immutable when editing a past evolutio | evolucoes | NOT_APPLICABLE | ADAPT | [security-lgpd.md §dt-registro-immutability](architecture/security-lgpd.md) | — |
| RULE-EVOLUCOES-060 | Nutritional-assessment numeric coercion on load | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-061 | Ventilation/device date-field adapters for nursing forms | evolucoes | NOT_APPLICABLE | RETIRE | — | — |
| RULE-EVOLUCOES-062 | Pharmacist evolution-form key naming/type inconsistency | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §professional-role-enum](design/screens/clinical-forms.md) | P3 |
| RULE-EVOLUCOES-063 | Strip ids when creating a new evolucao | evolucoes | NOT_APPLICABLE | ADAPT | [clinical-forms.md §new-record-id-stripping](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-064 | Field read-only (disableAll) conditions | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §field-disable-semantics](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-065 | String field disable condition (nullifier lookup) | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §field-disable-semantics](design/screens/clinical-forms.md) | P3 |
| RULE-EVOLUCOES-066 | Numeric field inclusive min/max range validation | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §numeric-field-bounds](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-067 | Interval field slider bounds | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §interval-field-bounds](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-068 | Multicheck selection-count min/max | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §multicheck-bounds](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-069 | Masked field regex pattern validation | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §masked-field-validation](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-070 | Repeatable list maximum item cap | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §repeatable-list-cap](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-071 | Required-if validation for text/date/extra fields | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §required-if-validation](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-072 | Dynamic-form field-level validation constraints | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §campo-engine-schema](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-073 | Dynamic-form conditional field visibility | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §conditional-field-visibility](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-074 | Form-group annulment (soft-void) mechanic | evolucoes | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-evolucoes-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-EVOLUCOES-075 | Encounter-number field name/type mismatch across models | evolucoes | NOT_APPLICABLE | ADOPT-CORRECTED | [data-model.md §encounter-identifier-canonical](architecture/data-model.md) | P3 |
| RULE-EVOLUCOES-076 | Gender code enumeration | evolucoes | NOT_APPLICABLE | ADOPT | [clinical-forms.md §gender-enum](design/screens/clinical-forms.md) | — |
| RULE-EVOLUCOES-077 | Relatório de Evolução filter requires professional + valid d | evolucoes | NOT_APPLICABLE | ADOPT | [command-center.md §relatorio-evolucao-filter](design/screens/command-center.md) | — |
| RULE-FORMULARIOS-CLINICOS-001 | Pressure-injury (LPP) NPUAP staging enum | formularios-clinicos | VERIFIED | ADOPT | [clinical-forms.md §lpp-staging-enum](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-002 | Pressure-injury (LPP) staging + wound-bed composite assessme | formularios-clinicos | DISCREPANCY | ADOPT-CORRECTED | [clinical-forms.md §peri-wound-edema-exudate-enum](design/screens/clinical-forms.md) | P2 |
| RULE-FORMULARIOS-CLINICOS-003 | Nursing-technician (TecEnfermagem) tegumentary LPP list vari | formularios-clinicos | DISCREPANCY | ADOPT-CORRECTED | [clinical-forms.md §peri-wound-edema-exudate-enum](design/screens/clinical-forms.md) | P2 |
| RULE-FORMULARIOS-CLINICOS-004 | Peri-wound edema classification - 4 cm threshold enum (backe | formularios-clinicos | DISCREPANCY | ADOPT-CORRECTED | [clinical-forms.md §peri-wound-edema-exudate-enum](design/screens/clinical-forms.md) | P2 |
| RULE-FORMULARIOS-CLINICOS-005 | Nursing cardiovascular assessment enums with capillary-refil | formularios-clinicos | DISCREPANCY | ADOPT-CORRECTED | [hemodynamics.md §capillary-refill-time](clinical/domains/hemodynamics.md) | P2 |
| RULE-FORMULARIOS-CLINICOS-006 | Nursing-technician diet block ranges (subset) | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §tecenfermagem-diet-block](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-007 | Home-care incident triage - urgency grade and symptom classi | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §intercorrencia-triage-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-008 | Physiotherapy early-mobilization eligibility flags | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §physio-mobilization-eligibility](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-009 | Home-care incident intervention/conduct with conditional spe | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §intercorrencia-intervention-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-010 | Physician physical-exam enums and conditional reveals | formularios-clinicos | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §physician-exam-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-011 | Nursing global assessment enums and risk conditionals | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-global-assessment-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-012 | Nursing-technician respiratory assessment with aspiration co | formularios-clinicos | NOT_APPLICABLE | ADAPT | [clinical-forms.md §numeric-field-bounds-o2-flow](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-013 | Nursing-technician genitourinary with diaper-change conditio | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §genitourinary-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-014 | Nursing-technician high-cost drug/antibiotic list and other  | formularios-clinicos | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-formularios-clinicos-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-FORMULARIOS-CLINICOS-015 | Home-care incident disposition/outcome enum | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §intercorrencia-disposition-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-016 | Physiotherapy conduct enums (respiratory & motor techniques) | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §physio-conduct-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-017 | Intercorrencia (clinical incident/complication) domain-conce | formularios-clinicos | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-FORMULARIOS-CLINICOS-018 | Pressure-injury (LPP) origin classification enum (tipo_lpp,  | formularios-clinicos | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §lpp-origin-required-field](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-019 | Other-lesion (non-pressure) assessment list | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §other-lesion-assessment-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-020 | Anatomical lesion / catheter-insertion site enumeration | formularios-clinicos | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §anatomical-site-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-021 | Home-care chronic-diagnosis catalog (backend humanize map +  | formularios-clinicos | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §chronic-diagnosis-catalog](design/screens/clinical-forms.md) | P3 |
| RULE-FORMULARIOS-CLINICOS-022 | Vascular-access / dressing tracked-field enum | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §device-dressing-field-catalog](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-023 | Physician in-use invasive devices vocabulary | formularios-clinicos | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §physician-invasive-devices-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-024 | Physician in-use equipment vocabulary | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §physician-equipment-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-025 | Speech-therapy global assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §speech-therapy-global-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-026 | Speech-therapy orofacial and language enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §speech-therapy-orofacial-language](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-027 | Music-therapy global assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §music-therapy-global-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-028 | Intramusical-relations assessment enum | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §music-therapy-intramusical-relations](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-029 | Nursing abdominal assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-abdominal-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-030 | Nursing genitourinary assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-genitourinary-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-031 | Nursing neurological assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-neurological-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-032 | Physiotherapy neuro/cardio/respiratory assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §physiotherapy-neuro-cardio-respiratory-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-033 | Physiotherapy motor-function enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §physiotherapy-motor-function-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-034 | Psychology global assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §psychology-global-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-035 | Psychological-assessment enums | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §psychological-assessment-enums](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-036 | Nursing-technician global assessment with locomotion | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-technician-global-assessment](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-037 | Multidisciplinary care-team discipline icon taxonomy | formularios-clinicos | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-formularios-clinicos-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-FORMULARIOS-CLINICOS-038 | Terapeuta icon is a byte-identical duplicate of Psicologo ic | formularios-clinicos | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-FORMULARIOS-CLINICOS-039 | Binary gender iconography (Masculino/Feminino) | formularios-clinicos | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-formularios-clinicos-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-FORMULARIOS-CLINICOS-040 | Duplicate route registration for enfermagem form | formularios-clinicos | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-FORMULARIOS-CLINICOS-041 | Optional HH:MM 24h exit-time mask | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §optional-time-field-mask](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-042 | Vasopressor / inotrope / sedative dosing capture (movimentac | formularios-clinicos | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-formularios-clinicos-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-FORMULARIOS-CLINICOS-043 | Invasive-device dressing and exchange scheduling | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §invasive-device-dressing-schedule](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-044 | Pharmacist evolution neurological and cardiological assessme | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §pharmacist-neuro-cardio-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-FORMULARIOS-CLINICOS-045 | Nursing-technician evolution neurological assessment vocabul | formularios-clinicos | NOT_APPLICABLE | ADOPT | [clinical-forms.md §nursing-technician-neuro-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-001 | Sector alert-share percentage formula | indicadores-etl | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-indicadores-etl-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-INDICADORES-ETL-002 | Sector assisted-share percentage formula | indicadores-etl | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-indicadores-etl-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-INDICADORES-ETL-003 | TLP (standardized letality) percentage conversion | indicadores-etl | VERIFIED | ADOPT | [correlation-engine.md §tlp-standardized-mortality-ratio](clinical/domains/correlation-engine.md) | — |
| RULE-INDICADORES-ETL-004 | Sedation-use indicator representation (assistenciais vs cont | indicadores-etl | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-indicadores-etl-03](RATIFICATION.md) | P1 |
| RULE-INDICADORES-ETL-005 | Bed-occupancy percentage color thresholds | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-006 | Sector-level aggregate alert-color decision tree | indicadores-etl | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §alert-severity-rollup](clinical/domains/correlation-engine.md) | — |
| RULE-INDICADORES-ETL-007 | Dashboard alert-count 4th severity level inconsistent with 3 | indicadores-etl | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §alert-severity-enum](clinical/domains/correlation-engine.md) | P3 |
| RULE-INDICADORES-ETL-008 | Per-sector dashboard shortcut visibility by empresa type | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-009 | Unread-message badge display and cap | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-010 | Sector dashboard dual y-axis toggle | indicadores-etl | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-indicadores-etl-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-INDICADORES-ETL-011 | get_procedimentos_invasivos — invasive-procedure code lookup | indicadores-etl | NOT_APPLICABLE | ADOPT | [clinical-forms.md §invasive-procedures-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-012 | get_microindicadores — ICU micro-indicator boolean mapping,  | indicadores-etl | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-indicadores-etl-05](RATIFICATION.md) | P1 |
| RULE-INDICADORES-ETL-013 | Incremental (watermark) load of occupancy indicators | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-014 | Macro indicators loaded for current month only | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-015 | etl_schema (v1) — Tasy-to-Trilha sync with assistido reset | indicadores-etl | NOT_APPLICABLE | RETIRE | — | — |
| RULE-INDICADORES-ETL-016 | novo_etl_schema (v2) — Tasy-to-Trilha sync, criterio-modifie | indicadores-etl | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-INDICADORES-ETL-017 | Sector occupancy dashboard auto-reload interval | indicadores-etl | NOT_APPLICABLE | SUPERSEDE | [api-design.md §replaces-occupancy-polling](architecture/api/api-design.md) | — |
| RULE-INDICADORES-ETL-018 | Hierarchical recursive KPI rollup | indicadores-etl | NOT_APPLICABLE | ADAPT | [correlation-engine.md §hierarchical-kpi-rollup](clinical/domains/correlation-engine.md) | — |
| RULE-INDICADORES-ETL-019 | Assistencial-indicators endpoint URL template bug | indicadores-etl | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-INDICADORES-ETL-020 | Generic indicator create always stamps server-side usuario_i | indicadores-etl | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-side-audit-stamping](architecture/security-lgpd.md) | — |
| RULE-INDICADORES-ETL-021 | Video-call entry indicator has a fixed tipo and unvalidated  | indicadores-etl | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-scoped-authorization](architecture/security-lgpd.md) | — |
| RULE-INDICADORES-ETL-022 | Macro-indicator tile display filter | indicadores-etl | NOT_APPLICABLE | ADAPT | [clinical-forms.md §zero-value-display](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-023 | Macro-indicator KPI shape | indicadores-etl | NOT_APPLICABLE | ADOPT | [correlation-engine.md §macro-indicator-kpis](clinical/domains/correlation-engine.md) | — |
| RULE-INDICADORES-ETL-024 | Clinical indicator null-vs-truthy display rule (Informações  | indicadores-etl | NOT_APPLICABLE | ADAPT | [clinical-forms.md §null-vs-zero-display](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-025 | 24h indicator numeric-type display filter | indicadores-etl | NOT_APPLICABLE | ADOPT | [clinical-forms.md §24h-indicator-display](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-026 | Micro-indicadores icon/value display rule | indicadores-etl | NOT_APPLICABLE | ADOPT | [clinical-forms.md §micro-indicator-icons](design/screens/clinical-forms.md) | — |
| RULE-INDICADORES-ETL-027 | Indicador tipo enumeration and type-specific payload validat | indicadores-etl | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §indicador-tipo-payload-schema](design/screens/clinical-forms.md) | P3 |
| RULE-MOVIMENTACAO-ADT-001 | Length-of-stay (tempo de permanencia / dias de internacao) | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-002 | Bed/movimentacao micro-indicators payload (VM / noradrenalin | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-003 | Expected-mortality score (mortalidade_esperada) surfaced wit | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-004 | Bed-level assistencial information clinical panel (vitals /  | movimentacao-adt | VERIFIED | ADOPT | [early-warning-scores.md §assistencial-panel-vitals-neuro-labs](clinical/domains/early-warning-scores.md) | — |
| RULE-MOVIMENTACAO-ADT-005 | Bed micro-indicator lookup key: nr_atendimento + bed name as | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-006 | Bed patient snapshot defaults to empty dict when unassigned | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-05](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-007 | Patient basic name/age computed fields | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-06](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-008 | Precomputed vinculo lookup dict is built but never consumed  | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-009 | Fixed -3h display offset for prontuario timestamps | movimentacao-adt | DISCREPANCY | ADAPT | [clinical-forms.md §timestamp-localization](design/screens/clinical-forms.md) | P2 |
| RULE-MOVIMENTACAO-ADT-010 | Live camera RTSP URL construction | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-08](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-011 | Bed 'assistido' flag delegated to a model property (leito se | movimentacao-adt | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-movimentacao-adt-09](RATIFICATION.md) | UNVERIFIABLE |
| RULE-MOVIMENTACAO-ADT-012 | Bed/movimentacao alert aggregation + new-alert notification | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §bed-alert-aggregation](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-013 | Patient 'assisted' resolution across pathways (movimentacao) | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §patient-assisted-resolution](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-014 | Bed/trilha alert severity levels (AMARELO∣NEUTRO∣VERMELHO) | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §alerta-enum-amarelo-neutro-vermelho](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-015 | Overdue-protocol-item indicator on trilha chip | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §overdue-protocol-indicator](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-016 | Invasive-procedures alert indicator | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §invasive-procedures-indicator](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-017 | Trilha (care-pathway) click routing | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-018 | Bed trilhas selection branches by tipo (automatica/homecare  | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §trilha-dispatch-by-bed-type](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-019 | Bed queryset hierarchical scope resolution (setor > empresa  | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-020 | Bed patient resolution and auto-creation | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-021 | Homecare vs automatica bed classification and tenant routing | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-022 | Bed destroy() blocked while it has an active occupation | movimentacao-adt | NOT_APPLICABLE | ADAPT | [security-lgpd.md §referential-integrity-guards](architecture/security-lgpd.md) | — |
| RULE-MOVIMENTACAO-ADT-023 | Bed action-button eligibility by bed type and permission | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-024 | Homecare occupancy access filtering | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-025 | Bed eligibility for manual movimentacao (admission) | movimentacao-adt | NOT_APPLICABLE | ADAPT | [clinical-forms.md §admission-eligibility-guard](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-026 | Bed (leito) default type is manual | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §leito-tipo-enum](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-027 | Bed action_fields expose has_camera only on retrieve | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-028 | Camera-enabled bed list requires a non-empty configured IP | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-029 | Movimentacao queryset optionally scoped by setor, ordered by | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-030 | Sector patient list restricted to currently-occupied beds | movimentacao-adt | NOT_APPLICABLE | ADAPT | [clinical-forms.md §active-patient-list-scoping](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-031 | Discharge (baixa) - only the current movimentacao can be clo | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §admission-discharge-lifecycle](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-032 | First movimentacao - admission occupies the bed | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §admission-discharge-lifecycle](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-033 | First admission (Primeira Movimentacao) viewset - forced fie | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-034 | New movimentacao - carry-forward of clinical data from previ | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §admission-discharge-lifecycle](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-035 | New movimentacao viewset carries forward patient and bed fro | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-036 | Homecare bed 'trilhas' list is a static fixed template, not  | movimentacao-adt | NOT_APPLICABLE | ADOPT-CORRECTED | [correlation-engine.md §homecare-trilhas](clinical/domains/correlation-engine.md) | P3 |
| RULE-MOVIMENTACAO-ADT-037 | Automatic-pathway bed trilhas only populate when the bed is  | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §trilha-aggregation](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-038 | Trilha recompute orchestration on prontuario data update | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §recompute-on-update](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-039 | Prontuario lookback chain (buscar_ultimos_dados) | movimentacao-adt | NOT_APPLICABLE | ADAPT | [sepsis.md §historical-lookback-window](clinical/domains/sepsis.md) | — |
| RULE-MOVIMENTACAO-ADT-040 | Batch recompute of current movimentacoes' trilhas (Celery ta | movimentacao-adt | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §recompute-scheduling](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-041 | Patient creation wrapper (CadastrarPaciente) | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-042 | Patient-user-sector link diff-sync (vinculo bulk action) | movimentacao-adt | NOT_APPLICABLE | ADAPT | [security-lgpd.md §patient-assignment-sync](architecture/security-lgpd.md) | — |
| RULE-MOVIMENTACAO-ADT-043 | SetorPacienteVinculoViewSet forces all link fields from the  | movimentacao-adt | NOT_APPLICABLE | ADAPT | [security-lgpd.md §url-trusted-identity-fields](architecture/security-lgpd.md) | — |
| RULE-MOVIMENTACAO-ADT-044 | Default active sector selection for patient management | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-045 | Pre-selection of already-linked patients | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-046 | Assistido (attend-to) action on a bed's care pathway (fronte | movimentacao-adt | NOT_APPLICABLE | ADAPT | [correlation-engine.md §assistido-acknowledgement](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-047 | Cardiorespiratory arrest capture (nullable group) | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §parada-cardiorrespiratoria](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-048 | Fixed 3-second minimum spinner on bed camera page | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-MOVIMENTACAO-ADT-049 | Test/temporary bed exclusion filter (AND semantics) | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-MOVIMENTACAO-ADT-050 | Bed occupancy and active-status mapping (Tasy indicators) | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-051 | Manual occupied bed requires a movimentacao | movimentacao-adt | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §occupancy-encounter-consistency](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-052 | Bed/company monitoring-modality enumeration (manual∣automati | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §leito-tipo](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-053 | Invasive-procedure type enumeration (10 values) | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §procedimento-invasivo](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-054 | Patient gender icon mapping | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-055 | Discharge (baixa) requires BOTH exit date and reason | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §baixa-leito](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-056 | Movimentacao requires patient unless it chains a prior movim | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §movimentacao-chaining](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-057 | Movimentacao data_entrada - absent OK, empty invalid, future | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §admission-timestamp-validation](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-058 | Automatic-type bed rejects movimentacao lacking data_entrada | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-MOVIMENTACAO-ADT-059 | Entry date must not be in the future (DataValidation) | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §future-date-guard](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-060 | Birthdate must not be in the future + patient payload requir | movimentacao-adt | NOT_APPLICABLE | ADAPT | [clinical-forms.md §cadastro-paciente](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-061 | dados_prontuario payload required | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §prontuario-required](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-062 | Movimentacao creation composite validation | movimentacao-adt | NOT_APPLICABLE | ADOPT | [correlation-engine.md §composite-admission-validation](clinical/domains/correlation-engine.md) | — |
| RULE-MOVIMENTACAO-ADT-063 | Movimentacao chronic-condition / pathway flags | movimentacao-adt | NOT_APPLICABLE | ADOPT | [clinical-forms.md §flags-clinicos](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-064 | Patient registration required fields and identifiers | movimentacao-adt | NOT_APPLICABLE | ADAPT | [security-lgpd.md §cpf-validation](architecture/security-lgpd.md) | — |
| RULE-MOVIMENTACAO-ADT-065 | InfoPaciente listing scoped by encounter | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-MOVIMENTACAO-ADT-066 | Update-patient-list button disabled check uses array referen | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-MOVIMENTACAO-ADT-067 | Bed-movement prontuário field annulment and date formatting | movimentacao-adt | NOT_APPLICABLE | ADAPT | [clinical-forms.md §prontuario-submit-normalization](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-068 | Past-prontuário date field hydration | movimentacao-adt | NOT_APPLICABLE | ADAPT | [clinical-forms.md §prontuario-hydration](design/screens/clinical-forms.md) | — |
| RULE-MOVIMENTACAO-ADT-069 | FormProntuario fields have no bound input controls | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-MOVIMENTACAO-ADT-070 | FilterOcupacoes "todos" sentinel and occupancy creation-type | movimentacao-adt | NOT_APPLICABLE | RETIRE | — | — |
| RULE-NUTRICAO-001 | BMI (IMC) auto-calculation | nutricao | VERIFIED | ADOPT | [clinical-forms.md §imc](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-002 | FOIS (Functional Oral Intake Scale) - enum of 7 levels | nutricao | VERIFIED | ADOPT | [clinical-forms.md §fois](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-003 | Nutrition-therapy pathway (payload_trilha_nutricao) - tolera | nutricao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-nutricao-01](RATIFICATION.md) | P1 |
| RULE-NUTRICAO-004 | Nutrition alert computation (calcular_alerta) - AMARELO bran | nutricao | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §alert-severity-taxonomy](clinical/domains/correlation-engine.md) | P3 |
| RULE-NUTRICAO-005 | Nutrition-therapy assessment block (frontend) - diet routes, | nutricao | DISCREPANCY | ADAPT | [clinical-forms.md §terapia-nutricional](design/screens/clinical-forms.md) | P2 |
| RULE-NUTRICAO-006 | Stress-ulcer / nutrition prophylaxis indication enum | nutricao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-nutricao-02](RATIFICATION.md) | P2 |
| RULE-NUTRICAO-007 | Dietitian daily-objectives conditional prescribed volumes | nutricao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §objetivos-diarios](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-008 | Height (altura) range validation 0-3 m | nutricao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §altura-validacao](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-009 | Food intolerance / aversion enums with conditional descripti | nutricao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §intolerancia-aversao](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-010 | Care-risk (riscos assistenciais) checklist with allergy deta | nutricao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §riscos-assistenciais](design/screens/clinical-forms.md) | — |
| RULE-NUTRICAO-011 | Dietitian abdominal assessment enums (extended) | nutricao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §avaliacao-abdominal](design/screens/clinical-forms.md) | — |
| RULE-OPERACIONAL-INFRA-001 | Round timestamp to whole hour (get_hora_cheia / justOclock) | operacional-infra | DISCREPANCY | RETIRE | — | P2 |
| RULE-OPERACIONAL-INFRA-002 | Patient name abbreviation with connective handling (nome_abr | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-003 | Offline prescriptions grouped by day, keyed by patient atend | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-004 | Continuous prescription 'real day' rolls over at 07:00 (shif | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-005 | Offline prescriptions windowed to the last 3 days, ordered b | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-006 | Length of stay (TEMPO_PERMANENCIA) computed property | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-05](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-007 | Pagination page-count and default page size | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-06](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-008 | Minutes elapsed between two dates | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-009 | format_horario — normalize hour-only strings to HH:MM | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-08](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-010 | parse_date_to_iso — multi-format date string parser with fix | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-09](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-011 | get_number — safe numeric coercion with zero default | operacional-infra | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-10](RATIFICATION.md) | UNVERIFIABLE |
| RULE-OPERACIONAL-INFRA-012 | popular_banco RASS enum values (synthetic data) | operacional-infra | VERIFIED | ADOPT | [neuro-sedation.md §rass-scale](clinical/domains/neuro-sedation.md) | — |
| RULE-OPERACIONAL-INFRA-013 | popular_banco SDRA (ARDS) severity enum (synthetic data) | operacional-infra | VERIFIED | ADOPT | [respiratory.md §ards-severity](clinical/domains/respiratory.md) | — |
| RULE-OPERACIONAL-INFRA-014 | Android TWA Digital Asset Links restricted to a single homol | operacional-infra | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-OPERACIONAL-INFRA-015 | Exclude entities already in a given access group | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-016 | Evolution (Formulario) full-day date-range filter | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-017 | ParanoiaMixin.delete/restore — admin-path hard delete vs cas | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-11](RATIFICATION.md) | AMBIGUOUS |
| RULE-OPERACIONAL-INFRA-018 | SetUpModel.delete — overrides ParanoiaMixin.delete with simp | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §soft-delete-audit-trail](architecture/security-lgpd.md) | P3 |
| RULE-OPERACIONAL-INFRA-019 | Offline water balance shows the last 2 records for an occupi | operacional-infra | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-OPERACIONAL-INFRA-020 | Offline evolution forms visible if authored by the requestin | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §draft-form-visibility](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-021 | Offline endpoints hardcode empresa lookup to whitelabel='hom | operacional-infra | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-OPERACIONAL-INFRA-022 | Offline bed access requires user membership at every level o | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-scoped-access](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-023 | Prescription/balance offline endpoints only include currentl | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-024 | Offline horario-prescricao deletion capability is permission | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-gated-destructive-actions](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-025 | Per-queue Celery worker concurrency assignment (serialize pa | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-026 | start.sh production branch references a uwsgi ini file absen | operacional-infra | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-OPERACIONAL-INFRA-027 | Environment classification from base URL | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-028 | Pagination control disabled when everything fits on one page | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-029 | Shift-day (turno) calendar-date assignment | operacional-infra | NOT_APPLICABLE | ADAPT | [correlation-engine.md §shift-day-windowing](clinical/domains/correlation-engine.md) | — |
| RULE-OPERACIONAL-INFRA-030 | Shared default search-result limit and debounce interval | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-031 | CreateSearchInput overrides configured limit to 5 on empty k | operacional-infra | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-OPERACIONAL-INFRA-032 | popular_banco valores_maximos_atributos — vital-sign referen | operacional-infra | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-operacional-infra-01](RATIFICATION.md) | P3 |
| RULE-OPERACIONAL-INFRA-033 | TEMPO_ATUALIZACAO_TRILHAS — automatic pathway recalculation  | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-034 | Shift-turnover (virada de turno) cutoff for date navigation | operacional-infra | NOT_APPLICABLE | ADAPT | [clinical-forms.md §shift-date-navigation](design/screens/clinical-forms.md) | — |
| RULE-OPERACIONAL-INFRA-035 | data_7_as_7 — 7am-to-7am shift/reporting-day boundary | operacional-infra | NOT_APPLICABLE | ADAPT | [early-warning-scores.md §shift-reporting-day](clinical/domains/early-warning-scores.md) | — |
| RULE-OPERACIONAL-INFRA-036 | custom_exception_handler / flatten_errors — DRF error envelo | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-02](RATIFICATION.md) | P3 |
| RULE-OPERACIONAL-INFRA-037 | ListChoiceField.to_representation — context-dependent repres | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-03](RATIFICATION.md) | AMBIGUOUS |
| RULE-OPERACIONAL-INFRA-038 | PWA service-worker generation disabled only in local develop | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-039 | PM2 multi-environment process configuration | operacional-infra | NOT_APPLICABLE | SUPERSEDE | [SUPERSEDE: ADR-001 ECS Fargate deployment mechanism](SUPERSEDE: ADR-001 ECS Fargate deployment mechanism) | — |
| RULE-OPERACIONAL-INFRA-040 | Per-environment deploy script workflow with asymmetric env-f | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-04](RATIFICATION.md) | AMBIGUOUS |
| RULE-OPERACIONAL-INFRA-041 | Environment secret files excluded from version control per d | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §secrets-management](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-042 | PWA app identity and installed-app display behavior | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-043 | Breadcrumb hides UUID-shaped route segments | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-044 | Assistido flag reset - 1-minute update window | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-045 | Interactive sepsis - overdue item auto-check and alert messa | operacional-infra | NOT_APPLICABLE | ADAPT | [sepsis.md §overdue-checklist-alerting](clinical/domains/sepsis.md) | — |
| RULE-OPERACIONAL-INFRA-046 | Celery queue naming convention — environment-namespaced rout | operacional-infra | NOT_APPLICABLE | SUPERSEDE | [system-architecture.md §alternativa-b-msk-streaming-escape-hatch](architecture/system-architecture.md) | — |
| RULE-OPERACIONAL-INFRA-047 | Celery beat scheduler — DatabaseScheduler, with a duplicate- | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-05](RATIFICATION.md) | P3 |
| RULE-OPERACIONAL-INFRA-048 | Backend CI gate covers only trilha_manual tests | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §ci-test-coverage-clinical-engines](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-049 | Nursing-shift day window 07:00-07:00 | operacional-infra | NOT_APPLICABLE | ADAPT | [clinical-forms.md §shift-date-navigation](design/screens/clinical-forms.md) | — |
| RULE-OPERACIONAL-INFRA-050 | next/image remote image domain whitelist | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §remote-asset-allowlisting](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-051 | Uniqueness constraints across org hierarchy | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-hierarchy-uniqueness](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-052 | Observation-by-bed includes replies to that bed | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-053 | UniqueTogetherManagerMixin.save — composite uniqueness exclu | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-054 | UniqueManagerMixin.save — single-field uniqueness excluding  | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-055 | popular_banco gender enum (synthetic data) | operacional-infra | NOT_APPLICABLE | ADOPT | [clinical-forms.md §gender-enum](design/screens/clinical-forms.md) | — |
| RULE-OPERACIONAL-INFRA-056 | Diagnosis-list checks are non-functional (vars().fromkeys mi | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-06](RATIFICATION.md) | P3 |
| RULE-OPERACIONAL-INFRA-057 | upload_to — model-type-based storage folder convention | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-058 | verificar_setor_da_empresa — tenant-hierarchy consistency ch | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §tenant-hierarchy-consistency](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-059 | Per-company auto-refresh interval field | operacional-infra | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-operacional-infra-07](RATIFICATION.md) | AMBIGUOUS |
| RULE-OPERACIONAL-INFRA-060 | TasyModel Oracle database routing (reads and writes forced t | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-OPERACIONAL-INFRA-061 | Request-body upload size cap (DATA_UPLOAD_MAX_MEMORY_SIZE =  | operacional-infra | NOT_APPLICABLE | ADAPT | [security-lgpd.md §upload-size-limits](architecture/security-lgpd.md) | — |
| RULE-OPERACIONAL-INFRA-062 | Per-environment uWSGI worker capacity and recycling threshol | operacional-infra | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PIORA-CLINICA-001 | Piora Clinica criterio_1 - Frequencia respiratoria (graded s | piora-clinica | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-piora-clinica-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-PIORA-CLINICA-002 | Piora Clinica criterio_2 - Temperatura axilar (graded sub-sc | piora-clinica | DISCREPANCY | ADOPT-CORRECTED | [early-warning-scores.md §piora-clinica-temperatura](clinical/domains/early-warning-scores.md) | P2 |
| RULE-PIORA-CLINICA-003 | Piora Clinica criterio_3 - Pressao arterial sistolica (PAS)  | piora-clinica | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-piora-clinica-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-PIORA-CLINICA-004 | Piora Clinica criterio_4 - Frequencia cardiaca (FC) (graded  | piora-clinica | DISCREPANCY | ADOPT-CORRECTED | [hemodynamics.md §piora-clinica-fc](clinical/domains/hemodynamics.md) | P2 |
| RULE-PIORA-CLINICA-005 | Piora Clinica criterio_5 - Nivel de consciencia (graded sub- | piora-clinica | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-piora-clinica-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-PIORA-CLINICA-006 | Piora Clinica criterio_6 - Dor (escala numerica 0-10) (grade | piora-clinica | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-piora-clinica-04](RATIFICATION.md) | P0 |
| RULE-PIORA-CLINICA-007 | Piora Clinica criterio_7 - Dor (escala comportamental 3-12)  | piora-clinica | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-piora-clinica-05](RATIFICATION.md) | P0 |
| RULE-PIORA-CLINICA-008 | Piora Clinica criterio_8 - SatO2 (paciente regular / nao-DPO | piora-clinica | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-piora-clinica-06](RATIFICATION.md) | P1 |
| RULE-PIORA-CLINICA-009 | Piora Clinica criterio_9 - SatO2 (paciente DPOC/COPD) (grade | piora-clinica | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-piora-clinica-07](RATIFICATION.md) | P1 |
| RULE-PIORA-CLINICA-010 | Piora Clinica - Calculo do alerta (soma agregada + gatilho p | piora-clinica | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-piora-clinica-08](RATIFICATION.md) | P0 |
| RULE-PIORA-CLINICA-011 | Piora Clinica - Payload de alertas/recomendacoes/intervencoe | piora-clinica | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-piora-clinica-09](RATIFICATION.md) | UNVERIFIABLE |
| RULE-PIORA-CLINICA-012 | Vital signs entry auto-creates clinical-worsening (PioraClin | piora-clinica | NOT_APPLICABLE | SUPERSEDE | [early-warning-scores.md §score-computation-trigger](clinical/domains/early-warning-scores.md) | — |
| RULE-PRESCRICAO-001 | ml medications capture exported quantity for fluid balance ( | prescricao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-prescricao-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-PRESCRICAO-002 | Dose-level medication suspension check (get_suspenso) | prescricao | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-PRESCRICAO-003 | Continuous-prescription (order-level) suspension flag - now- | prescricao | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-PRESCRICAO-004 | Prescription day-boundary rule for exporting a dose quantity | prescricao | NOT_APPLICABLE | ADAPT | [hemodynamics.md §fluid-balance-day-boundary](clinical/domains/hemodynamics.md) | — |
| RULE-PRESCRICAO-005 | 07:00 shift-boundary reordering of scheduled dose times for  | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-006 | Offline prescription validity days | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-007 | Prescription-item type priority ordering (5-tier) | prescricao | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-PRESCRICAO-008 | Prescription horario administration/cancellation/reschedule  | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-009 | Medication administration status -> checkbox icon and actor  | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-010 | Continuous-prescription (PrescricaoContinua) daily generatio | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-011 | Prescription time-slot (horario) visual status priority | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-012 | Horario persistence routing (POST / PATCH / DELETE) | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-013 | Save vs Save-and-check vs Update-time decision when hour edi | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-014 | Delete authorization for a scheduled dose (get_can_delete) | prescricao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §deny-by-default-authorization](architecture/security-lgpd.md) | P3 |
| RULE-PRESCRICAO-015 | Delete horario only when can_delete | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-016 | Add-new-horario button eligibility | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-017 | Only the checking user may revert a check | prescricao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §originator-only-revert](architecture/security-lgpd.md) | — |
| RULE-PRESCRICAO-018 | can_manage_prescricao gates all administration controls | prescricao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §permission-gated-controls](architecture/security-lgpd.md) | — |
| RULE-PRESCRICAO-019 | Medication reconciliation logic | prescricao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §medication-reconciliation](design/screens/clinical-forms.md) | — |
| RULE-PRESCRICAO-020 | Geracao de horarios a partir de DS_HORARIOS | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-021 | Bulk medication-administration checkoff (multi_checagem) | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-022 | Horario prescricao manage_data payload injection | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-023 | Suspended horario blocks all administration actions | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-024 | Quick "administered" check without reason | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-025 | Administration-check form value construction | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-026 | Revert administration check requires justification | prescricao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §justification-required-for-reversal](architecture/security-lgpd.md) | — |
| RULE-PRESCRICAO-027 | Antibiotic course tracking list (with malformed field) | prescricao | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §antibiotic-course-tracking](design/screens/clinical-forms.md) | P3 |
| RULE-PRESCRICAO-028 | Prescription-dose administration/cancellation lifecycle | prescricao | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-PRESCRICAO-029 | Not-administered reason enum (motivo_nao_administrado) | prescricao | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §motivo-nao-administrado](design/screens/clinical-forms.md) | P3 |
| RULE-PRESCRICAO-030 | Not-administered reason enum with "outros" free-text require | prescricao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §motivo-nao-administrado](design/screens/clinical-forms.md) | — |
| RULE-PRESCRICAO-031 | Add-new-horario requires a time (HH:mm) | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-032 | Horario de prescricao - autor padrao 'sistema' | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-033 | Horario prescricao scoped to parent prescricao continua | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PRESCRICAO-034 | Only the checking user may cancel a scheduled dose | prescricao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §checador-only-cancellation](architecture/security-lgpd.md) | — |
| RULE-PRESCRICAO-035 | Non-administration reason validation (effectively unreachabl | prescricao | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-PRESCRICAO-036 | Checagem lock — cannot alter administration status once set  | prescricao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-prescricao-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-PRESCRICAO-037 | Pharmacist global assessment (risks with dead conditionals) | prescricao | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §pharmacist-risk-assessment](design/screens/clinical-forms.md) | P3 |
| RULE-PRESCRICAO-038 | Pharmacist prophylaxis checklist | prescricao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §pharmacist-prophylaxis](design/screens/clinical-forms.md) | — |
| RULE-PRESCRICAO-039 | Pharmacist intervention vocabulary | prescricao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §pharmacist-intervention-vocabulary](design/screens/clinical-forms.md) | — |
| RULE-PRESCRICAO-040 | Pharmacist form variable/file naming mismatch | prescricao | NOT_APPLICABLE | RETIRE | — | P3 |
| RULE-PRESCRICAO-041 | Prescricao continua day filter | prescricao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-PROFILAXIA-001 | Prophylaxis v1 - hyperglycemia subcutaneous insulin NPH slid | profilaxia | VERIFIED | ADOPT | [pharmaco-interaction.md §insulina-hiperglicemia](clinical/domains/pharmaco-interaction.md) | — |
| RULE-PROFILAXIA-002 | Prophylaxis v1 - VTE anticoagulation dosing by renal functio | profilaxia | VERIFIED | ADOPT | [pharmaco-interaction.md §profilaxia-tev](clinical/domains/pharmaco-interaction.md) | — |
| RULE-PROFILAXIA-003 | Prophylaxis v1 alert aggregation (amarelo/vermelho scoring) | profilaxia | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §alert-severity-taxonomy](clinical/domains/correlation-engine.md) | — |
| RULE-PROFILAXIA-004 | Prophylaxis v3 alert aggregation (amarelo/vermelho scoring) | profilaxia | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §alert-severity-taxonomy](clinical/domains/correlation-engine.md) | — |
| RULE-PROFILAXIA-005 | Prophylaxis v3 criterio_1 - GI stress-ulcer (LAMGD) prophyla | profilaxia | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-profilaxia-01](RATIFICATION.md) | P1 |
| RULE-PROFILAXIA-006 | Prophylaxis v3 criterio_9 - invasive device prescribed (VERM | profilaxia | NOT_APPLICABLE | ADOPT | [sepsis.md §device-associated-infection-bundle](clinical/domains/sepsis.md) | — |
| RULE-PROFILAXIA-007 | Prophylaxis v1 - LAMGD (stress-ulcer) prophylaxis, mobilizat | profilaxia | NOT_APPLICABLE | ADAPT | [sepsis.md §profilaxia-icu-bundle](clinical/domains/sepsis.md) | — |
| RULE-PROFILAXIA-008 | Prophylaxis v3 - reduced active criteria set facade (LAMGD + | profilaxia | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-profilaxia-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-SEDACAO-001 | Sedacao v3 criterio_7 - moderate pain (analog 4-6 / BPS 7-9) | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §pain-moderate-two-consecutive](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-002 | Sedacao v3 criterio_8 - severe pain (analog 7-10 / BPS 10-12 | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §pain-severe-two-consecutive](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-003 | Sedacao v3 criterio_9 - deep sedation RASS -3..-5 (defined,  | sedacao | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §deep-sedation-rass](clinical/domains/neuro-sedation.md) | P3 |
| RULE-SEDACAO-004 | Sedacao v3 criterio_12 - weaning readiness (defined, unwired | sedacao | DISCREPANCY | ADOPT-CORRECTED | [respiratory.md §weaning-readiness](clinical/domains/respiratory.md) | P3 |
| RULE-SEDACAO-005 | Sedacao v3 criterio_1 - excessive continuous sedation infusi | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-006 | Sedacao v3 criterio_2 - sedation despite adequate oxygenatio | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §sedation-despite-adequate-oxygenation](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-007 | Sedacao v3 criterio_3 - neuromuscular blockade with P/F>150  | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §neuromuscular-blockade-deescalation](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-008 | Sedacao v3 criterio_4 - undersedation on invasive vent (defi | sedacao | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §undersedation-invasive-vent](clinical/domains/neuro-sedation.md) | P2 |
| RULE-SEDACAO-009 | Sedacao v3 criterio_5 - no morning sedation reduction (>=1/2 | sedacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sedacao-02](RATIFICATION.md) | P1 |
| RULE-SEDACAO-010 | Sedacao v3 criterio_6 - high-dose neuromuscular blockade (de | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-011 | Sedacao v3 criterio_10 - prolonged sedation >96h (defined, u | sedacao | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §prolonged-sedation-96h](clinical/domains/neuro-sedation.md) | P3 |
| RULE-SEDACAO-012 | Sedacao v3 criterio_11 - prolonged propofol without safety l | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §pris-surveillance](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-013 | Sedacao v3 active-sedative detection (set_sedativo_em_uso) | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-014 | Sedacao v3 alert (calcular_alerta_v2 used; legacy calcular_a | sedacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sedacao-05](RATIFICATION.md) | — |
| RULE-SEDACAO-015 | Sedation manual C1 - sedoanalgesia overdose (any sedative >1 | sedacao | NOT_APPLICABLE | ADAPT | [neuro-sedation.md §sedative-overdose-threshold](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-016 | Sedation manual C2 - deep RASS with low FiO2/PEEP | sedacao | DISCREPANCY | ADOPT-CORRECTED | [neuro-sedation.md §deep-sedation-low-vent-support](clinical/domains/neuro-sedation.md) | P3 |
| RULE-SEDACAO-017 | Sedation manual C3 - good oxygenation on sedation | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §sedation-lightening-candidate](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-018 | Sedation manual C4 - sedation justified by severity | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-06](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-019 | Sedation manual C5 - poor oxygenation with light/absent seda | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-020 | Sedation manual C6 - severity without sedation | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-08](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-021 | Sedation manual pathway alert level (count of criteria) | sedacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sedacao-09](RATIFICATION.md) | — |
| RULE-SEDACAO-022 | Cardiac arrest within last 24h (PCR-24h helper, manual model | sedacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sedacao-10](RATIFICATION.md) | AMBIGUOUS |
| RULE-SEDACAO-023 | Sedacao v1 alert (TrilhaSedacaoModel.calcular_alerta) | sedacao | NOT_APPLICABLE | SUPERSEDE | [neuro-sedation.md §sedation-alert-aggregation](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-024 | Sedation/analgesia pathway recommendation catalog (facade te | sedacao | VERIFIED | ADOPT | [neuro-sedation.md §recommendation-catalog](clinical/domains/neuro-sedation.md) | — |
| RULE-SEDACAO-025 | Sedative-specific reduction recommendation (criterio_1 free  | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-11](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-026 | Sedative drug enumeration (Sedativo.nome_sedativo choices) | sedacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sedacao-12](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEDACAO-027 | Unique sedative per prontuario + dose unit | sedacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-001 | SEPSE v1 alert maiores/menores dual threshold | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-002 | SEPSE v3 alert maiores/menores (OR thresholds) + risk messag | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-02](RATIFICATION.md) | P1 |
| RULE-SEPSE-003 | Sepse - Classificacao de alerta (maiores/menores) | sepse | DISCREPANCY | SUPERSEDE | [sepsis.md §screening-major-minor](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-004 | Sepsis pathway alert (major/minor two-axis threshold) | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-005 | Sepse - Hierarquia de nivel de consciencia | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-006 | SEPSE v3 assistencial info snapshot (diurese/BH aggregation) | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-05](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-007 | SEPSE v3 criterio_1 - fever without vasopressor | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-06](RATIFICATION.md) | P1 |
| RULE-SEPSE-008 | SEPSE v3 criterio_2 - tachypnea/hypoxemia without vasopresso | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-tachypnea-hypoxemia](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-009 | SEPSE v3 criterio_3 - respiratory failure prescription | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-07](RATIFICATION.md) | P1 |
| RULE-SEPSE-010 | SEPSE v3 criterio_4 - newly started vasopressor | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-new-vasopressor](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-011 | SEPSE v3 criterio_5 - hypotension without vasopressor | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-hypotension](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-012 | SEPSE v3 criterio_6 - thrombocytopenia without vasopressor | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-thrombocytopenia](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-013 | SEPSE v3 criterio_7 - hyperlactatemia without vasopressor | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §criterio-hyperlactatemia](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-014 | SEPSE v3 criterio_8 - oliguria without vasopressor/dialysis | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-08](RATIFICATION.md) | P0 |
| RULE-SEPSE-015 | SEPSE v3 criterio_9 - acute kidney injury without vasopresso | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-09](RATIFICATION.md) | P1 |
| RULE-SEPSE-016 | SEPSE v3 criterio_10 - acute encephalopathy/delirium | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-10](RATIFICATION.md) | P1 |
| RULE-SEPSE-017 | SEPSE v3 criterio_11 - hyperbilirubinemia/jaundice (incomple | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-11](RATIFICATION.md) | P1 |
| RULE-SEPSE-018 | SEPSE v3 criterio_12 - hypothermia (minor) | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-hypothermia](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-019 | SEPSE v3 criterio_13 - tachycardia (minor, wrong column) | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-12](RATIFICATION.md) | P1 |
| RULE-SEPSE-020 | SEPSE v3 criterio_14 - respiratory alkalosis/hypoxemia spont | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-13](RATIFICATION.md) | P1 |
| RULE-SEPSE-021 | SEPSE v3 criterio_15 - leukocytosis/leukopenia/bandemia/CRP  | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-14](RATIFICATION.md) | P1 |
| RULE-SEPSE-022 | SEPSE v3 criterio_16 - prolonged capillary refill (minor, ne | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-capillary-refill](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-023 | SEPSE v3 criterio_17 - enteral tube with adequate GCS (minor | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-15](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-024 | SEPSE v3 criterio_18 - central line > 7 days (minor) | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-16](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-025 | SEPSE v3 criterio_19 - femoral central line > 5 days (minor) | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-17](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-026 | SEPSE v3 criterio_20 - recent abdominal surgery (minor) | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-18](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-027 | Sepse criterio_1 - Febre (fever) | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-febre](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-028 | Sepse criterio_2 - Taquipneia / dessaturacao sob O2 | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-taquipneia](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-029 | Sepse criterio_3 - Escalonamento de suporte ventilatorio | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-19](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-030 | Sepse criterio_4 - Tempo de enchimento capilar > 5s | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §criterio-tec](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-031 | Sepse criterio_5 - Hipotensao | sepse | VERIFIED | ADOPT | [sepsis.md §criterio-hipotensao](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-032 | Sepse criterio_6 - Oliguria (sonda) ou dessaturacao | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-20](RATIFICATION.md) | P1 |
| RULE-SEPSE-033 | Sepse criterio_7 - Variacao do nivel de consciencia | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-21](RATIFICATION.md) | P1 |
| RULE-SEPSE-034 | Sepse criterio_8 - Hipotermia | sepse | VERIFIED | ADOPT | [sepsis.md §hypothermia-minor-c8](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-035 | Sepse criterio_9 - Taquicardia | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §tachycardia-minor-c9](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-036 | Sepse criterio_10 - Dispositivo invasivo com permanencia > 7 | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-037 | Sepse criterio_11 - Placeholder (sempre False) | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-02](RATIFICATION.md) | P1 |
| RULE-SEPSE-038 | Sepsis C1 (major) - fever | sepse | VERIFIED | ADOPT | [sepsis.md §fever-major-c1](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-039 | Sepsis C2 (major) - spontaneous respiratory distress | sepse | VERIFIED | ADOPT | [sepsis.md §respiratory-distress-major-c2](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-040 | Sepsis C3 (major) - recent start of mechanical ventilation | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-041 | Sepsis C4 (major) - noradrenaline started in last 24h | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-042 | Sepsis C5 (major) - slow capillary refill | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §capillary-refill-major-c5](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-043 | Sepsis C6 (major) - hypotension (PAS<90 or PAD<90 in 24h) | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-22](RATIFICATION.md) | P0 |
| RULE-SEPSE-044 | Sepsis C7 (major) - oliguria or rising creatinine | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-06](RATIFICATION.md) | P1 |
| RULE-SEPSE-045 | Sepsis C8 (major) - Glasgow drop or delirium | sepse | VERIFIED | ADOPT | [sepsis.md §glasgow-drop-or-delirium-major-c8](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-046 | Sepsis C9 (major) - hyperbilirubinemia | sepse | VERIFIED | ADOPT | [sepsis.md §hyperbilirubinemia-major-c9](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-047 | Sepsis C10 (minor) - hypothermia in last 24h | sepse | VERIFIED | ADOPT | [sepsis.md §hypothermia-minor-c10](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-048 | Sepsis C11 (minor) - tachycardia | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §tachycardia-minor-c11](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-049 | Sepsis C12 (minor) - hypocapnia or poor oxygenation | sepse | VERIFIED | ADOPT | [sepsis.md §hypocapnia-oxygenation-minor-c12](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-050 | Sepsis C13 (minor) - elevated arterial lactate | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §lactate-minor-c13](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-051 | Sepsis C14 (minor) - leukocytosis in last 24h | sepse | VERIFIED | ADOPT | [sepsis.md §leukocytosis-minor-c14](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-052 | Sepsis C15 (minor) - thrombocytopenia in last 24h | sepse | VERIFIED | ADOPT | [sepsis.md §thrombocytopenia-minor-c15](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-053 | Sepsis C16 (minor) - poor oral intake with preserved conscio | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-054 | Sepsis C17 (minor) - depressed consciousness in last 12h | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §altered-mentation-minor-c17](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-055 | Sepsis C18 (minor) - central line > 7 days | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-23](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-056 | Sepsis C19 (minor) - femoral central line > 5 days | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-09](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-057 | Sepsis C20 (minor) - recent abdominal surgery | sepse | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sepse-10](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SEPSE-058 | Sepse v3 automatica - trigger threshold table (20 criteria) | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-11](RATIFICATION.md) | P1 |
| RULE-SEPSE-059 | Sepse automatica variant B - 27-criterion alert catalog + gl | sepse | DISCREPANCY | ADAPT | [sepsis.md §hour-1-bundle-global-recommendation](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-060 | Sepse pathway variant A - 11-criterion catalog + Meropenem/1 | sepse | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sepse-12](RATIFICATION.md) | P1 |
| RULE-SEPSE-061 | SEPSE volume expansion (expansao volemica) decision and dosi | sepse | DISCREPANCY | ADOPT-CORRECTED | [sepsis.md §volume-resuscitation-dosing](clinical/domains/sepsis.md) | P2 |
| RULE-SEPSE-062 | SEPSE reassessment lab thresholds (bicarbonate, dobutamine,  | sepse | VERIFIED | ADOPT | [sepsis.md §reassessment-labs](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-063 | SEPSE hemodynamic-status decision (intubation RASS-2, fluid  | sepse | VERIFIED | ADOPT | [sepsis.md §hemodynamic-status-decision](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-064 | SEPSE invasive-devices decision (early NE, central access, C | sepse | NOT_APPLICABLE | ADOPT | [sepsis.md §invasive-devices-decision](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-065 | SEPSE vasoactive-drug escalation thresholds and shock index | sepse | VERIFIED | ADOPT | [sepsis.md §vasoactive-escalation](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-066 | Sepsis pathway - disabled/legacy criteria (v-old 27 vs curre | sepse | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-SEPSE-067 | Sepsis / infection-source screening flags (movimentacao) | sepse | NOT_APPLICABLE | ADOPT | [sepsis.md §infection-source-screening-flags](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-068 | Urea field encodes an unbounded value under a threshold name | sepse | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sepse-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-SEPSE-069 | Bundle item overdue (atraso_item_interativa) time windows | sepse | VERIFIED | ADOPT | [sepsis.md §hour-1-bundle-timers](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-070 | Bundle item visibility (exibir) - reassessment appears after | sepse | NOT_APPLICABLE | ADOPT | [sepsis.md §hour-1-bundle-timers](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-071 | SEPSE v3 interactive-protocol creation gate (can_criar_novo_ | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §protocol-creation-eligibility](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-072 | SEPSE protocol acceptance workflow and orange alert | sepse | NOT_APPLICABLE | SUPERSEDE | [sepsis.md §protocol-acceptance-lifecycle](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-073 | SEPSE protocol rejection workflow and neutral alert | sepse | NOT_APPLICABLE | SUPERSEDE | [sepsis.md §protocol-acceptance-lifecycle](clinical/domains/sepsis.md) | P3 |
| RULE-SEPSE-074 | SEPSE protocol closure (accepted -> encerrado) workflow | sepse | NOT_APPLICABLE | SUPERSEDE | [sepsis.md §protocol-acceptance-lifecycle](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-075 | SEPSE item check / uncheck and protocol completion state mac | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-completion](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-076 | SEPSE interactive protocol bundle (hour-1 vs reassessment it | sepse | NOT_APPLICABLE | ADOPT | [sepsis.md §hour-1-bundle](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-077 | SEPSE item checker auto-attribution | sepse | NOT_APPLICABLE | ADAPT | [security-lgpd.md §server-side-actor-attribution](architecture/security-lgpd.md) | — |
| RULE-SEPSE-078 | Sepsis first-hour auto-check guard | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-automation](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-079 | Sepsis 1h bundle - exam solicitation auto-check | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-automation](clinical/domains/sepsis.md) | P3 |
| RULE-SEPSE-080 | Sepsis 1h bundle - antimicrobial escalation auto-check (24h  | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-automation](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-081 | Sepsis 1h bundle - volume expansion auto-check (4h window) | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-automation](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-082 | Vital signs entry auto-creates sepsis-screening (Sepse) reco | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §screening-trigger](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-083 | Interactive sepsis trail filtered by bed | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-084 | Active sepsis care-pathway selection | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-085 | Interactive sepsis pathway completion transition | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-086 | Historical sepsis pathway instances filtered by aceito=false | sepse | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-SEPSE-087 | Sepsis page "back" navigation preserves drawer context | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-088 | Empty-state for absent sepsis protocols | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-089 | Current protocol tab requires non-empty checklist items | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-090 | Sepsis protocol lifecycle state display | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §protocol-lifecycle](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-091 | Sepsis protocol item conditional visibility and expandabilit | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-092 | Sepsis protocol item check-off workflow | sepse | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SEPSE-093 | Sepsis-pathway dual completion flags | sepse | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sepse-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-SEPSE-094 | Sepsis-pathway accept/discard workflow | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §protocol-decline-workflow](clinical/domains/sepsis.md) | — |
| RULE-SEPSE-095 | Sepsis protocol item first-hour delay alert | sepse | NOT_APPLICABLE | ADAPT | [sepsis.md §hour-1-bundle-timers](clinical/domains/sepsis.md) | P3 |
| RULE-SEPSE-096 | Sepsis interactive bundle step and package enums | sepse | NOT_APPLICABLE | ADOPT | [clinical-forms.md §sepsis-hour1-bundle-items](design/screens/clinical-forms.md) | — |
| RULE-SEPSE-097 | Sepsis protocol refusal permission | sepse | NOT_APPLICABLE | ADAPT | [security-lgpd.md §rbac-clinical-protocol-actions](architecture/security-lgpd.md) | — |
| RULE-SEPSE-098 | Sepsis-checklist signer requires CPF, unlike other checklist | sepse | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sepse-03](RATIFICATION.md) | AMBIGUOUS |
| RULE-SEPSE-099 | Manual sepsis pathway active criteria descriptions (_REGRAS, | sepse | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sepse-add-01](RATIFICATION.md) | ADDENDUM |
| RULE-SINAIS-VITAIS-001 | Blood-pressure and heart-rate plausible ranges (movimentacao | sinais-vitais | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SINAIS-VITAIS-002 | Blood-gas and laboratory plausible ranges (movimentacao form | sinais-vitais | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SINAIS-VITAIS-003 | Urine-output and temperature plausible ranges (movimentacao  | sinais-vitais | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SINAIS-VITAIS-004 | Capillary refill time (TEC) range and >5s threshold — incons | sinais-vitais | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sinais-vitais-01](RATIFICATION.md) | P1 |
| RULE-SINAIS-VITAIS-005 | Physician-form vital-sign ranges (partial) — HR/FR/temp/SpO2 | sinais-vitais | NOT_APPLICABLE | ADAPT | [clinical-forms.md §vital-signs-entry-bounds](design/screens/clinical-forms.md) | P3 |
| RULE-SINAIS-VITAIS-006 | SinaisVitais listing includes soft-deleted records | sinais-vitais | NOT_APPLICABLE | ADAPT | [security-lgpd.md §soft-delete-non-deleted-manager](architecture/security-lgpd.md) | P3 |
| RULE-SINAIS-VITAIS-007 | SinaisVitais soft-delete logs audit action (no balance adjus | sinais-vitais | NOT_APPLICABLE | ADAPT | [security-lgpd.md §audit-trail-soft-delete](architecture/security-lgpd.md) | — |
| RULE-SINAIS-VITAIS-008 | SinaisVitais manage_data payload injection | sinais-vitais | NOT_APPLICABLE | RETIRE | — | — |
| RULE-SINAIS-VITAIS-009 | PorcentagemValidator — generic percentage range | sinais-vitais | NOT_APPLICABLE | ADOPT | [clinical-forms.md §percentage-field-validation](design/screens/clinical-forms.md) | — |
| RULE-SINAIS-VITAIS-010 | FiO2Validator — inspired oxygen fraction range, zero exempte | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §fio2-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-011 | GlasgowValidator — Glasgow Coma Scale range, zero exempted | sinais-vitais | VERIFIED | ADOPT | [neuro-sedation.md §gcs-range](clinical/domains/neuro-sedation.md) | — |
| RULE-SINAIS-VITAIS-012 | PeepValidator — PEEP range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §peep-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-013 | TecValidator — capillary refill time range, zero exempted | sinais-vitais | NOT_APPLICABLE | ADAPT | [hemodynamics.md §capillary-refill-time](clinical/domains/hemodynamics.md) | — |
| RULE-SINAIS-VITAIS-014 | Po2Validator — PaO2/PO2 range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §pao2-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-015 | FRValidator — respiratory rate range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §respiratory-rate-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-016 | LactatoArterialValidator — arterial lactate range, no zero e | sinais-vitais | NOT_APPLICABLE | ADOPT | [sepsis.md §lactate-bounds](clinical/domains/sepsis.md) | — |
| RULE-SINAIS-VITAIS-017 | VolumeCorrenteValidator — tidal volume range, no zero exempt | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §tidal-volume-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-018 | PASValidator — systolic blood pressure range, zero exempted | sinais-vitais | NOT_APPLICABLE | ADOPT | [hemodynamics.md §systolic-bp-bounds](clinical/domains/hemodynamics.md) | — |
| RULE-SINAIS-VITAIS-019 | PADValidator — diastolic blood pressure range, no zero exemp | sinais-vitais | NOT_APPLICABLE | ADOPT | [hemodynamics.md §diastolic-bp-bounds](clinical/domains/hemodynamics.md) | — |
| RULE-SINAIS-VITAIS-020 | PAMValidator — mean arterial pressure range, no zero exempti | sinais-vitais | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sinais-vitais-02](RATIFICATION.md) | — |
| RULE-SINAIS-VITAIS-021 | DebitoUrinario24hValidator — 24h urine output range, no zero | sinais-vitais | NOT_APPLICABLE | ADOPT | [aki.md §urine-output-bounds](clinical/domains/aki.md) | — |
| RULE-SINAIS-VITAIS-022 | BilirrubinasValidator — bilirubin range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [sepsis.md §bilirubin-bounds](clinical/domains/sepsis.md) | — |
| RULE-SINAIS-VITAIS-023 | TemperaturaValidator — body temperature range, zero exempted | sinais-vitais | NOT_APPLICABLE | ADOPT | [early-warning-scores.md §temperature-bounds](clinical/domains/early-warning-scores.md) | — |
| RULE-SINAIS-VITAIS-024 | PaCO2Validator — PaCO2 range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §paco2-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-025 | CreatininaValidator — creatinine range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [aki.md §creatinine-bounds](clinical/domains/aki.md) | — |
| RULE-SINAIS-VITAIS-026 | LeucocitosValidator — leukocyte count range, no zero exempti | sinais-vitais | NOT_APPLICABLE | ADOPT | [sepsis.md §leukocyte-bounds](clinical/domains/sepsis.md) | — |
| RULE-SINAIS-VITAIS-027 | FrequenciaCardiacaValidator — heart rate range, no zero exem | sinais-vitais | NOT_APPLICABLE | ADOPT | [early-warning-scores.md §heart-rate-bounds](clinical/domains/early-warning-scores.md) | — |
| RULE-SINAIS-VITAIS-028 | PlaquetasValidator — platelet count range, no zero exemption | sinais-vitais | NOT_APPLICABLE | ADOPT | [sepsis.md §platelet-bounds](clinical/domains/sepsis.md) | — |
| RULE-SINAIS-VITAIS-029 | DobutaminaValidator — dobutamine dose range, no zero exempti | sinais-vitais | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sinais-vitais-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SINAIS-VITAIS-030 | NoradrenalinaValidator — norepinephrine dose range, no zero  | sinais-vitais | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-sinais-vitais-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-SINAIS-VITAIS-031 | SedativoValidator — sedative dose range, no zero exemption | sinais-vitais | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-sinais-vitais-05](RATIFICATION.md) | P3 |
| RULE-SINAIS-VITAIS-032 | PressaoInspiratoriaValidator — inspiratory pressure (PINS) r | sinais-vitais | NOT_APPLICABLE | ADOPT | [respiratory.md §inspiratory-pressure-bounds](clinical/domains/respiratory.md) | — |
| RULE-SINAIS-VITAIS-033 | SatO2Validator — oxygen saturation range, no zero exemption  | sinais-vitais | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-sinais-vitais-06](RATIFICATION.md) | AMBIGUOUS |
| RULE-TENANCY-ORGANIZACAO-001 | Establishment occupancy percentage formula | tenancy-organizacao | VERIFIED | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-002 | Sector occupancy percentage formula | tenancy-organizacao | VERIFIED | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-003 | Establishment bed total (ativo-scoped) vs occupied-bed total | tenancy-organizacao | DISCREPANCY | RETIRE | — | P2 |
| RULE-TENANCY-ORGANIZACAO-004 | Sector active-bed total vs. occupied-bed total use inconsist | tenancy-organizacao | DISCREPANCY | RETIRE | — | P2 |
| RULE-TENANCY-ORGANIZACAO-005 | Establishment macro-indicator aggregate (sum/avg rounded to  | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-006 | Sector macro-indicator single-record fetch with silent failu | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-007 | Establishment unread message count sums across ALL sectors,  | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-008 | Sector unread message count via Firestore | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-009 | Combined setor display name | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-05](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-010 | 'atualizado_em' timestamp floored to 5-minute buckets | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-06](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-011 | Sector alert counts merge manual movement alerts with automa | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-07](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-012 | Sector bed totals (active beds only) | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-08](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-013 | Sector gender counts merge manual movements with automatic-p | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-09](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-014 | Sector chat preview picks the first related observation with | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-10](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-015 | Monthly total intervention count for sector indicators | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-11](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-016 | Processing-mode (tipo) enumeration for company/bed/sector/es | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-017 | EmpresaMiddleware — path-based empresa (tenant) resolution | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-resolution](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-018 | EstabelecimentoMiddleware — path-based estabelecimento resol | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-resolution](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-019 | SetorMiddleware — path-based setor resolution + dual empresa | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-resolution](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-020 | LeitoMiddleware — path-based leito resolution (no cross-tena | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-TENANCY-ORGANIZACAO-021 | Sector queryset dual (non-exclusive) scoping by empresa and  | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-resolution](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-022 | Establishment queryset optionally scoped to parent empresa | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-resolution](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-023 | Cascading estabelecimento-then-setor selection gate | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-024 | GET bypasses can_manage_empresa permission | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §method-scoped-authorization](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-025 | Homecare-only dashboard shortcuts (Feed / Relatório de Evolu | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-026 | Manual-type gates estabelecimento creation | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-027 | Manual-type gates leito creation | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [clinical-forms.md §bed-management-affordances](design/screens/clinical-forms.md) | — |
| RULE-TENANCY-ORGANIZACAO-028 | Manual-type gates setor creation and editing | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenancy-hierarchy](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-029 | Establishment gender/alert/assisted totals branch by tipo (m | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §tenant-scoped-aggregation](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-030 | Establishment total assisted patients branches by tipo | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §tenant-scoped-aggregation](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-031 | Establishment action_fields expose camera credentials only o | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §field-level-exposure-gating](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-032 | Establishment destroy() blocked while any bed has an active  | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §deletion-safety-guards](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-033 | Establishment chats action lists only sectors the user belon | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-context-required](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-034 | Sector patient/gender totals branch by tipo (manual vs. auto | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §tenant-scoped-aggregation](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-035 | Sector total alert counts branch by tipo | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §tenant-scoped-aggregation](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-036 | Sector total assisted-patient count branches by tipo (manual | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §tenant-scoped-aggregation](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-037 | Sector destroy() blocked while any bed has an active occupat | tenancy-organizacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-01](RATIFICATION.md) | P3 |
| RULE-TENANCY-ORGANIZACAO-038 | Sector clinical indicator aggregation across care pathways ( | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-02](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-039 | Company owner (proprietario) access lifecycle on save | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §user-provisioning](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-040 | Company logo base64 conversion on update | tenancy-organizacao | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TENANCY-ORGANIZACAO-041 | Company-wide indicadores action scopes to user's establishme | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-03](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-042 | Establishment indicadores action scopes movimentacoes and se | tenancy-organizacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TENANCY-ORGANIZACAO-043 | Auto-refresh polling interval driven by company setting (emp | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §realtime-dashboard-updates](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-044 | Auto-refresh polling interval driven by company setting (est | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [alert-engine.md §realtime-dashboard-updates](architecture/alert-engine.md) | — |
| RULE-TENANCY-ORGANIZACAO-045 | Access-group exactly-one-scope constraint (three_xor) | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §scope-exclusivity](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-046 | Grupo/estabelecimento-scoped member search | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [clinical-forms.md §access-group-member-search](design/screens/clinical-forms.md) | — |
| RULE-TENANCY-ORGANIZACAO-047 | Whitelabel brand enumeration (unique per company) | tenancy-organizacao | NOT_APPLICABLE | ADOPT | [security-lgpd.md §tenant-config](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-048 | Company field constraints (primary color length, refresh int | tenancy-organizacao | NOT_APPLICABLE | ADOPT-CORRECTED | [security-lgpd.md §tenant-config](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-049 | Company logo field rename with silent drop for non-string va | tenancy-organizacao | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-tenancy-organizacao-05](RATIFICATION.md) | P3 |
| RULE-TENANCY-ORGANIZACAO-050 | UndefinedMiddleware — reject literal 'undefined' in URL path | tenancy-organizacao | NOT_APPLICABLE | ADAPT | [security-lgpd.md §login-input-validation](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-051 | AcaoHomecare tenant scoping | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-context-required](architecture/security-lgpd.md) | — |
| RULE-TENANCY-ORGANIZACAO-052 | Multi-tenant data scoping by sector/establishment | tenancy-organizacao | NOT_APPLICABLE | SUPERSEDE | [security-lgpd.md §tenant-context-required](architecture/security-lgpd.md) | — |
| RULE-TRILHAS-ENGINE-001 | Automatic-bed pathway composition (v3 + v2 model sets) | trilhas-engine | NOT_APPLICABLE | SUPERSEDE | [correlation-engine.md §domain-routing](clinical/domains/correlation-engine.md) | P3 |
| RULE-TRILHAS-ENGINE-002 | Homecare-bed pathway composition | trilhas-engine | NOT_APPLICABLE | SUPERSEDE | [early-warning-scores.md §care-context-scoping](clinical/domains/early-warning-scores.md) | — |
| RULE-TRILHAS-ENGINE-003 | get_trilha leito-type dispatch | trilhas-engine | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-trilhas-engine-01](RATIFICATION.md) | AMBIGUOUS |
| RULE-TRILHAS-ENGINE-004 | Pathway alert-status color precedence | trilhas-engine | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TRILHAS-ENGINE-005 | Interactive care-pathway eligibility (Sepse / Profilaxia) | trilhas-engine | NOT_APPLICABLE | SUPERSEDE | [sepsis.md §protocol-response-workflow](clinical/domains/sepsis.md) | — |
| RULE-TRILHAS-ENGINE-006 | Interactive pathway restricted to automatic bed type | trilhas-engine | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TRILHAS-ENGINE-007 | Mark-pathway-assisted eligibility and own-record authorizati | trilhas-engine | NOT_APPLICABLE | ADAPT | [security-lgpd.md §alert-acknowledgment-ownership](architecture/security-lgpd.md) | — |
| RULE-TRILHAS-ENGINE-008 | Pathway overdue-item alert | trilhas-engine | NOT_APPLICABLE | ADAPT | [sepsis.md §bundle-overdue-alert](clinical/domains/sepsis.md) | — |
| RULE-TRILHAS-ENGINE-009 | Care-pathway catalog and criteria counts | trilhas-engine | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TRILHAS-ENGINE-010 | Automatica facade — active payload variant selection per tri | trilhas-engine | NOT_APPLICABLE | RETIRE | — | — |
| RULE-TRILHAS-ENGINE-011 | Manual pathway set created per movimentacao (Estabilidade/Se | trilhas-engine | NOT_APPLICABLE | ADAPT | [correlation-engine.md §admission-triggered-domains](clinical/domains/correlation-engine.md) | — |
| RULE-TRILHAS-ENGINE-012 | AtualizarTrilhasV3 — v3 care-pathway bootstrap and bed re-li | trilhas-engine | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-trilhas-engine-02](RATIFICATION.md) | AMBIGUOUS |
| RULE-TRILHAS-ENGINE-013 | Trilha name humanization (6-char prefix split) | trilhas-engine | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-TRILHAS-ENGINE-014 | Accept interactive protocol workflow | trilhas-engine | NOT_APPLICABLE | SUPERSEDE | [sepsis.md §protocol-response-workflow](clinical/domains/sepsis.md) | — |
| RULE-TRILHAS-ENGINE-015 | Refuse interactive protocol workflow (justification required | trilhas-engine | NOT_APPLICABLE | RATIFY | [RATIFICATION.md §rat-trilhas-engine-03](RATIFICATION.md) | AMBIGUOUS |
| RULE-TRILHAS-ENGINE-016 | Criterion recommendations and interventions rendering | trilhas-engine | NOT_APPLICABLE | ADAPT | [clinical-forms.md §recommendation-list](design/screens/clinical-forms.md) | — |
| RULE-TRILHAS-ENGINE-017 | Per-criterion drug-dosing reference image | trilhas-engine | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-trilhas-engine-04](RATIFICATION.md) | UNVERIFIABLE |
| RULE-TRILHAS-ENGINE-018 | Care-pathway type enumeration (AssistidoChoices vs Observaca | trilhas-engine | NOT_APPLICABLE | ADOPT-CORRECTED | [clinical-forms.md §trilha-tipo-enum](design/screens/clinical-forms.md) | P3 |
| RULE-VENTILACAO-001 | Predicted body weight and protective tidal volume (VC 4/5/6  | ventilacao | VERIFIED | ADOPT | [respiratory.md §pbw-tidal-volume-targets](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-002 | Days on mechanical ventilation (buscar_dias_com_ventilacao_m | ventilacao | UNVERIFIABLE | RATIFY | [RATIFICATION.md §rat-ventilacao-01](RATIFICATION.md) | UNVERIFIABLE |
| RULE-VENTILACAO-003 | Ventilation C1 - high inspiratory pressure or tidal volume | ventilacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-ventilacao-02](RATIFICATION.md) | P1 |
| RULE-VENTILACAO-004 | Ventilation C2 - FiO2xPEEP mismatch with moderate hypoxemia | ventilacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-ventilacao-03](RATIFICATION.md) | P1 |
| RULE-VENTILACAO-005 | Ventilation C3 - FiO2xPEEP mismatch with severe hypoxemia | ventilacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-ventilacao-04](RATIFICATION.md) | P1 |
| RULE-VENTILACAO-006 | Ventilation C2/C3 previous-version FiO2->PEEP table (peep_ol | ventilacao | DISCREPANCY | RETIRE | — | P3 |
| RULE-VENTILACAO-007 | Ventilation C4 - weaning readiness / consciousness | ventilacao | DISCREPANCY | ADAPT | [respiratory.md §weaning-readiness](clinical/domains/respiratory.md) | P2 |
| RULE-VENTILACAO-008 | Ventilation C5 - prolonged intubation (>10 days TOT) | ventilacao | VERIFIED | ADOPT | [respiratory.md §prolonged-intubation-tracheostomy](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-009 | Ventilation C6 - prolonged intubation with COVID-19 | ventilacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-ventilacao-05](RATIFICATION.md) | P1 |
| RULE-VENTILACAO-010 | Ventilation C7 - severe hypoxemia early in admission | ventilacao | VERIFIED | ADOPT | [correlation-engine.md §ards-shock](clinical/domains/correlation-engine.md) | — |
| RULE-VENTILACAO-011 | Ventilation C8 - extubation-readiness bundle | ventilacao | DISCREPANCY | RATIFY | [RATIFICATION.md §rat-ventilacao-06](RATIFICATION.md) | P0 |
| RULE-VENTILACAO-012 | Ventilation C9 - shock without ventilation | ventilacao | DISCREPANCY | ADOPT-CORRECTED | [correlation-engine.md §shock-without-ventilation](clinical/domains/correlation-engine.md) | P2 |
| RULE-VENTILACAO-013 | Ventilation C10 - adequate oxygenation (incl. COPD target) | ventilacao | VERIFIED | ADOPT | [respiratory.md §oxygenation-targets](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-014 | Ventilation pathway alert (count + special-criterion overrid | ventilacao | NOT_APPLICABLE | ADAPT | [respiratory.md §alert-aggregation](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-015 | Ventilacao v1 alert (used - calcular_alerta_v2, trilha_autom | ventilacao | NOT_APPLICABLE | SUPERSEDE | [respiratory.md §alert-aggregation](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-016 | Ventilacao v1 alert (unused legacy - calcular_alerta, trilha | ventilacao | NOT_APPLICABLE | RETIRE | — | AMBIGUOUS |
| RULE-VENTILACAO-017 | Ventilation/weaning facade protocol (ventilacao_automatica)  | ventilacao | VERIFIED | ADOPT | [respiratory.md §weaning-and-lung-protective-protocol](clinical/domains/respiratory.md) | — |
| RULE-VENTILACAO-018 | Ventilator parameter validation ranges (movimentacao form) | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilator-parameter-bounds](design/screens/clinical-forms.md) | — |
| RULE-VENTILACAO-019 | Physician respiratory-assessment ventilation decision tree ( | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilation-type-selector](design/screens/clinical-forms.md) | — |
| RULE-VENTILACAO-020 | Physiotherapy ventilation decision tree with divergent press | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilator-parameter-bounds](design/screens/clinical-forms.md) | P3 |
| RULE-VENTILACAO-021 | Supplemental O2 flow valid range 1-15 L/min (homecare) | ventilacao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §supplemental-o2-flow](design/screens/clinical-forms.md) | — |
| RULE-VENTILACAO-022 | PEEP (pressao expiratoria pulmonar) valid range 5-18 (homeca | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilator-parameter-bounds](design/screens/clinical-forms.md) | — |
| RULE-VENTILACAO-023 | Inspiratory pressure valid range 5-40 (homecare) | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilator-parameter-bounds](design/screens/clinical-forms.md) | — |
| RULE-VENTILACAO-024 | Ventilation-mode string classification lists (get_ventilacao | ventilacao | NOT_APPLICABLE | SUPERSEDE | [clinical-forms.md §ventilation-type-selector](design/screens/clinical-forms.md) | P3 |
| RULE-VENTILACAO-025 | VentilacaoMecanica ventilation / device / modality enumerati | ventilacao | NOT_APPLICABLE | ADAPT | [clinical-forms.md §ventilation-device-modality-enums](design/screens/clinical-forms.md) | P3 |
| RULE-VENTILACAO-026 | Nursing ventilation / secretion assessment enums (avaliacao_ | ventilacao | NOT_APPLICABLE | ADOPT | [clinical-forms.md §respiratory-assessment-enums](design/screens/clinical-forms.md) | — |

## Escalations (351)

| Item | Band | Rule | Outcome | Where |
|---|---|---|---|---|
| ESC-ADDENDUM-349 | ADDENDUM | RULE-SEPSE-099 | RATIFY | RATIFICATION.md |
| ESC-ADDENDUM-350 | ADDENDUM | RULE-AUTH-USUARIOS-063 | RATIFY | RATIFICATION.md |
| ESC-ADDENDUM-351 | ADDENDUM | RULE-DOCUMENTACAO-FATURAMENTO-032 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-293 | AMBIGUOUS | RULE-ALERTAS-014 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-294 | AMBIGUOUS | RULE-ALERTAS-025 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-295 | AMBIGUOUS | RULE-ANTIMICROBIANO-002 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-296 | AMBIGUOUS | RULE-VENTILACAO-016 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-297 | AMBIGUOUS | RULE-BALANCO-HIDRICO-045 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-298 | AMBIGUOUS | RULE-EVOLUCOES-011 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-299 | AMBIGUOUS | RULE-EVOLUCOES-017 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-300 | AMBIGUOUS | RULE-FORMULARIOS-CLINICOS-017 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-301 | AMBIGUOUS | RULE-FORMULARIOS-CLINICOS-037 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-302 | AMBIGUOUS | RULE-PRESCRICAO-028 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-303 | AMBIGUOUS | RULE-PROFILAXIA-008 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-304 | AMBIGUOUS | RULE-SEDACAO-022 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-305 | AMBIGUOUS | RULE-SEPSE-086 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-306 | AMBIGUOUS | RULE-SEPSE-093 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-307 | AMBIGUOUS | RULE-TRILHAS-ENGINE-003 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-308 | AMBIGUOUS | RULE-TRILHAS-ENGINE-012 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-309 | AMBIGUOUS | RULE-TRILHAS-ENGINE-013 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-310 | AMBIGUOUS | RULE-TRILHAS-ENGINE-015 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-311 | AMBIGUOUS | RULE-DOCUMENTACAO-FATURAMENTO-014 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-312 | AMBIGUOUS | RULE-SEPSE-066 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-313 | AMBIGUOUS | RULE-AUDITORIA-LOGS-025 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-314 | AMBIGUOUS | RULE-AUDITORIA-LOGS-028 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-315 | AMBIGUOUS | RULE-AUDITORIA-LOGS-032 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-316 | AMBIGUOUS | RULE-AUDITORIA-LOGS-034 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-317 | AMBIGUOUS | RULE-AUTH-USUARIOS-056 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-318 | AMBIGUOUS | RULE-BALANCO-HIDRICO-062 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-319 | AMBIGUOUS | RULE-CADASTROS-UI-001 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-320 | AMBIGUOUS | RULE-CADASTROS-UI-005 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-321 | AMBIGUOUS | RULE-CADASTROS-UI-006 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-322 | AMBIGUOUS | RULE-COMUNICACAO-041 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-323 | AMBIGUOUS | RULE-COMUNICACAO-045 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-324 | AMBIGUOUS | RULE-DOCUMENTACAO-FATURAMENTO-017 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-325 | AMBIGUOUS | RULE-DOCUMENTACAO-FATURAMENTO-024 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-326 | AMBIGUOUS | RULE-EVOLUCOES-018 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-327 | AMBIGUOUS | RULE-EVOLUCOES-022 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-328 | AMBIGUOUS | RULE-EVOLUCOES-048 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-329 | AMBIGUOUS | RULE-EVOLUCOES-074 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-330 | AMBIGUOUS | RULE-FORMULARIOS-CLINICOS-039 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-331 | AMBIGUOUS | RULE-MOVIMENTACAO-ADT-048 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-332 | AMBIGUOUS | RULE-MOVIMENTACAO-ADT-049 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-333 | AMBIGUOUS | RULE-MOVIMENTACAO-ADT-058 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-334 | AMBIGUOUS | RULE-OPERACIONAL-INFRA-017 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-335 | AMBIGUOUS | RULE-OPERACIONAL-INFRA-037 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-336 | AMBIGUOUS | RULE-PRESCRICAO-036 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-337 | AMBIGUOUS | RULE-SEPSE-068 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-338 | AMBIGUOUS | RULE-SEPSE-098 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-339 | AMBIGUOUS | RULE-SINAIS-VITAIS-033 | RATIFY | RATIFICATION.md |
| ESC-AMBIGUOUS-340 | AMBIGUOUS | RULE-TENANCY-ORGANIZACAO-020 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-341 | AMBIGUOUS | RULE-OPERACIONAL-INFRA-040 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-342 | AMBIGUOUS | RULE-OPERACIONAL-INFRA-059 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-343 | AMBIGUOUS | RULE-AUDITORIA-LOGS-021 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-344 | AMBIGUOUS | RULE-AUDITORIA-LOGS-022 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-345 | AMBIGUOUS | RULE-AUTH-USUARIOS-045 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-346 | AMBIGUOUS | RULE-AUTH-USUARIOS-047 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-347 | AMBIGUOUS | RULE-DOCUMENTACAO-FATURAMENTO-015 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-AMBIGUOUS-348 | AMBIGUOUS | RULE-FORMULARIOS-CLINICOS-040 | RETIRE-RECOMMENDED | traceability (disposition) |
| ESC-P0-001 | P0 | RULE-CLINICAL-SCORING-002 | RATIFY | RATIFICATION.md |
| ESC-P0-002 | P0 | RULE-CLINICAL-SCORING-005 | RATIFY | RATIFICATION.md |
| ESC-P0-003 | P0 | RULE-CLINICAL-SCORING-007 | RATIFY | RATIFICATION.md |
| ESC-P0-004 | P0 | RULE-PIORA-CLINICA-006 | RATIFY | RATIFICATION.md |
| ESC-P0-005 | P0 | RULE-PIORA-CLINICA-007 | RATIFY | RATIFICATION.md |
| ESC-P0-006 | P0 | RULE-ESTABILIDADE-016 | RATIFY | RATIFICATION.md |
| ESC-P0-007 | P0 | RULE-CLINICAL-SCORING-008 | RATIFY | RATIFICATION.md |
| ESC-P0-008 | P0 | RULE-SEPSE-014 | RATIFY | RATIFICATION.md |
| ESC-P0-009 | P0 | RULE-EFICIENCIA-005 | RATIFY | RATIFICATION.md |
| ESC-P0-010 | P0 | RULE-PIORA-CLINICA-010 | RATIFY | RATIFICATION.md |
| ESC-P0-011 | P0 | RULE-VENTILACAO-011 | RATIFY | RATIFICATION.md |
| ESC-P0-012 | P0 | RULE-SEPSE-043 | RATIFY | RATIFICATION.md |
| ESC-P1-013 | P1 | RULE-CLINICAL-SCORING-004 | RATIFY | RATIFICATION.md |
| ESC-P1-014 | P1 | RULE-INDICADORES-ETL-012 | RATIFY | RATIFICATION.md |
| ESC-P1-015 | P1 | RULE-PIORA-CLINICA-008 | RATIFY | RATIFICATION.md |
| ESC-P1-016 | P1 | RULE-PIORA-CLINICA-009 | RATIFY | RATIFICATION.md |
| ESC-P1-017 | P1 | RULE-SEPSE-002 | RATIFY | RATIFICATION.md |
| ESC-P1-018 | P1 | RULE-SEPSE-032 | RATIFY | RATIFICATION.md |
| ESC-P1-019 | P1 | RULE-SEPSE-033 | RATIFY | RATIFICATION.md |
| ESC-P1-020 | P1 | RULE-SEPSE-037 | RATIFY | RATIFICATION.md |
| ESC-P1-021 | P1 | RULE-SEDACAO-009 | RATIFY | RATIFICATION.md |
| ESC-P1-022 | P1 | RULE-BALANCO-HIDRICO-006 | RATIFY | RATIFICATION.md |
| ESC-P1-023 | P1 | RULE-BALANCO-HIDRICO-007 | RATIFY | RATIFICATION.md |
| ESC-P1-024 | P1 | RULE-BALANCO-HIDRICO-008 | RATIFY | RATIFICATION.md |
| ESC-P1-025 | P1 | RULE-BALANCO-HIDRICO-010 | RATIFY | RATIFICATION.md |
| ESC-P1-026 | P1 | RULE-BALANCO-HIDRICO-013 | RATIFY | RATIFICATION.md |
| ESC-P1-027 | P1 | RULE-BALANCO-HIDRICO-016 | RATIFY | RATIFICATION.md |
| ESC-P1-028 | P1 | RULE-ESTABILIDADE-001 | RATIFY | RATIFICATION.md |
| ESC-P1-029 | P1 | RULE-INDICADORES-ETL-004 | RATIFY | RATIFICATION.md |
| ESC-P1-030 | P1 | RULE-EFICIENCIA-006 | RATIFY | RATIFICATION.md |
| ESC-P1-031 | P1 | RULE-ESTABILIDADE-005 | RATIFY | RATIFICATION.md |
| ESC-P1-032 | P1 | RULE-ESTABILIDADE-007 | RATIFY | RATIFICATION.md |
| ESC-P1-033 | P1 | RULE-ESTABILIDADE-008 | RATIFY | RATIFICATION.md |
| ESC-P1-034 | P1 | RULE-ESTABILIDADE-009 | RATIFY | RATIFICATION.md |
| ESC-P1-035 | P1 | RULE-ESTABILIDADE-015 | RATIFY | RATIFICATION.md |
| ESC-P1-036 | P1 | RULE-SEPSE-007 | RATIFY | RATIFICATION.md |
| ESC-P1-037 | P1 | RULE-SEPSE-009 | RATIFY | RATIFICATION.md |
| ESC-P1-038 | P1 | RULE-SEPSE-015 | RATIFY | RATIFICATION.md |
| ESC-P1-039 | P1 | RULE-SEPSE-016 | RATIFY | RATIFICATION.md |
| ESC-P1-040 | P1 | RULE-SEPSE-017 | RATIFY | RATIFICATION.md |
| ESC-P1-041 | P1 | RULE-SEPSE-019 | RATIFY | RATIFICATION.md |
| ESC-P1-042 | P1 | RULE-SEPSE-020 | RATIFY | RATIFICATION.md |
| ESC-P1-043 | P1 | RULE-SEPSE-021 | RATIFY | RATIFICATION.md |
| ESC-P1-044 | P1 | RULE-SEPSE-058 | RATIFY | RATIFICATION.md |
| ESC-P1-045 | P1 | RULE-SINAIS-VITAIS-004 | RATIFY | RATIFICATION.md |
| ESC-P1-046 | P1 | RULE-ESTABILIDADE-017 | RATIFY | RATIFICATION.md |
| ESC-P1-047 | P1 | RULE-ESTABILIDADE-024 | RATIFY | RATIFICATION.md |
| ESC-P1-048 | P1 | RULE-NUTRICAO-003 | RATIFY | RATIFICATION.md |
| ESC-P1-049 | P1 | RULE-PROFILAXIA-005 | RATIFY | RATIFICATION.md |
| ESC-P1-050 | P1 | RULE-SEPSE-060 | RATIFY | RATIFICATION.md |
| ESC-P1-051 | P1 | RULE-VENTILACAO-003 | RATIFY | RATIFICATION.md |
| ESC-P1-052 | P1 | RULE-VENTILACAO-004 | RATIFY | RATIFICATION.md |
| ESC-P1-053 | P1 | RULE-VENTILACAO-005 | RATIFY | RATIFICATION.md |
| ESC-P1-054 | P1 | RULE-VENTILACAO-009 | RATIFY | RATIFICATION.md |
| ESC-P1-055 | P1 | RULE-EFICIENCIA-002 | RATIFY | RATIFICATION.md |
| ESC-P1-056 | P1 | RULE-EFICIENCIA-004 | RATIFY | RATIFICATION.md |
| ESC-P1-057 | P1 | RULE-SEPSE-044 | RATIFY | RATIFICATION.md |
| ESC-P2-058 | P2 | RULE-CLINICAL-SCORING-014 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P2-059 | P2 | RULE-EVOLUCOES-003 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-060 | P2 | RULE-FORMULARIOS-CLINICOS-002 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-061 | P2 | RULE-FORMULARIOS-CLINICOS-003 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-062 | P2 | RULE-PIORA-CLINICA-002 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-063 | P2 | RULE-PIORA-CLINICA-004 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-064 | P2 | RULE-SEPSE-030 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-065 | P2 | RULE-SEPSE-035 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-066 | P2 | RULE-EQUILIBRIO-004 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-067 | P2 | RULE-SEDACAO-008 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-068 | P2 | RULE-SEPSE-061 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-069 | P2 | RULE-BALANCO-HIDRICO-009 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-070 | P2 | RULE-BALANCO-HIDRICO-011 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-071 | P2 | RULE-CLINICAL-SCORING-010 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-072 | P2 | RULE-TENANCY-ORGANIZACAO-003 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P2-073 | P2 | RULE-TENANCY-ORGANIZACAO-004 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P2-074 | P2 | RULE-ESTABILIDADE-011 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-075 | P2 | RULE-FORMULARIOS-CLINICOS-004 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-076 | P2 | RULE-FORMULARIOS-CLINICOS-005 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-077 | P2 | RULE-NUTRICAO-005 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-078 | P2 | RULE-SEPSE-003 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P2-079 | P2 | RULE-SEPSE-013 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-080 | P2 | RULE-ESTABILIDADE-019 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-081 | P2 | RULE-ESTABILIDADE-020 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-082 | P2 | RULE-SEPSE-059 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-083 | P2 | RULE-VENTILACAO-007 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-084 | P2 | RULE-VENTILACAO-012 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-085 | P2 | RULE-EFICIENCIA-003 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-086 | P2 | RULE-NUTRICAO-006 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P2-087 | P2 | RULE-SEPSE-042 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-088 | P2 | RULE-SEPSE-048 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-089 | P2 | RULE-SEPSE-050 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-090 | P2 | RULE-SEPSE-054 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P2-091 | P2 | RULE-MOVIMENTACAO-ADT-009 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P2-092 | P2 | RULE-OPERACIONAL-INFRA-001 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-093 | P3 | RULE-BALANCO-HIDRICO-019 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-094 | P3 | RULE-CLINICAL-SCORING-017 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-095 | P3 | RULE-EFICIENCIA-010 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-096 | P3 | RULE-SEDACAO-003 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-097 | P3 | RULE-SEDACAO-004 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-098 | P3 | RULE-BALANCO-HIDRICO-058 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-099 | P3 | RULE-SEDACAO-011 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-100 | P3 | RULE-SINAIS-VITAIS-031 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-101 | P3 | RULE-BALANCO-HIDRICO-022 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-102 | P3 | RULE-ALERTAS-003 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-103 | P3 | RULE-BALANCO-HIDRICO-025 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-104 | P3 | RULE-ESTABILIDADE-012 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-105 | P3 | RULE-ESTABILIDADE-013 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-106 | P3 | RULE-INDICADORES-ETL-007 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-107 | P3 | RULE-NUTRICAO-004 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-108 | P3 | RULE-PRESCRICAO-002 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-109 | P3 | RULE-PRESCRICAO-003 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-110 | P3 | RULE-SEPSE-095 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-111 | P3 | RULE-SINAIS-VITAIS-005 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-112 | P3 | RULE-BALANCO-HIDRICO-026 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-113 | P3 | RULE-BALANCO-HIDRICO-035 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-114 | P3 | RULE-BALANCO-HIDRICO-043 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-115 | P3 | RULE-COMUNICACAO-026 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-116 | P3 | RULE-EVOLUCOES-025 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-117 | P3 | RULE-EVOLUCOES-029 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-118 | P3 | RULE-EVOLUCOES-030 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-119 | P3 | RULE-FORMULARIOS-CLINICOS-038 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-120 | P3 | RULE-INDICADORES-ETL-016 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-121 | P3 | RULE-MOVIMENTACAO-ADT-036 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-122 | P3 | RULE-OPERACIONAL-INFRA-019 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-123 | P3 | RULE-PRESCRICAO-014 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-124 | P3 | RULE-SEDACAO-016 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-125 | P3 | RULE-SEPSE-073 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-126 | P3 | RULE-SEPSE-079 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-127 | P3 | RULE-TENANCY-ORGANIZACAO-037 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-128 | P3 | RULE-TRILHAS-ENGINE-001 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-129 | P3 | RULE-TRILHAS-ENGINE-018 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-130 | P3 | RULE-VENTILACAO-006 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-131 | P3 | RULE-VENTILACAO-020 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-132 | P3 | RULE-VENTILACAO-024 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-133 | P3 | RULE-AUTH-USUARIOS-020 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-134 | P3 | RULE-AUTH-USUARIOS-021 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-135 | P3 | RULE-AUTH-USUARIOS-022 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-136 | P3 | RULE-AUTH-USUARIOS-030 | RESOLVED-BY-DISPOSITION (SUPERSEDE) | traceability (disposition) |
| ESC-P3-137 | P3 | RULE-EFICIENCIA-008 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-138 | P3 | RULE-EFICIENCIA-011 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-139 | P3 | RULE-AUDITORIA-LOGS-009 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-140 | P3 | RULE-AUDITORIA-LOGS-010 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-141 | P3 | RULE-AUDITORIA-LOGS-012 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-142 | P3 | RULE-AUDITORIA-LOGS-013 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-143 | P3 | RULE-AUDITORIA-LOGS-014 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-144 | P3 | RULE-AUDITORIA-LOGS-024 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-145 | P3 | RULE-AUDITORIA-LOGS-026 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-146 | P3 | RULE-AUDITORIA-LOGS-030 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-147 | P3 | RULE-AUDITORIA-LOGS-031 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-148 | P3 | RULE-AUTH-USUARIOS-051 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-149 | P3 | RULE-AUTH-USUARIOS-052 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-150 | P3 | RULE-AUTH-USUARIOS-053 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-151 | P3 | RULE-BALANCO-HIDRICO-051 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-152 | P3 | RULE-BALANCO-HIDRICO-061 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-153 | P3 | RULE-CADASTROS-UI-016 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-154 | P3 | RULE-COMUNICACAO-034 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-155 | P3 | RULE-COMUNICACAO-035 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-156 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-008 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-157 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-021 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-158 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-022 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-159 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-023 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-160 | P3 | RULE-EVOLUCOES-023 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-161 | P3 | RULE-EVOLUCOES-057 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-162 | P3 | RULE-EVOLUCOES-062 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-163 | P3 | RULE-EVOLUCOES-065 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-164 | P3 | RULE-EVOLUCOES-075 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-165 | P3 | RULE-FORMULARIOS-CLINICOS-021 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-166 | P3 | RULE-INDICADORES-ETL-019 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-167 | P3 | RULE-INDICADORES-ETL-027 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-168 | P3 | RULE-MOVIMENTACAO-ADT-066 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-169 | P3 | RULE-MOVIMENTACAO-ADT-069 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-170 | P3 | RULE-OPERACIONAL-INFRA-018 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-171 | P3 | RULE-OPERACIONAL-INFRA-021 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-172 | P3 | RULE-OPERACIONAL-INFRA-032 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-173 | P3 | RULE-OPERACIONAL-INFRA-036 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-174 | P3 | RULE-OPERACIONAL-INFRA-056 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-175 | P3 | RULE-PRESCRICAO-029 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-176 | P3 | RULE-PRESCRICAO-035 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-177 | P3 | RULE-PRESCRICAO-037 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-178 | P3 | RULE-PRESCRICAO-040 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-179 | P3 | RULE-SINAIS-VITAIS-006 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-180 | P3 | RULE-TENANCY-ORGANIZACAO-049 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-181 | P3 | RULE-VENTILACAO-025 | RESOLVED-BY-DISPOSITION (ADAPT) | traceability (disposition) |
| ESC-P3-182 | P3 | RULE-OPERACIONAL-INFRA-014 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-183 | P3 | RULE-OPERACIONAL-INFRA-026 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-184 | P3 | RULE-OPERACIONAL-INFRA-031 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-185 | P3 | RULE-OPERACIONAL-INFRA-047 | RESOLVED-BY-DISPOSITION (RATIFY) | RATIFICATION.md |
| ESC-P3-186 | P3 | RULE-PRESCRICAO-007 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-187 | P3 | RULE-PRESCRICAO-027 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-188 | P3 | RULE-AUTH-USUARIOS-044 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-189 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-002 | RESOLVED-BY-DISPOSITION (RETIRE) | traceability (disposition) |
| ESC-P3-190 | P3 | RULE-DOCUMENTACAO-FATURAMENTO-020 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-P3-191 | P3 | RULE-AUTH-USUARIOS-007 | RESOLVED-BY-DISPOSITION (ADOPT-CORRECTED) | traceability (disposition) |
| ESC-UNVERIFIABLE-192 | UNVERIFIABLE | RULE-SEPSE-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-193 | UNVERIFIABLE | RULE-SEPSE-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-194 | UNVERIFIABLE | RULE-SEPSE-029 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-195 | UNVERIFIABLE | RULE-SEPSE-036 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-196 | UNVERIFIABLE | RULE-SEPSE-006 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-197 | UNVERIFIABLE | RULE-SEPSE-004 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-198 | UNVERIFIABLE | RULE-SEPSE-023 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-199 | UNVERIFIABLE | RULE-SEPSE-024 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-200 | UNVERIFIABLE | RULE-SEPSE-025 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-201 | UNVERIFIABLE | RULE-SEPSE-026 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-202 | UNVERIFIABLE | RULE-SEPSE-040 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-203 | UNVERIFIABLE | RULE-SEPSE-041 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-204 | UNVERIFIABLE | RULE-SEPSE-053 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-205 | UNVERIFIABLE | RULE-SEPSE-055 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-206 | UNVERIFIABLE | RULE-SEPSE-056 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-207 | UNVERIFIABLE | RULE-SEPSE-057 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-208 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-209 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-006 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-210 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-015 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-211 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-038 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-212 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-041 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-213 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-042 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-214 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-012 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-215 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-007 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-216 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-008 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-217 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-011 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-218 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-009 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-219 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-220 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-013 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-221 | UNVERIFIABLE | RULE-TENANCY-ORGANIZACAO-014 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-222 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-059 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-223 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-056 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-224 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-057 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-225 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-004 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-226 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-227 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-012 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-228 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-017 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-229 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-018 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-230 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-020 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-231 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-021 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-232 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-023 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-233 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-024 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-234 | UNVERIFIABLE | RULE-BALANCO-HIDRICO-028 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-235 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-003 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-236 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-237 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-009 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-238 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-239 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-011 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-240 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-004 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-241 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-242 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-006 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-243 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-007 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-244 | UNVERIFIABLE | RULE-OPERACIONAL-INFRA-008 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-245 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-246 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-003 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-247 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-248 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-249 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-011 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-250 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-006 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-251 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-007 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-252 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-008 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-253 | UNVERIFIABLE | RULE-MOVIMENTACAO-ADT-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-254 | UNVERIFIABLE | RULE-SEDACAO-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-255 | UNVERIFIABLE | RULE-SEDACAO-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-256 | UNVERIFIABLE | RULE-SEDACAO-013 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-257 | UNVERIFIABLE | RULE-SEDACAO-025 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-258 | UNVERIFIABLE | RULE-SEDACAO-026 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-259 | UNVERIFIABLE | RULE-SEDACAO-018 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-260 | UNVERIFIABLE | RULE-SEDACAO-019 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-261 | UNVERIFIABLE | RULE-SEDACAO-020 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-262 | UNVERIFIABLE | RULE-EVOLUCOES-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-263 | UNVERIFIABLE | RULE-EVOLUCOES-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-264 | UNVERIFIABLE | RULE-EVOLUCOES-004 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-265 | UNVERIFIABLE | RULE-EVOLUCOES-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-266 | UNVERIFIABLE | RULE-PIORA-CLINICA-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-267 | UNVERIFIABLE | RULE-PIORA-CLINICA-003 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-268 | UNVERIFIABLE | RULE-PIORA-CLINICA-005 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-269 | UNVERIFIABLE | RULE-PIORA-CLINICA-011 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-270 | UNVERIFIABLE | RULE-COMUNICACAO-003 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-271 | UNVERIFIABLE | RULE-COMUNICACAO-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-272 | UNVERIFIABLE | RULE-COMUNICACAO-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-273 | UNVERIFIABLE | RULE-INDICADORES-ETL-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-274 | UNVERIFIABLE | RULE-INDICADORES-ETL-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-275 | UNVERIFIABLE | RULE-INDICADORES-ETL-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-276 | UNVERIFIABLE | RULE-ALERTAS-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-277 | UNVERIFIABLE | RULE-ALERTAS-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-278 | UNVERIFIABLE | RULE-AUTH-USUARIOS-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-279 | UNVERIFIABLE | RULE-AUTH-USUARIOS-002 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-280 | UNVERIFIABLE | RULE-DOCUMENTACAO-FATURAMENTO-027 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-281 | UNVERIFIABLE | RULE-DOCUMENTACAO-FATURAMENTO-028 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-282 | UNVERIFIABLE | RULE-ESTABILIDADE-010 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-283 | UNVERIFIABLE | RULE-ESTABILIDADE-022 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-284 | UNVERIFIABLE | RULE-FORMULARIOS-CLINICOS-014 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-285 | UNVERIFIABLE | RULE-FORMULARIOS-CLINICOS-042 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-286 | UNVERIFIABLE | RULE-SINAIS-VITAIS-029 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-287 | UNVERIFIABLE | RULE-SINAIS-VITAIS-030 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-288 | UNVERIFIABLE | RULE-AUDITORIA-LOGS-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-289 | UNVERIFIABLE | RULE-EFICIENCIA-009 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-290 | UNVERIFIABLE | RULE-PRESCRICAO-001 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-291 | UNVERIFIABLE | RULE-TRILHAS-ENGINE-017 | RATIFY | RATIFICATION.md |
| ESC-UNVERIFIABLE-292 | UNVERIFIABLE | RULE-VENTILACAO-002 | RATIFY | RATIFICATION.md |

## Legacy design ADRs (18)

| ADR | Title | Disposition | Target |
|---|---|---|---|
| 0001 | Frontend stack and UI library | SUPERSEDE | design/frontend-architecture.md#stack |
| 0002 | Dark-first compact base theme | ADOPT | design/design-tokens.md#theme-modes |
| 0003 | Light mode client overlay | SUPERSEDE | design/design-tokens.md#theme-switching |
| 0004 | Per-tenant white-label runtime color | ADOPT | design/design-tokens.md#tenant-branding |
| 0005 | Design token source of truth and governance | ADOPT | design/design-tokens.md#governance |
| 0006 | No formal token scales | ADOPT | design/design-tokens.md#formal-scales |
| 0007 | Neumorphic elevation visual signature | ADAPT | design/design-tokens.md#elevation |
| 0008 | PageContainer app shell cascading refetch | ADAPT | design/frontend-architecture.md#app-shell |
| 0009 | Information architecture — no persistent nav | ADOPT | design/information-architecture.md#navigation |
| 0010 | Drawer-in-drawer secondary view pattern | ADOPT | design/frontend-architecture.md#overlay-stack |
| 0011 | JS window-width responsive strategy | ADAPT | design/design-tokens.md#responsive-breakpoints |
| 0012 | Canonical primitives vs parallel implementations | ADOPT | design/component-library.md#canonical-primitives |
| 0013 | Clinical severity color system | ADAPT | design/design-tokens.md#clinical-severity |
| 0014 | No abnormal-value threshold flagging | ADOPT | design/clinical-ux.md#abnormal-value-flagging |
| 0015 | Config-driven dynamic clinical form engine | ADAPT | design/form-engine.md#schema-driven-engine |
| 0016 | Feedback and loading patterns | ADOPT | design/frontend-architecture.md#feedback-patterns |
| 0017 | Fragmented real-time architecture | ADOPT | design/frontend-architecture.md#realtime-transport |
| 0018 | Client integration and authorization model | ADAPT | design/frontend-architecture.md#auth-integration |

## Vision-item coverage

| Vision item | Covered by |
|---|---|
| vision §3.1 — Infecção e Detecção de Sepse (SIRS / qSOFA / lactato; priority P1) | clinical/domains/sepsis.md#1-clinical-scope, clinical/domains/sepsis.md#3-trigger--staging-logic |
| vision §3.2 — Injúria Renal Aguda / AKI (KDIGO staging; priority P2) | clinical/domains/aki.md#1-clinical-scope, clinical/domains/aki.md#3-kdigo-staging-engine |
| vision §3.3 — Insuficiência Respiratória (SpO2/FiO2, Berlin ARDS; priority P5) | clinical/domains/respiratory.md#1-clinical-scope, clinical/domains/respiratory.md#3-trigger--staging-logic |
| vision §3.4 — Instabilidade Hemodinâmica (shock index, lactate clearance, vasopressor; priority P4) | clinical/domains/hemodynamics.md#1-clinical-scope, clinical/domains/hemodynamics.md#3-trigger--staging-logic |
| vision §3.5 — Delirium / Sedação (CAM-ICU, RASS; priority P7) — neuro-sedation domain | clinical/domains/neuro-sedation.md#1-clinical-scope, clinical/domains/neuro-sedation.md#3-trigger--staging-logic |
| vision §3.6 — Emergências Eletrolíticas (K/Na/Ca/Mg critical bands; priority P3) | clinical/domains/electrolyte.md#1-clinical-scope, clinical/domains/electrolyte.md#3-trigger--staging-logic-evidence-anchored |
| vision §3.7 — Interações Medicamentosas via EMR (QTc, serotonin, CNS, renal-dose; priority P6) | clinical/domains/pharmaco-interaction.md#1-clinical-scope, clinical/domains/pharmaco-interaction.md#4-alerts--trigger--staging-logic-with-evidence |
| vision §4.1 — Correlation Engine (Sepsis+AKI, Respiratory+Hemodynamic, Drug+Electrolyte; VIS-4-03) | clinical/domains/correlation-engine.md#1-clinical-scope, clinical/domains/correlation-engine.md#4-causal-chains--triggerstaging-logic-typed-unit-checked |
| vision §5 — Priorização de Implementação (P1-P7 impact/feasibility + Fase 2a-2d cronograma) | product/product-spec.md#2-user-stories-moscow |
| vision §6 — Desenho de Estudos Clínicos (§6.1 before-after observational; §6.2 stepped-wedge cluster RCT) | delivery/validation-plan.md#1-study-1--before-after-observational-study-quality-improvement-phase, delivery/validation-plan.md#2-study-2--stepped-wedge-cluster-randomized-controlled-trial-confirmatory, delivery/regulatory-plan.md#3-clinical-evaluation-plan-aligned-to-vision-6 |
| vision §7.1 metric VIS-7.1-01 — Sensibilidade para sepse (<1h): 45% -> >=80% | product/product-spec.md#32-vision-71-clinical-metrics, delivery/validation-plan.md#3-metrics-instrumentation-table |
| vision §7.1 metric VIS-7.1-02 — PPV dos alertas (acionáveis/total): 35% -> >=60% | product/product-spec.md#32-vision-71-clinical-metrics, delivery/validation-plan.md#3-metrics-instrumentation-table |
| vision §7.1 metric VIS-7.1-03 — Tempo médio até ação clínica pós-alerta: 42min -> <=15min | product/product-spec.md#32-vision-71-clinical-metrics, delivery/validation-plan.md#3-metrics-instrumentation-table |
| vision §7.1 metric VIS-7.1-04 — Taxa de alarm fatigue (ignorados/total): 25% -> <=10% | product/product-spec.md#32-vision-71-clinical-metrics, delivery/validation-plan.md#3-metrics-instrumentation-table |
| vision §7.1 metric VIS-7.1-05 — Redução de mortalidade em UTI: -10% relativo | product/product-spec.md#32-vision-71-clinical-metrics, delivery/validation-plan.md#3-metrics-instrumentation-table |
| vision §7.2 metric VIS-7.2-01 — Latência ingestão -> alerta (p95) < 30s | product/product-spec.md#33-vision-72-technical-metrics, architecture/observability-slo.md#3-stage-decomposed-latency-budget-barrier-c3-input |
| vision §7.2 metric VIS-7.2-02 — Disponibilidade da plataforma 99,9% | product/product-spec.md#33-vision-72-technical-metrics, architecture/observability-slo.md#2-slo-catalog--mvp-vs-production |
| vision §7.2 metric VIS-7.2-03 — Throughput de processamento > 500 alertas/min | product/product-spec.md#33-vision-72-technical-metrics, architecture/observability-slo.md#6-capacity-model-30--90-beds--multi-hospital |
| vision §7.2 metric VIS-7.2-04 — Retenção de dados (TimescaleDB) 7 anos (LGPD/CFM) | product/product-spec.md#33-vision-72-technical-metrics, architecture/data-model.md#8-hypertable--retention-strategy-per-entity--con-seed-03-resolved |
| vision §7.2 metric VIS-7.2-05 — Versionamento de algoritmos de alerta 100% auditável | product/product-spec.md#33-vision-72-technical-metrics, architecture/data-model.md#5-algorithm-versioning-inv-3--con-0068imp-c-03 |
| US-01 (MUST, Fase 1) — vitais ingested via HL7 v2, manual scoring eliminated | product/product-spec.md#21-must--fase-1-mvp |
| US-02 (MUST, Fase 1) — MEWS calculated in real time | product/product-spec.md#21-must--fase-1-mvp |
| US-03 (MUST, Fase 1) — alerts when MEWS >=5 (urgente) / >=7 (crítico) | product/product-spec.md#21-must--fase-1-mvp |
| US-04 (MUST, Fase 1) — which parameters contributed to the elevated score | product/product-spec.md#21-must--fase-1-mvp |
| US-05 (MUST, Fase 1) — acknowledge (reconhecer) an alert | product/product-spec.md#21-must--fase-1-mvp |
| US-06 (MUST, Fase 1) — painel de leitos with scores + alert status | product/product-spec.md#21-must--fase-1-mvp |
| US-07 (SHOULD, Fase 2) — SOFA + NEWS2 (incl. hypercapnic Scale 2) | product/product-spec.md#22-should--fase-2-original-set |
| US-08 (SHOULD, Fase 2) — Fase-2 clinical alert domains | product/product-spec.md#22-should--fase-2-original-set |
| US-09 (SHOULD, Fase 2) — Fase-2 clinical alert domains (cont.) | product/product-spec.md#22-should--fase-2-original-set |
| US-10 (SHOULD, Fase 2) — Fase-2 clinical alert domains (cont.) | product/product-spec.md#22-should--fase-2-original-set |
| US-11 (COULD, Fase 3) — Fase-3 extension | product/product-spec.md#23-could--fase-3-original-set |
| US-12 (COULD, Fase 3) — Fase-3 extension | product/product-spec.md#23-could--fase-3-original-set |

<!-- END GENERATED -->
