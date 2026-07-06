# Intensicare — Relatório de Impacto à Proteção de Dados (RIPD)

**Versão:** 1.0.0
**Data:** 2026-07-06
**Work Order:** WO-039 — Fase 3
**Regulamento:** Lei Geral de Proteção de Dados Pessoais (LGPD — Lei nº 13.709/2018)
**Referência normativa:** ISO 27701:2019 (Privacy Information Management)
**Controlador de dados:** [Instituição de Saúde contratante]
**Operador de dados:** Intensicare (plataforma SaaS)

---

## 1. Identificação do Tratamento

### 1.1 Descrição do Tratamento

O Intensicare processa dados pessoais sensíveis (dados de saúde) de pacientes
internados em UTI para:

1. **Monitoramento contínuo**: Coleta de sinais vitais em tempo real via HL7/MLLP.
2. **Cálculo de scores clínicos**: MEWS, NEWS2, SOFA, qSOFA para detecção precoce
   de deterioração.
3. **Geração de alertas**: Notificações para equipe clínica sobre pacientes em risco.
4. **Armazenamento histórico**: Série temporal de dados vitais para análise clínica
   retrospectiva.
5. **Interoperabilidade**: Sincronização com MPI (Master Patient Index) e FHIR.

### 1.2 Natureza e Escopo

| Característica | Descrição |
|----------------|-----------|
| **Volume de titulares** | Dependente da instituição (estimativa: 500-2000 pacientes/ano por UTI) |
| **Frequência** | Contínua (24×7, ingestão a cada 1-5 minutos por leito) |
| **Duração** | Indeterminada (retenção configurável por tenant) |
| **Abrangência geográfica** | Brasil (ANVISA) — dados armazenados em AWS us-east-1, backup us-west-2 |
| **Base legal** | Art. 7º IV — Proteção da vida/incolumidade física; Art. 11º II — Obrigação legal/regulatória (RDC 686/2022) |

---

## 2. Dados Pessoais Tratados

### 2.1 Categorias de Titulares

| Titular | Categoria |
|---------|-----------|
| Pacientes UTI | Dados sensíveis (saúde) |
| Profissionais de saúde | Dados pessoais (identificação, credenciais, logs de acesso) |
| Administradores do sistema | Dados pessoais (identificação, credenciais IAM) |

### 2.2 Dados de Pacientes (PHI — Protected Health Information)

| Dado | Categoria | Criptografado | Retenção |
|------|-----------|---------------|----------|
| Nome completo | Identificação direta | ✅ pgcrypto | Configurável (default: 20 anos) |
| CPF/CNS (Cartão Nacional de Saúde) | Identificação unívoca | ✅ pgcrypto | Configurável |
| Data de nascimento | Identificação indireta | ✅ pgcrypto | Configurável |
| Número de prontuário (MRN) | Identificação clínica | Blind-index somente | Configurável |
| Sinais vitais (FC, FR, PA, SpO₂, Temp) | Dado clínico | ❌ (não-PHI, necessário para scores) | 20 anos (TimescaleDB) |
| Resultados laboratoriais | Dado clínico sensível | ✅ pgcrypto (PHI fields) | 20 anos |
| Medicações administradas | Dado clínico sensível | ✅ pgcrypto (PHI fields) | 20 anos |
| Scores clínicos (MEWS, NEWS2, etc.) | Dado derivado | ❌ (agregado, não-PHI) | 20 anos |
| Eventos de correlação clínica | Dado derivado | ✅ pgcrypto (se referencia PHI) | 20 anos |

### 2.3 Dados de Profissionais de Saúde

| Dado | Categoria | Finalidade |
|------|-----------|------------|
| Nome de usuário | Identificação | Autenticação SSO (IAM Identity Center) |
| Email institucional | Identificação | Notificações de alerta |
| Role clínico | Autorização | ABAC (controle de acesso baseado em atributos) |
| Tenant ID | Vinculação institucional | Isolamento multi-tenant |
| Timestamps de acesso | Auditoria | `audit_trail` imutável |

---

## 3. Medidas de Segurança Técnicas (Art. 46 LGPD)

### 3.1 Criptografia

| Camada | Tecnologia | Detalhe |
|--------|-----------|---------|
| **Dados em repouso** | pgcrypto (AES-256-GCM) | PHI criptografada no PostgreSQL com chave por tenant injetada via GUC `app.encryption_key` |
| **Chaves de criptografia** | AWS KMS (envelope encryption) | CMK multi-region no HSM → DEK por tenant → pgcrypto |
| **Dados em trânsito** | TLS 1.3 | API Gateway / Application Load Balancer |
| **WAL (Write-Ahead Log)** | KMS encryption | Logs do TimescaleDB criptografados em repouso e em trânsito (cross-region) |

✅ **Evidência:** `src/intensicare/services/patient_encryption.py`, `src/intensicare/services/kms_keys.py`

### 3.2 Controle de Acesso

| Mecanismo | Descrição |
|-----------|-----------|
| **Autenticação SSO** | IAM Identity Center (OIDC) — MFA obrigatório, senhas nunca trafegam para a aplicação |
| **Autorização ABAC** | Políticas baseadas em atributos (tenant, role, grupo clínico, recurso, ação) |
| **Isolamento multi-tenant** | Cada tenant possui DEK própria; dados de diferentes instituições jamais compartilham chave |
| **Segregação de funções** | ABAC impede que papel "viewer" acesse PHI ou escreva dados |
| **Menor privilégio** | Roles clínicos recebem apenas as permissões necessárias (ex: farmacêutico só vê medicamentos) |
| **Trilha de auditoria** | Toda ação (create/read/update/delete) registrada em `audit_trail` imutável |

✅ **Evidência:** `src/intensicare/auth/iam.py`, `src/intensicare/auth/abac.py`, `src/intensicare/models/audit_trail.py`

### 3.3 Resiliência e Disponibilidade

| Medida | Descrição |
|--------|-----------|
| **Multi-AZ** | Aurora/TimescaleDB com read replicas em múltiplas AZs |
| **Multi-Região (DR)** | RPO 1h, RTO 1h documentados em `infrastructure/dr/dr_drill_plan.md` |
| **Dead-man switch** | Watchdog externo (CloudWatch Lambda) que alerta se o sistema parar de responder |
| **WAL Archiving** | Logs de transação replicados cross-region via S3 |
| **ECR Replication** | Imagens Docker replicadas para região secundária |

✅ **Evidência:** `infrastructure/dr/dr_drill_plan.md`, `infrastructure/dr/dr_drill.py`

### 3.4 Privacidade por Design (Art. 46 §2º)

| Princípio | Implementação |
|-----------|---------------|
| **Minimização** | Somente dados necessários para scores clínicos são processados em texto plano |
| **Pseudonimização** | MRN armazenado como blind-index (HMAC-SHA256) — busca sem descriptografar |
| **Transparência** | Trilha de auditoria registra todo acesso a PHI (who, when, what, why) |
| **Não-vinculação** | Dados de diferentes tenants isolados criptograficamente (DEKs distintas) |
| **Age derivation** | Idade calculada a partir de data de nascimento criptografada, sem expor texto plano |

✅ **Evidência:** `src/intensicare/services/patient_encryption.py` (funções `compute_mrn_bidx`, `age_derivation`)

---

## 4. Direitos dos Titulares (Arts. 17-22 LGPD)

| Direito | Como o Intensicare atende |
|---------|--------------------------|
| **Confirmação e Acesso (Art. 18, I-II)** | `GET /api/v1/patients/{id}` — dados do paciente (com decrypt on-the-fly) |
| **Correção (Art. 18, III)** | `PUT /api/v1/patients/{id}` — atualização de dados via interface autorizada |
| **Anonimização/Bloqueio/Eliminação (Art. 18, IV)** | Dead-man switch permite destruição criptográfica (delete da DEK = dados inacessíveis) |
| **Portabilidade (Art. 18, V)** | Exportação FHIR R4 (formato interoperável padrão) |
| **Informação sobre compartilhamento (Art. 18, VII)** | `audit_trail` registra toda comunicação externa (FHIR, MPI) |
| **Revogação de consentimento (Art. 18, IX)** | DEK pode ser destruída para tornar dados permanentemente inacessíveis |
| **Oposição (Art. 18, §2º)** | Bloqueio lógico via flag `is_active=False` no cache de paciente |

---

## 5. Análise de Riscos (Art. 5º LGPD)

### 5.1 Matriz de Risco

| Risco | Probabilidade | Impacto | Mitigação | Risco Residual |
|-------|--------------|---------|-----------|----------------|
| Acesso não autorizado a PHI | Baixa | Muito Alto | IAM IC + ABAC + KMS + audit trail | Baixo |
| Vazamento de dados em trânsito | Muito Baixa | Muito Alto | TLS 1.3, mTLS para HL7 | Muito Baixo |
| Corrupção/perda de dados | Baixa | Alto | Multi-AZ, WAL archiving, backup cross-region | Baixo |
| Acesso por administrador malicioso | Muito Baixa | Crítico | Blind-index, KMS envelope, audit trail imutável, dead-man switch | Baixo |
| Violação de tenant isolation | Muito Baixa | Crítico | DEK por tenant (KMS), GUC isolation por sessão PostgreSQL | Muito Baixo |
| Indisponibilidade prolongada do sistema | Baixa | Alto | DR multi-region, RTO 1h | Baixo |
| Não conformidade regulatória (ANVISA/LGPD) | Baixa | Alto | RIPD documentado, evidências técnicas, ANVISA checklist | Baixo |

### 5.2 Cenários de Incidente e Resposta

**Cenário 1: Comprometimento de credenciais de profissional de saúde**
- **Detecção**: `audit_trail` mostra padrão anômalo de acesso (fora de horário, volume anormal).
- **Resposta**: Revogar token IAM IC → invalidar sessões → alertar CSO.
- **Notificação**: ANPD e titular em até 72h (se risco relevante).

**Cenário 2: Acesso indevido cross-tenant**
- **Detecção**: `ABACAccessDenied` no log + alerta de segurança.
- **Resposta**: Bloquear tenant ofensor → investigar `audit_trail` → corrigir ABAC policy.
- **Notificação**: ANPD em até 72h se dados de outro tenant foram expostos.

**Cenário 3: Perda de chave KMS**
- **Detecção**: `KMSKeyError` ao tentar descriptografar DEK.
- **Resposta**: KMS MRK replica na região secundária → promover réplica.
- **Notificação**: Não requer notificação se nenhum dado foi exposto (apenas indisponível).

---

## 6. Dead-Man Switch Criptográfico (Mecanismo de Destruição)

O Intensicare implementa um **dead-man switch criptográfico** como mecanismo
de destruição de dados em cenários extremos (ex: ordem judicial, violação massiva):

1. **CMK raiz** no KMS é a única capaz de descriptografar as DEKs dos tenants.
2. Se a CMK for **deletada** (com waiting period de 7-30 dias):
   - Todas as DEKs criptografadas tornam-se permanentemente inacessíveis.
   - Todos os dados PHI armazenados tornam-se irrecuperáveis (ciphertext sem chave).
   - Dados não-PHI (scores, logs) permanecem acessíveis para auditoria.
3. O dead-man switch (INV-5) monitora a saúde do sistema e pode disparar
   a destruição criptográfica se configurado para tal.

⚠️ **Atenção**: Este mecanismo é irreversível. Requer aprovação de 2-of-3
signatários (CSO, Clinical Lead, Legal) para ser acionado.

✅ **Evidência:** `src/intensicare/services/kms_keys.py`, `config.py` (watchdog_timeout_seconds)

---

## 7. Transferência Internacional (Art. 33 LGPD)

| Aspecto | Descrição |
|---------|-----------|
| **Localização dos dados** | AWS us-east-1 (Virgínia, EUA) — primário; us-west-2 (Oregon, EUA) — DR |
| **Fundamento legal** | Art. 33, IX — Cláusulas-padrão contratuais + certificações (AWS ISO 27001/27701) |
| **Garantias** | AWS é signatária do CISPE Code of Conduct; dados criptografados com chaves sob controle do cliente (CMK no KMS) |
| **País de destino** | Estados Unidos (adequado conforme decisão de adequação da ANPD, se existente, ou cláusulas-padrão) |

---

## 8. Responsabilidades (Art. 37 e 41 LGPD)

| Papel | Responsável | Contato |
|-------|------------|---------|
| **Controlador** | Instituição de saúde contratante | A definir (contrato) |
| **Operador** | Intensicare (plataforma) | dpo@intensicare.io |
| **DPO (Data Protection Officer)** | A designar | dpo@intensicare.io |
| **CSO (Chief Security Officer)** | Responsável técnico pela segurança | cso@intensicare.io |

---

## 9. Revisão e Atualização

| Versão | Data | Alteração | Autor |
|--------|------|-----------|-------|
| 1.0.0 | 2026-07-06 | Versão inicial (Fase 3 — WO-039) | Equipe Intensicare |
| Próxima | TBD | Incluir resultados do estudo de validação clínica | — |

---

## 10. Aprovações

| Função | Nome | Data | Assinatura |
|--------|------|------|------------|
| CSO | _________ | __/__/____ | _________ |
| Clinical Lead | _________ | __/__/____ | _________ |
| DPO | _________ | __/__/____ | _________ |
| Legal | _________ | __/__/____ | _________ |
