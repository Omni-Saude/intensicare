# Alternativa-B Decision Template — CTO + AMH Sign-Off

**Owner:** amh-integration-architect
**Dependências de ratificação:** system-architecture.md §6, ADR-001 (ADR001-F-08)
**Status:** Template — preencher quando o trigger disparar

---

## 1. Contexto

A **Alternativa B** (ADR-001 §Alternativas, `ADR001-F-08`) consiste em provisionar **um tópico MSK dedicado** para o feed operacional de sinais vitais, contornando o pipeline batch do AMH Data Platform para o caminho NRT (near-real-time). É o escape hatch de Fase 4 do ADR-001, ativado **apenas** quando o caminho operacional MLLP não consegue sustentar `VIS-C-09` (p95 bedside→alert < 30s).

Conforme **system-architecture.md §6.1**, o trigger é quantificado em duas condições (T1):

| # | Condição | Threshold |
|---|---|---|
| **T1(a)** | Vitals end-to-end bedside→alert p95 — `source_freshness` + owned-pipeline Σ | **> 30s** (`VIS-C-09`) sustentado por **7 dias consecutivos** com feed MLLP saudável |
| **T1(b)** | Feed MLLP indisponível | **> 0.5%** das monitored bed-hours na mesma janela de 7 dias (espelha `ADR001-C-10`, 99.5% availability floor) |

**Este documento é o template de decisão.** Deve ser preenchido com evidências reais de telemetria e submetido para sign-off conjunto do **CTO Office + Time de Engenharia AMH** antes do provisionamento do tópico MSK (§6.2).

---

## 2. Evidências de Telemetria

### 2.1 Período de Observação

| Campo | Valor |
|---|---|
| Data de início da janela | `____-__-__` |
| Data de fim da janela | `____-__-__` |
| Dias na janela rolante | 7 |
| Fonte das métricas | AMP/Grafana — OTEL (`ADR001-C-06`) |

### 2.2 Condição Disparadora

- [ ] **T1(a)** — p95 bedside→alert > 30s por 7 dias consecutivos, MLLP saudável
- [ ] **T1(b)** — MLLP indisponível > 0.5% bed-hours

### 2.3 Série Temporal de Latência (7 dias)

| Dia | p95 bedside→alert (s) | p95 owned-pipeline (s) | `source_freshness` (s) | MLLP status | MLLP unavail % |
|---|---|---|---|---|---|
| 1 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 2 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 3 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 4 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 5 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 6 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |
| 7 | ____ | ____ | ____ | [ ] OK [ ] Degradado | ____ |

**Threshold:** p95 > 30s (`VIS-C-09`)

### 2.4 Métricas Agregadas

| Métrica | Valor | Threshold | Status |
|---|---|---|---|
| p95 médio (janela) | ____ s | 30s | [ ] BREACH [ ] OK |
| p95 máximo (janela) | ____ s | 30s | [ ] BREACH [ ] OK |
| Dias acima do threshold | ____ / 7 | 7 consecutivos | [ ] BREACH [ ] OK |
| MLLP unavail (max) | ____ % | 0.5% | [ ] BREACH [ ] OK |

### 2.5 Gráficos e Dashboards de Referência

- AMP Dashboard URL: `________________________________`
- Grafana Snapshot URL: `________________________________`
- OTEL trace exemplar (trace ID): `________________________________`

---

## 3. Avaliação de Impacto

### 3.1 Domínios Afetados

| Domínio | Impacto | Scores afetados | Alerts suprimidos/atrasados |
|---|---|---|---|
| Early-Warning Scores (vitals) | 🔴 CRÍTICO | MEWS, NEWS2, qSOFA | ____ |
| Hemodynamics (NRT) | 🟡 ALTO | Shock index, MAP trends | ____ |
| Respiratory (NRT SpO₂) | 🟡 ALTO | SpO₂/FiO₂ trends | ____ |
| Demais domínios (batch) | 🟢 BAIXO | — | Não afetados (Gold batch é suficiente) |

### 3.2 Riscos de NÃO Ativar

- Atraso na detecção de deterioração clínica por early-warning scores
- Violação do SLO `VIS-C-09` (p95 < 30s) para scores vitals-driven
- Risco clínico: MEWS/NEWS2/qSOFA com latência > 30s podem perder janelas de intervenção precoce (RRT, `CON-0062`)

### 3.3 Riscos de ATIVAR

- Complexidade operacional adicional (um tópico MSK a mais)
- Custo de infraestrutura (MSK provisioning, taxa de transferência)
- Divergência potencial entre feed streaming e Gold batch (mitigado por Gold write-back `ADR001-C-04` como reconciliação)
- Dependência do AMH platform team para provisionamento e SLA do tópico

---

## 4. Proposta Técnica

### 4.1 Escopo do Tópico MSK

| Parâmetro | Valor Proposto |
|---|---|
| **Tópico** | `intensicare-vitals-operational` |
| **Partições** | ____ (sugestão: 3-6, por tenant) |
| **Retenção** | ____ horas (sugestão: 24-72h) |
| **Throughput estimado** | ____ msg/s (240 leitos, ~1 msg/leito/2s = ~120 msg/s) |
| **Formato** | HL7 v2 ORU-R01 (mesmo schema do MLLP listener) |
| **Source** | Bedside monitors → MSK (provisionado pelo AMH platform team) |
| **Consumer** | IntensiCare Alert Engine (NRT runner) |

### 4.2 Invariantes Preservados

- [ ] **Gold write-back mantido** (`ADR001-C-04`) — `fact_patient_score` / `fact_alert` continuam sendo escritos
- [ ] **Athena analytics mantido** (`ADR001-C-01`) — Gold permanece fonte analítica canônica
- [ ] **`mpi_id` como chave única** (`ADR001-C-02`) — sem alteração
- [ ] **Nenhum broker próprio** — apenas o tópico provisionado pelo AMH platform team (`ADR001-F-10`)
- [ ] **OTEL/AMP/Grafana mantido** (`ADR001-C-06`) — métricas do novo path exportadas para o mesmo stack

### 4.3 Diagrama de Arquitetura (pós-ativação)

```
Bedside Monitors (HL7 ORU-R01)
    │
    ├──▶ MLLP Listener (existente, mantido como fallback)
    │         │
    │         └──▶ PostgreSQL operational store
    │
    └──▶ MSK Topic: intensicare-vitals-operational (NOVO)
              │
              └──▶ Alert Engine (NRT runner)
                        │
                        ├──▶ PostgreSQL operational store
                        ├──▶ Redis (score cache + rate limit)
                        └──▶ Gold write-back (fact_patient_score / fact_alert)
```

---

## 5. Cronograma de Ativação

| Fase | Atividade | Responsável | Prazo |
|---|---|---|---|
| 1 | Provisionamento do tópico MSK | AMH Platform Team | ____ |
| 2 | Configuração do consumer (Alert Engine) | IntensiCare Team | ____ |
| 3 | Testes de integração (shadow mode) | QA / Clinical Safety | ____ |
| 4 | Validação de latência p95 < 30s | SRE / Observability | ____ |
| 5 | Ativação em produção (canary → full) | DevOps / AMH | ____ |
| 6 | Monitoramento pós-ativação (7 dias) | SRE / Observability | ____ |

---

## 6. Sign-Off

A ativação da Alternativa B requer aprovação conjunta de **três partes** (§6.2):

| Papel | Nome | Assinatura | Data |
|---|---|---|---|
| **CTO Office** | _________________________ | _________________________ | ___/___/____ |
| **AMH Engineering Lead** | _________________________ | _________________________ | ___/___/____ |
| **amh-integration-architect** | _________________________ | _________________________ | ___/___/____ |

### 6.1 Comentários / Condições

```
________________________________________________________________________________
________________________________________________________________________________
________________________________________________________________________________
________________________________________________________________________________
```

---

## 7. Referências

| Documento | Seção | Descrição |
|---|---|---|
| [system-architecture.md](../architecture/system-architecture.md) | §6 | Alternativa-B decision table (T1–T6) |
| [system-architecture.md](../architecture/system-architecture.md) | §6.2 | Activation mechanics — owner, approval, invariants |
| [ADR-001 — AMH Data Platform Consumer](../adr/ADR-001-amh-data-platform-consumer.md) | §Alternativas | Alternativa B definition (`ADR001-F-08`) |
| [_work/budgets/latency.yaml](../_work/budgets/latency.yaml) | — | Canonical latency budget (CON-SEED-01) |
| [observability-slo.md](../architecture/observability-slo.md) | §3–4 | OTEL metrics instrumentation |
| [BUILD-JOURNAL.md](BUILD-JOURNAL.md) | WO-040 | Registro de decisão e evidências |

---

**Template Version:** 1.0
**Criado em:** 2026-07-06
**Próximo passo:** Preencher §2 com dados de telemetria reais e convocar sign-off.
