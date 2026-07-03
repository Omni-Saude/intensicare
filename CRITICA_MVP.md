# Análise Crítica da Arquitetura MVP Proposta — Intensicare

**Autor:** Agente de Revisão Arquitetural  
**Data:** 26 de Junho de 2026  
**Escopo:** Validação da simplificação arquitetural de 12+ componentes para **FastAPI Monolith + PostgreSQL/TimescaleDB + Redis + Docker Compose** como MVP da plataforma Intensicare.  
**Público-alvo:** Hospitais brasileiros (médio/grande porte), integração primária via HL7 v2, FHIR R4 como objetivo futuro.  
**Contexto regulatório:** LGPD (Lei Geral de Proteção de Dados), ANS/SBIS requisitos para sistemas de informação em saúde, resolução CFM sobre prontuário eletrônico.  

---

## 1. A Stack Simplificada é Apropriada para o MVP?

### Veredito: SIM, com qualificações importantes.

A stack proposta (FastAPI + PostgreSQL/TimescaleDB + Redis + Docker Compose) **é adequada para um MVP focado em 1–3 UTIs piloto** (estimativa de 30–90 leitos monitorados simultaneamente). Vamos decompor por caso de uso:

### 1.1 Ingestão de Sinais Vitais

O README aspira usar Apache NiFi para ingestão HL7/FHIR. Para um MVP em hospital brasileiro:

- **HL7 v2 é fundamental e inevitável.** A maioria dos monitores multiparamétricos (Philips, GE, Mindray, Dixtal) e sistemas de prontuário eletrônico (MV, Tasy, Soul MV) expõem HL7 v2 por TCP/IP (MLLP — Minimal Lower Layer Protocol). FastAPI **não tem suporte nativo a MLLP**, que é um protocolo de framing binário sobre TCP, não HTTP.
- **Risco:** Se você não tiver um adaptador MLLP→HTTP no MVP, não conseguirá receber dados de monitores reais. A correção é incluir um **sidecar MLLP** (ex: Mirth Connect em modo minimalista, ou um serviço Python com `hl7apy` + `asyncio` escutando em porta TCP) que traduza mensagens HL7 v2 para JSON e as encaminhe à API FastAPI.
- **Alternativa pragmática para MVP:** Muitos hospitais brasileiros já possuem um barramento de integração (InterSystems Ensemble, Mirth Connect, ou mesmo o Tasy Integration Engine). Se o hospital piloto tiver esse barramento, o MVP pode consumir via REST/Webhook do barramento existente, eliminando a necessidade de MLLP direto.

### 1.2 Cálculo de Scores (MEWS, SOFA, qSOFA, NEWS2)

Estes são **algoritmos determinísticos baseados em thresholds**. Não requerem ML runtime (ONNX) nem processamento de streams (Flink). São perfeitamente implementáveis como:

- **Funções síncronas em Python** disparadas na inserção de vitais (via trigger PostgreSQL ou chamada direta no endpoint POST /vitals).
- **Tarefas assíncronas com Redis Queue (RQ/ARQ)** para desacoplar ingestão de scoring sem introduzir Kafka. O Redis que já está na stack resolve isso.

**O ONNX/ML do README é aspiracional:** o modelo de sepse treinado no MIMIC-IV ainda está "under review" segundo a tabela de validação do próprio README. Não faz sentido incluir runtime de ML no MVP se o modelo clínico nem está validado.

### 1.3 Alerting

Para 30–90 leitos, o volume de alertas é baixo (dezenas por hora, não milhares por segundo). FastAPI + Redis Pub/Sub ou WebSocket nativo é suficiente. O Redis serve como:

- **Cache de estado do paciente** (último score, tendências de 6h).
- **Rate limiting de alertas** (evitar alarm fatigue — "ALERT_RATE_LIMIT_PER_HOUR=3" do README).
- **Fila de notificações** para push (WebSocket, SMS, WhatsApp — comum em hospitais brasileiros).

### 1.4 PostgreSQL + TimescaleDB

TimescaleDB é essencialmente PostgreSQL com extensão para time-series. **Acerto total.** O PostgreSQL sozinho já oferece:

- **Hypertables** para séries temporais de vitais (inserção eficiente, compressão automática, retenção policy).
- **Relacional** para dados mestres (pacientes, leitos, unidades, usuários).
- **JSONB** para armazenar payloads HL7/FHIR semi-estruturados, flexível para evolução de schema.
- **Auditoria nativa** via triggers PL/pgSQL (abordado na seção 4).

**Números de capacidade para referência:** um PostgreSQL/TimescaleDB em hardware modesto (4 vCPU, 16 GB RAM) ingere confortavelmente 50.000–100.000 pontos de dados/segundo em hypertables. Para 90 leitos com vitais a cada 5 minutos + waveforms a cada 2 segundos, você está na casa de ~3.000 pontos/segundo — **duas ordens de grandeza abaixo do limite.**

---

## 2. Riscos de NÃO Começar com Event Sourcing / Kafka

### 2.1 Cenário Atual vs. Futuro

O README posiciona Kafka como "Immutable Event Log" e "High-throughput message backbone". O MVP sem Kafka **não tem event sourcing**. Isso traz riscos específicos:

### Risco 1: Perda de Rastreabilidade de Dados (ALTO)

| Com Kafka | Sem Kafka |
|-----------|-----------|
| Todo dado ingerido é um evento imutável e replayable | Dados viram rows em tabela SQL; UPDATE/sobrescrita possível sem histórico |
| Correção retroativa de scores é trivial (reprocessa o log) | Reprocessamento requer restore de backup + script ad-hoc |
| Debug de alerta falso: "o que o sistema viu às 14:32:17?" | Sem log de evento bruto, você depende de logging textual (frágil) |

**Mitigação MVP:** Implementar **event log em tabela PostgreSQL** (`ingestion_events`) com:

- Append-only (sem UPDATE/DELETE, só INSERT + soft-delete lógico).
- Payload bruto (JSONB) da mensagem HL7 original.
- Timestamp de ingestão imutável (server-side `now()`).
- UUID de idempotência (chave única).

Isso não é Kafka, mas para volume de MVP, oferece o invariante crítico: **"todo dado que entrou está registrado de forma imutável e recuperável"**. Na fase 2, essa tabela vira o tópico Kafka inicial (change data capture com Debezium).

### Risco 2: Acoplamento Ingestão→Processamento (MÉDIO)

Sem Kafka como buffer/desacoplador, se a API de scoring cair, as mensagens HL7 que chegarem nesse intervalo podem ser perdidas se você não tiver fila interna.

**Mitigação:** Redis como buffer intermediário com `LPUSH`/`BRPOP` + padrão outbox. Se o scoring falhar, a mensagem fica na fila Redis e é reprocessada. (Redis com persistência AOF habilitada — sem `appendfsync no`, use `appendfsync everysec`.)

### Risco 3: Dificuldade de Evoluir para Event-Driven no Futuro (BAIXO)

Se o MVP for bem-sucedido e você precisar migrar para Kafka na Fase 2, a migração será **mais trabalhosa** do que se tivesse começado com Kafka. Porém, é um custo aceitável considerando que:

- 80–90% dos MVPs de healthcare nunca chegam à escala que justifica Kafka.
- O tempo de mercado ganho ao não operacionalizar Kafka (cluster de 3+ brokers, ZooKeeper/KRaft, particionamento, retenção) é de **3–6 meses** em equipe enxuta.
- Você pode usar o **Transactional Outbox Pattern** desde o dia 1: toda mutação de estado clínico grava primeiro na tabela de outbox; um worker (RQ/ARQ) publica eventos. Na migração para Kafka, troca-se o publisher do worker, o resto do código permanece igual.

### Risco 4: Conformidade Regulatória (MÉDIO)

A LGPD e normas do CFM exigem:

- **Integridade dos dados** — não pode haver adulteração de registros clínicos após o fato.
- **Trilha de auditoria** — quem acessou, quando, o quê.

Sem event sourcing (Kafka), você precisa implementar isso **explicitamente** no PostgreSQL (triggers de auditoria, row-level security, append-only tables). É factível, mas **não negociável** — se o MVP rodar em hospital real com dados de pacientes, a trilha de auditoria tem que estar implementada antes do primeiro paciente. Veja seção 4.

---

## 3. FastAPI vs. Go vs. Node.js para Integração Hospitalar

### 3.1 Veredito: FastAPI é a melhor escolha para MVP brasileiro, com ressalva para HL7.

### Argumentos a favor de FastAPI

| Critério | FastAPI (Python) | Go | Node.js |
|----------|------------------|----|--------|
| **Ecossistema HL7 v2** | `hl7apy` (maduro, mantido) — parse, build, validate mensagens HL7 | `go-hl7` (básico, pouca manutenção) | `node-hl7` (maduro) |
| **Ecossistema FHIR** | `fhir.resources` (oficial HL7), `fhirclient` (SMART) | `go-fhir` (limitado) | `fhir` (bom) |
| **Bibliotecas científicas/clínicas** | scipy, numpy, pandas — cálculo de scores, análise de tendências, futura integração ML | Limitado | Limitado |
| **Mão de obra no Brasil** | Abundante (Python é a linguagem #1 em healthtechs brasileiras) | Escassa para domínio de saúde | Abundante, mas mais voltada a front-end |
| **Produtividade / Velocidade de iteração** | Alta (Pydantic, auto-docs, type hints) | Média (compilação, verbosidade) | Alta, mas tipagem frágil |
| **Performance bruta** | Boa para I/O (asyncio) — 5k–10k req/s em máquina modesta | Excelente (30k+ req/s) | Boa (event loop, mas single-threaded) |
| **WebSocket nativo** | Sim, Starlette integrado | Requer libs externas | Sim, first-class |

### O caso contra Go para MVP

Go seria superior em latência pura e uso de memória, mas:

- O gargalo do MVP **não é performance da API**, é integração hospitalar (HL7, conectividade de rede, barramentos legados).
- A velocidade de desenvolvimento em Python para prototipação clínica (ajuste de thresholds, iteração com médicos) é significativamente maior.
- O ecossistema HL7/FHIR em Go é imaturo — você passaria mais tempo escrevendo parsers HL7 do que construindo features clínicas.

### O caso contra Node.js para MVP (mais sutil)

Node.js seria uma escolha razoável, especialmente com TypeScript. O problema é o ecossistema de computação científica — cálculo de scores como SOFA (que envolve agregações temporais, razão PaO₂/FiO₂, etc.) é mais natural em Python. Se o time tem mais proficiência em Node, é uma alternativa viável, mas Python ganha pela afinidade com o domínio.

### Ressalva crítica: HL7 v2 / MLLP

Independente da linguagem, o MVP precisa de um **serviço MLLP listener** que:

1. Escute em porta TCP (típico: 2575 ou 8440).
2. Aceite framing MLLP (caractere VT no início, FS + CR no fim).
3. Parseie segmentos HL7 v2.x (MSH, PID, OBR, OBX).
4. Encaminhe o parseado para a API FastAPI como JSON.

**Recomendação:** Um microsserviço Python separado (FastAPI + `hl7apy` + `asyncio` com `asyncio.start_server`) ou usar Mirth Connect como sidecar (se o hospital já tiver licença). Isso resolve o gap MLLP sem contaminar a API principal com complexidade de protocolo binário.

---

## 4. Invariantes Arquiteturais Não-Negociáveis (Mesmo no MVP)

Se o MVP for rodar com **dados reais de pacientes** em ambiente hospitalar (não em sandbox/benchmark), estes são os requisitos que **não podem ser postergados para Fase 2:**

### 4.1 Trilha de Auditoria Imutável

**O quê:** Todo acesso e mutação a dados clínicos deve ser registrado com timestamp, usuário, ação e payload.

**Como no MVP:**

```sql
-- Tabela de auditoria unificada
CREATE TABLE audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_id TEXT NOT NULL,           -- usuário ou sistema
    action TEXT NOT NULL,             -- 'vital_ingested', 'score_calculated', 'alert_acknowledged'
    resource_type TEXT NOT NULL,      -- 'patient', 'vital_signs', 'alert'
    resource_id TEXT NOT NULL,
    payload JSONB NOT NULL,           -- snapshot completo do que foi feito
    ip_address INET,
    correlation_id UUID               -- para rastrear cadeia causal
);

-- Trigger que impede UPDATE/DELETE na tabela de eventos de ingestão
CREATE OR REPLACE FUNCTION prevent_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Mutação não permitida em tabela de auditoria de dados clínicos';
END;
$$ LANGUAGE plpgsql;
```

**Por que não pode esperar:** LGPD Art. 6º, VII + Resolução CFM 1.821/07. Sem auditoria, o MVP é **ilegal para dados de pacientes reais.**

### 4.2 Idempotência de Ingestão

**O quê:** Se o hospital reenviar a mesma mensagem HL7 (retry de rede, comum em MLLP), o sistema não pode duplicar dados clínicos nem disparar alertas duplicados.

**Como no MVP:**

- Cada mensagem HL7 carrega `MSH-10 Message Control ID`. Armazenar como chave única no PostgreSQL.
- Alternativa: calcular hash SHA-256 do payload HL7 completo como chave de idempotência.
- `INSERT ... ON CONFLICT (idempotency_key) DO NOTHING` — a mensagem é aceita uma única vez.

**Por que não pode esperar:** Duplicação de dados de vitais corrompe séries temporais (médias, tendências) e pode gerar artefatos nos scores — ex: dois batimentos cardíacos de 40 bpm duplicados podem disparar alerta falso de bradicardia.

### 4.3 Versionamento de Algoritmos de Scoring

**O quê:** Cada score calculado (MEWS, SOFA, NEWS2) deve registrar **qual versão do algoritmo** foi usada para calculá-lo.

**Como no MVP:**

```sql
CREATE TABLE clinical_scores (
    id UUID PRIMARY KEY,
    patient_id TEXT NOT NULL,
    score_type TEXT NOT NULL,      -- 'MEWS', 'SOFA', 'qSOFA', 'NEWS2'
    score_value NUMERIC NOT NULL,
    algorithm_version TEXT NOT NULL, -- 'MEWS-v1.0.0', 'NEWS2-NHS-2023'
    input_data JSONB NOT NULL,       -- valores de entrada (HR, RR, Temp, etc.)
    calculated_at TIMESTAMPTZ NOT NULL
);
```

**Por que não pode esperar:** Se você ajustar thresholds (ex: mudar MEWS de 5→4 para alerta urgente) e não souber qual versão gerou cada score histórico, perde a capacidade de auditar decisões clínicas passadas. Em auditoria de óbito, isso é catastrófico.

### 4.4 Criptografia de Dados Sensíveis em Repouso

**O quê:** PHI (Protected Health Information) — nome, CPF, CNS, data de nascimento — não pode ser armazenado em texto plano no banco.

**Como no MVP:**

- PostgreSQL `pgcrypto` para criptografar campos sensíveis.
- Ou criptografia em nível de aplicação com envelope encryption (chave mestra no Redis/ambiente, chaves de dados no banco).
- **Mínimo aceitável:** Colunas `patient_name`, `patient_document` com AES-256-GCM usando chave via variável de ambiente (não hardcoded).

**Por que não pode esperar:** LGPD Art. 46 — medidas de segurança proporcionais ao risco. Dados de saúde são dados sensíveis (Art. 5º, II). Vazamento de banco de dados MVP sem criptografia é incidente reportável à ANPD.

### 4.5 Health Check e Dead Man's Switch

**O quê:** Se o sistema cair silenciosamente, precisa haver detecção externa.

**Como no MVP:**

- Endpoint `/api/v1/health` com verificação de conectividade ao banco e Redis.
- Script externo (cron ou systemd timer no host Docker) que faz polling e dispara alerta por SMS/WhatsApp se o sistema não responder em 60s.

**Por que não pode esperar:** O propósito do sistema é alertar sobre deterioração clínica. Se o próprio sistema cair e ninguém souber, o risco de dano ao paciente é real. Isso é **patient safety 101.**

### 4.6 Retry com Backoff Exponencial nas Integrações de Saída

**O quê:** Quando o MVP enviar um alerta (SMS, push notification, callback HTTP para o barramento do hospital) e falhar, deve re-tentar com backoff.

**Como no MVP:**

- Redis Queue com mecanismo de retry (ARQ tem nativamente, RQ tem `retry`).
- Dead letter queue para alertas que falharam após N tentativas — uma pessoa real precisa ver isso.

---

## 5. O Que Pode (e Deve) Ser Postergado para Fase 2

| Componente do README | Postergar? | Justificativa |
|----------------------|-----------|---------------|
| **Apache NiFi** | SIM | Substituído por MLLP sidecar + endpoints FastAPI. Complexidade desproporcional para MVP. |
| **Apache Kafka** | SIM | Event log em PostgreSQL + Redis como buffer cobre o MVP. Migrar com Outbox Pattern na Fase 2. |
| **Apache Flink** | SIM | Cálculo de scores é determinístico e de baixo volume; não requer CEP. |
| **ONNX Runtime** | SIM | Modelo de sepse não está clinicamente validado (status "Under Review" no README). |
| **Kubernetes** | SIM | Docker Compose é suficiente para 1–3 UTIs. K8s agrega complexidade operacional de 3–4x. |
| **Linkerd** | SIM | mTLS é relevante em multi-cluster; em monólito Docker Compose, TLS no reverse proxy (Caddy/Nginx) basta. |
| **Keycloak** | PARCIAL | MVP pode usar OAuth2 simples com `fastapi-users` + JWT. Keycloak só se justifica quando houver SSO com AD/hospital ou múltiplos realms. |
| **HashiCorp Vault** | SIM | Segredos via variáveis de ambiente + Docker secrets. Vault é overkill para MVP. |
| **ELK Stack** | SIM | Logs estruturados (JSON) para stdout/stderr + driver de log do Docker (journald/loki). Grafana + Loki no lugar de ELK se precisar de UI. |
| **MinIO** | SIM | Sistema de arquivos local ou volume Docker. MinIO é necessário quando houver múltiplas réplicas ou necessidade de S3. |
| **Prometheus + Grafana** | PARCIAL | Manter apenas métricas básicas expostas via `/metrics` (Prometheus format). Grafana pode ser adicionado com um container extra (baixo esforço). |
| **SMART-on-FHIR Apps** | SIM | Focar em API FHIR R4 server-side primeiro. SMART apps requerem Keycloak + fluxo de autorização complexo. |
| **Mobile App (React Native)** | SIM | Web app responsivo (mobile-first CSS) supre 80% da necessidade dos plantonistas. |

---

## 6. Arquitetura MVP Recomendada (Diagrama Conceitual)

```
┌──────────────────────────────────────────────────────┐
│              MONITORES / EHR HOSPITALAR               │
│            (HL7 v2 por MLLP / TCP/IP)                 │
└────────────────────────┬─────────────────────────────┘
                         │ TCP:2575 (MLLP)
┌────────────────────────▼─────────────────────────────┐
│            MLLP Listener (Python asyncio)             │
│         Parse HL7 → JSON → POST /api/v1/vitals        │
└────────────────────────┬─────────────────────────────┘
                         │ HTTPS (REST)
┌────────────────────────▼─────────────────────────────┐
│                                                       │
│              FASTAPI MONOLITH (Docker)                │
│                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ Vitals   │ │ Scoring  │ │ Alerting │              │
│  │ Endpoint │ │ Engine   │ │ Engine   │              │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘              │
│       │             │            │                     │
│  ┌────▼─────────────▼────────────▼─────┐              │
│  │         Service Layer                │              │
│  │  (idempotency, validation, audit)    │              │
│  └────┬─────────────┬─────────────┬────┘              │
│       │             │             │                    │
│  ┌────▼────┐  ┌─────▼──────┐ ┌───▼──────┐            │
│  │PostgreSQL│  │   Redis    │ │  ARQ/RQ  │            │
│  │Timescale │  │ cache+queue│ │  Worker  │            │
│  └─────────┘  └────────────┘ └──────────┘            │
│                                                       │
└──────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│              REVERSE PROXY (Caddy/Nginx)               │
│              TLS + Rate Limiting + Logs                │
└──────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────┐
│          CLIENTES: Web App + WhatsApp/SMS             │
└──────────────────────────────────────────────────────┘
```

---

## 7. Recomendações Finais

### O que está certo na proposta:

1. **Monólito modular em FastAPI** — decisão correta. Organizar o código em módulos (`vitals/`, `scoring/`, `alerts/`, `patients/`) com interfaces internas bem definidas facilita a extração para microsserviços no futuro, se necessário.

2. **PostgreSQL + TimescaleDB** — escolha ideal para workload híbrido (time-series + relacional + JSONB semi-estruturado para HL7/FHIR).

3. **Redis na stack** — cobre cache, filas de trabalho, rate limiting e sessões com uma única tecnologia operacionalmente simples.

4. **Docker Compose, não Kubernetes** — para 1–3 UTIs, K8s é complexidade que rouba tempo de validação clínica. O custo de operação de K8s (manutenção de cluster, upgrades, troubleshooting de CNI/CSI) é subestimado por times que nunca operaram K8s em produção.

5. **Deferir Kafka para Fase 2** — correto. O custo operacional do Kafka (3 brokers + ZooKeeper/KRaft, monitoramento de consumer lag, rebalance de partições) não se justifica para volume de MVP.

### O que precisa ser ajustado:

1. **⚠️ Gap MLLP/HL7 v2** — FastAPI sozinho não recebe HL7 por MLLP. Incluir um MLLP listener no MVP (container separado no mesmo Docker Compose). Sem isso, a integração com monitores reais é inviável.

2. **⚠️ Trilha de auditoria desde o dia 1** — implementar triggers de auditoria e tabela `audit_trail` antes da primeira ingestão de dados de paciente. Não dá para "adicionar depois" — é ilegal operar sem isso.

3. **⚠️ Testar com HL7 real de hospital brasileiro** — o README tem fixtures de exemplo genéricos. Hospitais brasileiros (especialmente via Tasy/MV) têm convenções próprias de segmentos Z (Z-segments). O MVP precisa ser validado com pelo menos 48h de tráfego HL7 real do hospital piloto.

### Stack final recomendada para o MVP:

```
MVP Core:
  ├── FastAPI (API principal + scoring engine)
  ├── MLLP Listener (Python asyncio, container separado)
  ├── PostgreSQL 16 + TimescaleDB 2.x
  ├── Redis 7.x (cache, queue, rate limiting)
  ├── ARQ (async task queue sobre Redis)
  ├── Caddy (reverse proxy, TLS automático)
  
Monitoramento (leve):
  ├── Prometheus (metrics pull)
  └── Grafana (dashboards, opcional no MVP)
  
Infra:
  └── Docker Compose (single-host)
  
Não incluir no MVP:
  ├── Kafka, Flink, ONNX, NiFi
  ├── Kubernetes, Linkerd
  ├── Keycloak, Vault
  └── ELK, MinIO
```

---

## 8. Conclusão

A simplificação proposta é **clinicamente responsável e tecnicamente sólida** para um MVP focado em 1–3 UTIs. O princípio de "simplificar radicalmente e iterar com feedback clínico real" é o caminho correto para healthtech — é preferível ter um monólito funcional que entrega alertas corretos em 48h do que uma plataforma de 12 componentes que nunca sai do staging.

Os três riscos que exigem ação imediata:
1. **Resolver o gap MLLP** antes da integração hospitalar.
2. **Implementar trilha de auditoria** antes de processar dados reais de pacientes.
3. **Validar com tráfego HL7 real** do hospital piloto brasileiro, incluindo segmentos Z específicos do ecossistema Tasy/MV/Soul MV.

Se esses três pontos forem endereçados, o MVP tem condições de iniciar um piloto clínico com segurança e conformidade regulatória adequadas para o estágio de maturidade do produto.
