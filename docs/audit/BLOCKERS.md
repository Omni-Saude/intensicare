# BLOCKERS.md — IntensiCare Gap Closure Blockers

**Created:** 2026-07-09 08:16 UTC-3

---

## AWS-DEPENDENT BLOCKERS

### B1 — C1: CDC Consumer ADT
- **Gap:** CDC consumer (Kafka/MSK) para tópicos ADT não construído
- **Bloqueador:** AWS account não provisionada; sem acesso a MSK/Kafka
- **Impacto:** Bloqueia C2 (tabelas ADT), H2 (74 DMN rules), H10 (pre-population)
- **Plano de desbloqueio:** Provisionar AWS account → criar MSK cluster → implementar `consumers/cdc_adt.py`
- **Owner:** DevOps / AWS Admin
- **Workaround:** Implementar API REST-based movement registration (já parcialmente feito em domain_movimentacao.py)
- **Status:** 🚫 BLOCKED

### B2 — C6: ECS Task Definitions
- **Gap:** Task definitions ECS Fargate para API, Engine, MLLP listener
- **Bloqueador:** AWS account não provisionada
- **Impacto:** Deploy em staging/production impossível sem ECS
- **Plano de desbloqueio:** Provisionar AWS → criar task definitions via Terraform ou Console
- **Owner:** DevOps / AWS Admin
- **Status:** 🚫 BLOCKED

### B3 — H6: IAM Identity Center SSO Test
- **Gap:** Integração IAM IC nunca testada contra IdP real
- **Bloqueador:** IAM Identity Center não configurado em AWS
- **Impacto:** Auth SSO não validada em staging
- **Plano de desbloqueio:** Configurar IAM IC → testar `auth/iam.py` contra IdP real
- **Owner:** DevOps / Security
- **Status:** 🚫 BLOCKED

---

## DEPENDENCY BLOCKERS

### B4 — H2: 74 DMN Movement Rules
- **Gap:** 74 regras DMN de movimentação (apenas 9/74 implementadas)
- **Bloqueador:** Depende de C1 (CDC consumer) para ingestão de eventos
- **Impacto:** Regras de qualidade/segurança (readmissão <24h, alta sem medicação) não disparam
- **Plano de desbloqueio:** Após C1 → implementar DMN engine
- **Owner:** Backend Team
- **Status:** 🚫 BLOCKED (chain: C1 → C2 → H2)

### B5 — H10: Pre-population from MovimentacaoStateStore
- **Gap:** Evoluções não pre-populam dados do state store
- **Bloqueador:** Depende de C1 (CDC consumer) → C2 (ADT tables) → H2 (DMN rules)
- **Impacto:** Campos de Background no template de evolução ficam vazios
- **Plano de desbloqueio:** Após chain C1→C2→H2 → implementar pre-population
- **Workaround:** Implementar stub com mock data para desbloquear H11 (templates)
- **Owner:** Backend Team
- **Status:** 🚫 BLOCKED (with workaround available)

---

## BLOCKER RESOLUTION TRACKER

| Blocker | Gaps Blocked | Can Workaround? | Workaround |
|---------|-------------|-----------------|------------|
| B1 (AWS CDC) | C1, C2, H2, H10 | ✅ Partial | REST-based movement API exists |
| B2 (AWS ECS) | C6 | ❌ No | — |
| B3 (AWS IAM) | H6 | ❌ No | IAM stays disabled (`iam_enabled=False`) |
| B4 (C1→H2) | H2 | ✅ Yes | Implement rules against REST API |
| B5 (C1→H10) | H10 | ✅ Yes | Stub with mock data |

---

*Updated each milestone.*
