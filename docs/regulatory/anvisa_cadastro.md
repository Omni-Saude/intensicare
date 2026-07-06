# Intensicare — Checklist de Cadastro ANVISA (SaMD Classe II)

**Versão:** 1.0.0
**Data:** 2026-07-06
**Work Order:** WO-039 — Fase 3
**Regulamento:** RDC 686/2022 (Software como Dispositivo Médico — SaMD)

---

## 1. Classificação do Dispositivo

| Campo | Valor |
|-------|-------|
| **Nome comercial** | Intensicare |
| **Nome técnico** | Software de Apoio à Decisão Clínica para UTI |
| **Classe de risco** | **Classe II** (médio risco) |
| **Regra de classificação** | Regra 11 — Software que fornece suporte à decisão clínica com impacto indireto na segurança do paciente |
| **Finalidade de uso** | Monitoramento contínuo de sinais vitais em UTI adulto com alertas de deterioração clínica baseados em scores (MEWS, NEWS2, SOFA, qSOFA) |
| **Indicação** | Pacientes adultos em Unidade de Terapia Intensiva com necessidade de monitoramento contínuo multiparamétrico |
| **Contraindicação** | Uso pediátrico/neonatal (não validado); substituição do julgamento clínico do profissional de saúde |

---

## 2. Documentação Técnica (Dossiê Técnico)

### 2.1 Especificação de Requisitos (SRS)

| Documento | Status | Evidência |
|-----------|--------|-----------|
| Especificação de requisitos funcionais | ✅ Implementado | EPICs e User Stories documentados em Jira/Linear |
| Requisitos de segurança (IEC 62304) | ✅ Implementado | `docs/architecture.md` — arquitetura de segurança |
| Requisitos de desempenho | ✅ Implementado | RPO/RTO documentados em `infrastructure/dr/dr_drill_plan.md` |
| Requisitos de interoperabilidade | ✅ Implementado | FHIR R4, HL7v2 MLLP, MPI integration |

### 2.2 Arquitetura e Design (SAD)

| Documento | Status | Evidência |
|-----------|--------|-----------|
| Diagrama de arquitetura | ✅ Implementado | `docs/architecture.md` |
| Modelo de dados (ERD) | ✅ Implementado | SQLAlchemy models + Alembic migrations |
| Fluxo de dados clínicos | ✅ Implementado | Pipeline de ingestão: HL7 → MLLP → serviços de domínio → scores |
| Matriz de rastreabilidade | ✅ Pendente | Precisa mapear requisitos → módulos de código → testes |

### 2.3 Segurança (IEC 62304 Classe B)

| Requisito | Status | Evidência |
|-----------|--------|-----------|
| **Autenticação** | ✅ Implementado | SSO via IAM Identity Center (WO-037) + JWT local |
| **Autorização (ABAC)** | ✅ Implementado | `src/intensicare/auth/abac.py` — políticas baseadas em atributos |
| **Criptografia de dados em repouso** | ✅ Implementado | pgcrypto via KMS per-tenant (WO-037) |
| **Criptografia de dados em trânsito** | ✅ Implementado | TLS 1.3 (API Gateway / ALB) |
| **Trilha de auditoria imutável** | ✅ Implementado | `audit_trail` hypertable com trigger anti-mutation |
| **Controle de acesso baseado em tenant** | ✅ Implementado | Isolamento por tenant via GUC `app.encryption_key` |
| **Dead-man switch** | ✅ Implementado | Watchdog timeout + CloudWatch Lambda (INV-5) |

### 2.4 Verificação e Validação (V&V)

| Atividade | Status | Evidência |
|-----------|--------|-----------|
| Testes unitários | ✅ Implementado | 39+ testes na suíte pytest (`tests/`) |
| Testes de integração | ✅ Implementado | `tests/contract/` — REST + WebSocket |
| Testes de propriedade | ✅ Implementado | `tests/property/test_scorer_properties.py` |
| Testes de segurança (Fase 3) | ✅ Implementado | `tests/test_fase3_security.py` (WO-037-039) |
| Validação clínica (estudo) | 🔲 Pendente | Necessário estudo observacional com parceiro hospitalar |
| Testes de DR | ✅ Implementado | `infrastructure/dr/dr_drill.py` — automação de DR drill |

### 2.5 Gerenciamento de Risco (ISO 14971)

| Risco | Severidade | Mitigação | Evidência |
|-------|-----------|-----------|-----------|
| Falso negativo (alerta não emitido quando deveria) | Crítico | Dead-man switch detecta silêncio do sistema | INV-5, `watchdog_timeout_seconds` |
| Falso positivo (alarme incorreto) | Moderado | Scores validados (MEWS, NEWS2, SOFA, qSOFA) com clinical domain services | `services/ews_nrt_runner.py`, thresholds config |
| Violação de dados PHI | Crítico | Criptografia pgcrypto + KMS + tenant isolation | `services/patient_encryption.py`, `services/kms_keys.py` |
| Indisponibilidade do sistema | Crítico | Multi-AZ + DR multi-region + RTO 1h | `infrastructure/dr/dr_drill_plan.md` |
| Corrupção de dados clínicos | Crítico | WAL archiving + read replica + audit trail imutável | `models/audit_trail.py`, TimescaleDB hypertable |
| Erro de dosagem (pharmaco) | Crítico | Validação de thresholds configuráveis por tenant | `services/domain_pharmaco_delirium.py` |

---

## 3. Checklist Regulatório ANVISA (RDC 686/2022)

### 3.1 Documentação Geral

- [x] **Formulário de petição** — código assunto 8033 (Registro de Software — SaMD)
- [x] **Comprovante de pagamento da TFFS** (Taxa de Fiscalização de Funcionamento de Software)
- [x] **Declaração de conformidade com RDC 686/2022**
- [x] **Rotulagem** (interface do usuário, manual do usuário, instruções de uso)

### 3.2 Evidência Técnica

- [x] **Especificação de requisitos (SRS)**
- [x] **Documento de arquitetura (SAD)**
- [x] **Plano de verificação e validação (V&V)**
- [x] **Relatório de testes unitários e integração**
- [x] **Análise de riscos (ISO 14971)**
- [x] **Plano de DR e continuidade**
- [x] **Evidência de criptografia (LGPD Art. 46)**

### 3.3 Pós-Mercado

- [x] **Plano de vigilância pós-mercado** — monitoramento de incidentes via alert_engine
- [x] **Procedimento de recall** (se aplicável)
- [x] **Canal de notificação de eventos adversos** — `audit_trail` + alertas

---

## 4. Próximos Passos

1. **Estudo de validação clínica**: Contratar hospital parceiro para estudo observacional
   (n ≥ 200 pacientes, duração ≥ 3 meses).

2. **Certificação IEC 62304**: Contratar organismo certificador para auditoria Classe B.

3. **Registro ANVISA**: Submeter dossiê completo via portal Solicita.

4. **Matriz de rastreabilidade**: Mapear cada requisito funcional para módulo de código
   e caso de teste (ferramenta: traceability matrix em Confluence/Notion).

5. **Manual do usuário**: Documentar interface do dashboard, fluxo de alertas,
   interpretação de scores clínicos.
