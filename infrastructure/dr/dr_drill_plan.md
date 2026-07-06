# Intensicare — Plano de Disaster Recovery (DR)

**Versão:** 1.0.0
**Data:** 2026-07-06
**Work Order:** WO-038 — Fase 3
**Responsável:** Equipe Intensicare SRE

---

## 1. Objetivo

Este documento define o procedimento de Disaster Recovery (DR) para a plataforma
Intensicare, garantindo continuidade dos serviços de monitoramento clínico de UTI
em caso de falha catastrófica da região primária (AWS `us-east-1`).

---

## 2. Objetivos de Recuperação (RPO/RTO)

| Métrica | Target | Descrição |
|---------|--------|-----------|
| **RPO** | 1 hora | Perda máxima de dados aceitável (intervalo entre último snapshot e desastre) |
| **RTO** | 1 hora | Tempo máximo para restaurar o serviço completo após acionamento do DR |

### 2.1 Justificativa

- Dados de sinais vitais são time-critical (escala de minutos). Um RPO de 1h é
  aceitável porque:
  - TimescaleDB possui WAL archiving contínuo para a região secundária.
  - O Redis de cache/rate-limit pode ser reconstruído a partir do PostgreSQL.
  - Os dispositivos MLLP reenviam mensagens HL7 não confirmadas (store-and-forward).

- RTO de 1h é factível porque:
  - Infraestrutura é definida como código (CDK/Terraform) na região secundária.
  - Imagens de container são multi-region (ECR replication).
  - DNS failover (Route 53) com health checks automatizados.

---

## 3. Arquitetura Multi-Região

```
┌──────────────────────────────────────────────────────────────────────┐
│                         REGIÃO PRIMÁRIA (us-east-1)                   │
│                                                                       │
│  ┌──────────┐   ┌──────────┐   ┌───────────────┐                    │
│  │ ECS Fargate│  │  Aurora/  │   │ ElastiCache    │                    │
│  │ (API)     │   │ TimescaleDB│   │ (Redis)       │                    │
│  └─────┬─────┘   └─────┬─────┘   └───────┬───────┘                    │
│        │               │                  │                            │
│        │    ┌──────────┴──────────────────┘                            │
│        │    │  WAL Archiving (S3 Cross-Region Replication)             │
│        │    │  ECR Image Replication                                    │
│        │    │  Route 53 Health Checks                                   │
│        │    │                                                           │
├────────┼────┼──────────────────────────────────────────────────────────┤
│        │    │           REGIÃO SECUNDÁRIA (us-west-2)                  │
│        │    │                                                           │
│  ┌─────┴────┴─────┐   ┌──────────────┐   ┌───────────────┐            │
│  │ ECS Fargate   │   │ Aurora/       │   │ ElastiCache    │            │
│  │ (API - standby)│   │ TimescaleDB   │   │ (Redis)       │            │
│  │               │   │ (read replica)│   │ (vazio)       │            │
│  └───────────────┘   └──────────────┘   └───────────────┘            │
│                                                                       │
│  Route 53 — failover automático (weighted routing → secundária)       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 4. Procedimento de DR

### 4.1 Pré-requisitos

1. **WAL Archiving ativo**: TimescaleDB configurado com `archive_mode = on` e
   `archive_command` apontando para bucket S3 com cross-region replication.

2. **ECR Replication**: Todas as imagens Docker do Intensicare replicadas para
   `us-west-2` via regra de replication do ECR.

3. **Infraestrutura standby**: Stack CDK/Terraform aplicada na região secundária
   com todos os recursos provisionados (VPC, subnets, security groups, ECS cluster,
   Aurora cluster, ElastiCache). Os serviços ECS rodam com `desired_count = 0`
   (standby quente, custo mínimo).

4. **DNS**: Route 53 hosted zone com registros weighted para ambas as regiões.
   Health checks apontando para `/api/v1/health`.

5. **KMS Multi-Region**: A CMK raiz deve ser uma **multi-region key** (MRK)
   com réplica em `us-west-2` para que as DEKs criptografadas possam ser
   descriptografadas na região secundária.

6. **IAM Identity Center**: O Identity Center é global — não requer replicação.
   A aplicação aponta para o mesmo `iam_oidc_issuer` em ambas as regiões.

### 4.2 Gatilhos de Acionamento

O DR é acionado quando **qualquer** das seguintes condições é detectada:

| Condição | Severidade | Detecção |
|----------|-----------|----------|
| `/api/v1/health` falha por > 5 minutos consecutivos | CRÍTICA | Route 53 health check + CloudWatch alarm |
| Latência p95 > 30s por > 10 minutos | CRÍTICA | CloudWatch Application Signals |
| Error rate 5xx > 20% por > 5 minutos | CRÍTICA | CloudWatch alarm |
| Dead-man's switch não recebe ping por > 2x `watchdog_timeout_seconds` | CRÍTICA | CloudWatch Lambda + SNS |
| Us-east-1 declarada `impaired` pela AWS | CRÍTICA | AWS Health Dashboard webhook |

### 4.3 Playbook de Failover

```yaml
# Ordem cronológica do failover — tempo estimado total: 45 min

fase_1_deteccao:        # t+0 min
  - CloudWatch alarm dispara → SNS → PagerDuty
  - SRE on-call reconhece o incidente
  - Decisão: failover manual (sempre) ou automático (se dead-man switch)

fase_2_validacao:       # t+5 min
  - Confirmar que NÃO é um falso positivo (ex: deploy quebrou health check)
  - Verificar status da região primária via AWS Health Dashboard
  - Se for outage real da AWS → prosseguir

fase_3_promocao_db:     # t+10 min
  - Promover read replica Aurora/TimescaleDB em us-west-2 para primária
    aws rds promote-read-replica --db-instance-identifier intensicare-dr
  - Aguardar promoção (~5-10 min)
  - Verificar WAL apply lag (deve ser < 1h para RPO)
    SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();

fase_4_kms:             # t+20 min
  - Confirmar que a KMS MRK replica em us-west-2 está ativa
    aws kms describe-key --key-id arn:aws:kms:us-west-2:.../mrk-...
  - Testar decrypt de uma DEK de exemplo

fase_5_servicos:        # t+25 min
  - Atualizar ECS services em us-west-2 para desired_count = N (produção)
    aws ecs update-service --cluster intensicare --service api \
      --desired-count 4 --region us-west-2
  - Aguardar tasks atingirem RUNNING (~3 min)

fase_6_dns:             # t+30 min
  - Atualizar Route 53 weighted records:
    * us-east-1 → weight 0
    * us-west-2 → weight 100
  - TTL dos records = 60s (baixo para failover rápido)
  - Verificar propagação: dig api.intensicare.io

fase_7_validacao_final: # t+35 min
  - Smoke test contra o endpoint de produção (agora em us-west-2):
    * GET  /api/v1/health          → 200
    * POST /auth/login              → 200 + tokens
    * GET  /api/v1/dashboard        → 200 (com dados)
    * POST /api/v1/vitals/ingest    → 202
  - Verificar se os dados pós-failover estão íntegros (últimos 60 min)

fase_8_comunicacao:     # t+40 min
  - Atualizar status page
  - Notificar stakeholders (clinical lead, CTO, CSO)
  - Registrar postmortem preliminar
```

### 4.4 Playbook de Failback

Após a restauração da região primária:

```yaml
fase_failback:
  - Sincronizar dados da região secundária → primária (pg_dump/pg_restore
    ou logical replication reversa)
  - Promover us-east-1 de volta a primária
  - Atualizar Route 53: us-east-1 weight 100, us-west-2 weight 0
  - Reduzir desired_count em us-west-2 para 0 (standby)
  - Validar integridade dos dados
  - Fechar postmortem
```

---

## 5. Testes de DR (dr_drill.py)

O script `dr_drill.py` (neste diretório) automatiza a validação periódica
do plano de DR. Consulte a docstring do script para instruções de execução.

### 5.1 Frequência dos Drills

| Tipo | Frequência | Escopo |
|------|-----------|--------|
| **Smoke test** | Semanal (automático via cron) | Valida health checks, conectividade cross-region, replicação |
| **Tabletop** | Trimestral | Simulação de mesa com SRE team (sem mexer em produção) |
| **Failover parcial** | Semestral | Promover réplica, validar leitura, NÃO cortar DNS |
| **Failover completo** | Anual | Failover real com tráfego redirecionado (janela de manutenção) |

---

## 6. Evidências para ANVISA / LGPD

O plano de DR atende aos seguintes requisitos regulatórios:

| Requisito | Evidência |
|-----------|-----------|
| **RDC 686/2022 (ANVISA)** — Continuidade de SaMD Classe II | DR plan documentado + drills trimestrais + RTO ≤ 1h |
| **LGPD Art. 46** — Medidas de segurança técnicas | Criptografia KMS multi-region + WAL encryption |
| **LGPD Art. 49** — Resiliência e restauração | RPO 1h documentado + WAL archiving cross-region |
| **ISO 27001:2022 A.8.14** — Redundância | Multi-AZ + multi-region com failover automatizado |
| **ISO 27701** — Continuidade de dados pessoais | DEKs criptografadas com CMK multi-region |

---

## 7. Contatos de Emergência

| Papel | Contato |
|-------|---------|
| SRE On-Call Primário | sre-oncall@intensicare.io |
| SRE On-Call Secundário | sre-backup@intensicare.io |
| Clinical Lead | clinical-lead@intensicare.io |
| CSO (Security) | cso@intensicare.io |
| AWS Enterprise Support | +1-888-xxx-xxxx (via console) |
