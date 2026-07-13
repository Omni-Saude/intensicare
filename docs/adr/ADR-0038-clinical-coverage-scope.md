# ADR-0038: Escopo de Cobertura Clínica — Decisões Conscientes de Fora-de-Escopo

**Status:** accepted
**Data:** 2026-07-12
**Decisão por:** Orquestração pós-auditoria + sign-off intensivista (`CLINICAL_SIGNOFF.md`)

---

## Contexto

A auditoria full-spectrum, Dimensão E — Inovação (`docs/audit/fullspectrum/DIM_E_INNOVATION.md`), aplicou dedução de **-6 pontos** (item 4 da tabela de scoring, linha 158) com o seguinte achado:

> "Gaps de cobertura clínica não documentados como decisão consciente: ausência total de glicemia e transfusão; PAV cobre só 1 elemento de bundle; profilaxia de TEV/UGE são checagens booleanas sem estratificação de risco (sem Padua/IMPROVE)."

O ponto central do achado (`DIM_E_INNOVATION.md:143`) não é que esses dados estejam ausentes — é que sua ausência **não está documentada como decisão consciente**: *"não há uma seção de docs que diga 'sabemos que faltam glicemia e transfusão, decisão consciente de não incluir no MVP'. Isso os torna mais próximos de omissão não documentada do que de gap conscientemente aceito."* A mesma auditoria (§4.3, `DIM_E_INNOVATION.md:114-121`) já reconhece que a ausência de ML é uma escolha deliberada e bem fundamentada (ADR-0023) — o objetivo desta ADR é dar aos gaps de **cobertura clínica** o mesmo tratamento: uma decisão nomeada, com razão técnica verificável e gatilho de reavaliação, em vez de silêncio.

Esta ADR não decide "implementar" ou "não implementar" cada gap por preferência de produto — ela documenta o que **investigação do schema e do pipeline de ingestão atual** (models SQLAlchemy, HL7/MLLP listener, cliente FHIR) mostra estar realmente disponível hoje, e o que exigiria trabalho de ingestão/schema ainda não feito. Nenhuma escolha aqui é definitiva; cada linha da tabela da Seção 2 tem um gatilho de reavaliação explícito.

### Investigação — dado exigido pelo Padua score vs. dado persistido hoje

O [Padua Prediction Score](https://doi.org/10.1160/TH10-08-0521) (11 itens de risco de TEV) foi usado como sonda de profundidade porque é o gap mais citado pela auditoria. Investigação direta do código (modelos SQLAlchemy em `src/intensicare/models/`, HL7 listener em `src/intensicare/mllp_listener.py`, cliente FHIR em `src/intensicare/fhir/client.py`, serviços de domínio em `src/intensicare/services/`):

| Item Padua | Existe hoje? | Evidência |
|---|---|---|
| Idade ≥ 70 | **Sim** — derivável, não persistido em claro | `src/intensicare/services/patient_encryption.py:128` `age_derivation()` decripta `patient_cache.birth_date` (`src/intensicare/models/patient_cache.py:41`) e calcula idade em tempo de consulta |
| Câncer ativo | **Não existe** | Nenhuma coluna em `patient_cache.py`, `pathway.py`, `clinical_score.py`, `deterioration.py`; string "câncer" não ocorre em nenhum model |
| TEV prévio (TVP/TEP) | **Não existe** | Idem — nenhum campo estruturado de histórico clínico em nenhum model |
| Mobilidade reduzida | **Não existe estruturado** | `_work/alerts/pathways/profilaxia.yaml:56` tem `mobilizacao_status` (booleano "mobilização precoce foi feita hoje?"), que é o oposto semântico de um fator de risco de admissão ("paciente está acamado há ≥3 dias") |
| Trombofilia conhecida | **Não existe** | Nenhuma coluna/campo em nenhum model |
| Trauma/cirurgia recente (≤1 mês) | **Não existe estruturado** | Texto livre em formulários de evolução (`services/domain_evolucoes.py`), nunca campo estruturado consultável |
| Insuficiência cardíaca/respiratória | **Parcial via proxy clínico, não via flag de comorbidade** | `VitalSign` tem `pao2_fio2`, `map_value`, `vasopressor_dose_mcg_kg_min` (`models/vital_sign.py:42-48`) — sinais de disfunção aguda usados pelas trilhas `respiratorio.yaml`/`estabilidade.yaml`, mas não um flag booleano "ICC/DPOC conhecida" |
| IAM/AVC recente | **Não existe** | Nenhum campo |
| Infecção aguda/doença reumatológica | **Parcial via proxy** | Trilha `sepse.yaml` infere infecção suspeita a partir de critérios SIRS/qSOFA; não é um flag de comorbidade reumatológica |
| Obesidade (IMC ≥ 30) | **Não existe valor, só rótulo de checklist** | `services/domain_profilaxia.py:58` — critério `tev-imc` = *"Ajuste para IMC > 40"* é um booleano de protocolo-seguido, não um valor numérico de peso/altura/IMC persistido |
| Terapia hormonal (contraceptivo/reposição) | **Não existe** | Nenhum campo em nenhum model |

**Conclusão da investigação (Padua):** dos 11 itens, **1 é derivável hoje** (idade, via decriptação de `birth_date`) e **10 não têm dado estruturado persistido em lugar algum do schema atual** — nem como coluna dedicada, nem como campo JSONB genérico de comorbidades. Não existe hoje nenhum modelo de "admissão estruturada" (histórico prévio, comorbidades codificadas, antropometria) — o que existe é cache demográfico (`patient_cache.py`) e formulários de evolução em texto livre (`domain_evolucoes.py`). **Implementar Padua hoje exigiria criar um novo modelo de dados e um novo caminho de captura (formulário estruturado de admissão ou ingestão de histórico codificado) — não é um ajuste de threshold em um input já existente.** Por isso a Tarefa 3 desta investigação (adicionar critério a YAML) não se aplica a Padua: não há dado a consumir.

### Investigação — glicemia e transfusão (Hb)

| Dado | Existe hoje? | Evidência |
|---|---|---|
| Glicemia (capilar ou laboratorial) | **Não existe caminho de ingestão** | `mllp_listener.py:59-68` `LOINC_VITAL_MAP` mapeia só 8 códigos (FC, PAS, PAD, temperatura, SpO₂×2, FR, AVPU) — nenhum LOINC de glicemia (2339-0/2345-7/41653-7); OBX não mapeado é descartado (`mllp_listener.py:295-301`, `logger.debug("...unmapped identifier... skipping")`). `LabResult` (`models/lab_result.py`) é genérica (`loinc_code`+`analyte`+`value_num`, sem whitelist), mas nenhum job em `src/` persiste `FHIRLabResult` (`fhir/client.py`) nessa tabela — o único uso é enriquecimento transitório de API (`services/patients.py`), não persistência. `services/domain_profilaxia.py:82,84` tem critérios `hg-meta`/`hg-monitor` — são checklists booleanos "protocolo de meta 140-180 mg/dL seguido?", não o valor de glicemia em si |
| Hemoglobina / transfusão | **Não existe caminho de ingestão** | Nenhum LOINC 718-7 em qualquer lugar de `src/`. `hb_pre`/`hb_post` existem em `services/domain_eficiencia.py:277-300,342` como chaves de um dict de input manual (`transfusion_inputs`, `api/v1/efficiency.py:109`) — a função `evaluate_transfusion_criteria()` já teria a **lógica clínica** pronta (gatilho restritivo Hb < 7,0 g/dL, linha 291) se o dado chegasse, mas hoje só chega via payload manual de chamada de API, nunca de um feed de laboratório |

**Conclusão da investigação (glicemia/transfusão):** o gargalo é idêntico para ambos e é de **ingestão**, não de lógica de negócio ou de schema de trilha: `LabResult` já é uma tabela genérica capaz de armazenar qualquer LOINC, e `evaluate_transfusion_criteria()` já implementa o gatilho restritivo de Hb — mas nenhum processo hoje escreve linhas em `lab_result` a partir de FHIR/HL7, e o whitelist do listener HL7 explicitamente não inclui glicemia. **Nenhum dos dois tem dado persistido hoje — a Tarefa 3 desta investigação (adicionar critério ao YAML) portanto não se aplica: não há coluna nem linha de tabela para o motor de trilhas consumir.**

---

## Decisão

Documentar formalmente, nesta ADR, a cobertura clínica atual das 12 trilhas e nomear cada gap de cobertura relevante como **decisão consciente de fora-de-escopo**, com razão técnica (não de preferência), dado faltante específico e gatilho objetivo de reavaliação — fechando o padrão de omissão não documentada apontado pela auditoria (Dim E, dedução -6). Nenhum código de produção é alterado por esta ADR: a investigação confirmou que nenhum dos gaps identificados (glicemia, transfusão, Padua/IMPROVE) tem dado persistido hoje que permita implementação imediata de um critério em YAML sem trabalho prévio de ingestão/schema.

### 1. Cobertura atual — 12 trilhas

| # | Trilha (`_work/alerts/pathways/*.yaml`) | Cobre (1 linha) |
|---|---|---|
| 1 | `sepse.yaml` | Triagem qSOFA/SIRS + infecção, disfunção orgânica, bundle 1h/3h (antibiótico, culturas), conforme SSC-2021 |
| 2 | `renal.yaml` | Creatinina, débito urinário, estadiamento KDIGO 2012 e indicação de TRS |
| 3 | `respiratorio.yaml` | Oxigenação (SpO₂, PaO₂/FiO₂), ventilação (PaCO₂, FR) e suporte (VNI/VM) em IRpA |
| 4 | `delirium.yaml` | Screening CAM-ICU + nível de sedação RASS, manejo não farmacológico/farmacológico (PADIS 2018) |
| 5 | `sedacao.yaml` | RASS diário, adequação de sedação, prevenção de sedação excessiva, interrupção diária (PADIS) |
| 6 | `ventilacao.yaml` | Parâmetros de proteção ventilatória (ARDSNet/PROSEVA) |
| 7 | `desmame.yaml` | Prontidão para desmame, teste de respiração espontânea, extubação, monitorização pós-extubação |
| 8 | `nutricao.yaml` | Triagem nutricional, progressão de dieta enteral até meta calórico-proteica, tolerância |
| 9 | `profilaxia.yaml` | Checklist booleano de TEV, úlcera de estresse, mobilização precoce e cabeceira elevada (sem escore de risco) |
| 10 | `antimicrobiano.yaml` | Stewardship: duração de antibioticoterapia, revisão diária, descalonamento guiado por PCT/culturas |
| 11 | `equilibrio.yaml` | Distúrbios de sódio, potássio, magnésio, cálcio iônico e fósforo, reposição guiada por protocolo |
| 12 | `estabilidade.yaml` | PAM, FC, perfusão tecidual (lactato) e uso de vasopressores (SSC/ESICM) |

### 2. FORA DE ESCOPO CONSCIENTE — e por quê

| Gap | Razão (técnica, não preferência) | Dado faltante específico | Gatilho de inclusão |
|---|---|---|---|
| **Glicemia / controle glicêmico** | Nenhum caminho de ingestão persiste valores de glicemia hoje: LOINC de glicemia não está no whitelist do listener HL7 (`mllp_listener.py:59-68` `LOINC_VITAL_MAP`), e nenhum job persiste `LabResult` a partir do cliente FHIR genérico (`fhir/client.py`) — a tabela existe (`models/lab_result.py`) mas fica vazia | `LabResult.value_num` com `loinc_code` de glicemia (2339-0 sangue total, 2345-7 soro/plasma, 41653-7 capilar POC) | Quando o pipeline de ingestão de glicemia (POC capilar ou laboratorial) estiver ativo — adicionar o(s) LOINC(s) ao `LOINC_VITAL_MAP` do listener HL7 e/ou implementar o job de persistência `FHIRLabResult → LabResult` que hoje não existe |
| **Transfusão / anemia (gatilho transfusional)** | Mesmo gargalo de ingestão da glicemia — a lógica clínica já existe (`services/domain_eficiencia.py:evaluate_transfusion_criteria`, gatilho restritivo Hb < 7,0 g/dL) mas só recebe `hb_pre`/`hb_post` via payload manual de API (`transfusion_inputs`, `api/v1/efficiency.py:109`), nunca de um feed de laboratório | `LabResult.value_num` com `loinc_code` 718-7 (hemoglobina) | Quando a ingestão automatizada de hemograma/Hb estiver ativa — mesma mudança de pipeline listada acima para glicemia, aplicada ao LOINC 718-7 |
| **Padua / IMPROVE (estratificação de risco de TEV em `profilaxia.yaml`)** | Requer 10 dos 11 fatores de risco como dado estruturado de comorbidade/histórico/antropometria (câncer ativo, TEV prévio, trombofilia, trauma/cirurgia recente, ICC/DPOC conhecida, IAM/AVC recente, doença reumatológica, IMC, terapia hormonal) — nenhum existe hoje em `patient_cache.py`, `pathway.py`, `clinical_score.py` ou `deterioration.py`; apenas idade ≥70 é derivável (`services/patient_encryption.py:128` `age_derivation()`) | Modelo de admissão estruturada (comorbidades codificadas, peso/altura/IMC, histórico de TEV) — não existe hoje nenhum model equivalente | Quando existir captura estruturada de dados de admissão (formulário clínico dedicado via `clinical_form.py` ou ingestão de histórico codificado do MPI/AMH) — então adicionar critério `graded` de score Padua a `profilaxia.yaml`, com bandas de risco (baixo/alto ≥4 pontos) por cima da checagem booleana já existente |
| **PAV — bundle completo (higiene oral, pressão de cuff, vigilância dedicada)** | Hoje só um elemento do bundle está implementado (cabeceira elevada, `profilaxia.yaml:66-86`); higiene oral e pressão de cuff não têm input mapeado em nenhum model, e uma trilha de vigilância de PAV exigiria dado de ventilação (`VitalSign.mechanical_ventilation`, existente) pareado com resultado de cultura microbiológica estruturado, que não existe (culturas hoje só aparecem como status booleano em `antimicrobiano.yaml`, não como resultado de microrganismo/sensibilidade) | Input estruturado de higiene oral e pressão de cuff (cmH₂O) + `LabResult`/model de cultura microbiológica pareável a `mechanical_ventilation` | Quando existir captura estruturada de cuidados de PAV (checklist de enfermagem além do booleano atual) e ingestão de resultado de cultura microbiológica estruturado |
| **Dor (CPOT)** | CPOT é citado apenas como texto livre dentro de `sedacao.yaml:139` (`evidence.recommendations`), nunca implementado como input de critério; BPS é mencionado mas também não é um input do motor de trilhas | Input estruturado de escala de dor (CPOT 0-8 ou BPS 3-12) por avaliação de enfermagem | Quando o motor de formulários clínicos dinâmicos (`services/clinical_form.py`, já usado para evoluções) for estendido com um formulário de avaliação de dor estruturado, alimentando um novo `input` em `sedacao.yaml` ou trilha dedicada |

### 3. Roadmap de inclusão (priorizado)

1. **Glicemia** — maior volume de pacientes-dia impactados, protocolo já bem padronizado (meta 140-180 mg/dL, já citado como checklist em `domain_profilaxia.py:82`), e o esforço é isolado a um único ponto de ingestão (adicionar LOINC ao `LOINC_VITAL_MAP` do listener HL7 e/ou implementar o job `FHIRLabResult → LabResult`). Menor esforço, maior valor clínico imediato.
2. **Dor (CPOT)** — reaproveita infraestrutura já existente (`services/clinical_form.py`, motor de formulário dinâmico já usado em evoluções), não exige novo modelo de dados nem novo pipeline de ingestão externa — apenas um novo formulário estruturado e um novo `input` em `sedacao.yaml`.
3. **Transfusão / Hb** — mesmo gargalo técnico da glicemia (pipeline de labs), lógica clínica de gatilho restritivo já implementada e testada em `domain_eficiencia.py`; falta apenas a mesma mudança de ingestão listada para glicemia, aplicada ao LOINC 718-7.
4. **Padua/IMPROVE** — maior esforço: exige um novo modelo de dados de admissão estruturada (comorbidades, antropometria, histórico) e um novo caminho de captura (formulário ou ingestão de histórico codificado), antes de qualquer mudança em `profilaxia.yaml`.
5. **PAV completo** — maior esforço combinado (captura de cuidados de enfermagem + ingestão de cultura microbiológica estruturada pareável a ventilação); depende de dado de microbiologia que hoje não tem modelo dedicado no schema.

---

## Alternativas Consideradas

### Alternativa A: Implementar glicemia e transfusão imediatamente via campo hardcoded/simulado
- **Prós:** fecharia a dedução de auditoria mais rapidamente, com uma trilha "funcionando" no YAML.
- **Contras:** sem pipeline de ingestão real, o critério ficaria sempre `na`/sem dado, ou pior, exigiria input manual não escalável — criaria a aparência de cobertura sem cobertura real, o que é mais perigoso em patient-safety do que a ausência documentada (falso senso de segurança).
- **Rejeitada porque:** a auditoria já penalizou "TEV/UGE são checagens booleanas" (item 4, -6) — adicionar mais um critério que também não reflete um dado real medido pioraria a fidelidade clínica em vez de melhorá-la.

### Alternativa B: Implementar Padua com os fatores de risco parcialmente disponíveis (só idade) e marcar os demais como "não avaliável"
- **Prós:** entregaria uma trilha Padua "parcial" hoje.
- **Contras:** o Padua Score é validado como escore de 11 itens somados — um score computado com 1 de 11 itens sub-representa sistematicamente o risco real (a maioria dos pacientes de alto risco tem múltiplos fatores concomitantes), podendo classificar erroneamente pacientes de alto risco como baixo risco. Isso é pior do que não ter o score.
- **Rejeitada porque:** um escore clinicamente inválido com aparência de escore validado é um risco de segurança do paciente maior do que a ausência do escore, mais ainda em um produto que se posiciona (ADR-0023) como dependente de racional clínico explicável e completo.

### Alternativa C: Documentar os gaps sem tabela estruturada, apenas texto narrativo (como já existe difuso em `docs/audit/fullspectrum/DIM_E_INNOVATION.md`)
- **Prós:** menor esforço de redação.
- **Contras:** o próprio achado da auditoria é que o gap **não está em um documento de decisão de produto** — um achado de auditoria não substitui uma ADR: não tem status `accepted`, não fica no diretório canônico de decisões (`docs/adr/`), e não é o lugar que a equipe de produto/roadmap consulta para saber "o que está fora do MVP e por quê" (que é exatamente como o gap de ML foi tratado, via ADR-0023, não apenas via achado de auditoria).
- **Rejeitada porque:** a decisão explícita da auditoria (`DIM_E_INNOVATION.md:186`) é "fechar gaps de cobertura documentados como decisão, não como silêncio" — o veículo correto para isso, seguindo o precedente do próprio produto (ADR-0023 para o gap de ML), é uma ADR.

---

## Consequências

### Positivas
- O gap de cobertura clínica (glicemia, transfusão, Padua/IMPROVE, PAV completo, dor/CPOT) passa a ter o mesmo nível de reconhecimento explícito que o gap de ML (ADR-0023) — fechando a lacuna apontada pela dedução -6 da Dimensão E.
- Cada gap tem um gatilho de inclusão objetivo e verificável (não "quando tivermos tempo"), amarrado a uma mudança de pipeline ou schema específica e nomeada.
- O roadmap prioriza pelo critério real de esforço técnico verificado (não intuição): glicemia e dor são os menores esforços porque reaproveitam infraestrutura existente (tabela `LabResult` genérica, motor `clinical_form.py`); Padua e PAV são os maiores porque exigem novo modelo de dados.

### Negativas
- Nenhum dos gaps é fechado por esta ADR — a dedução de auditoria original era sobre *documentação ausente*, não sobre *funcionalidade ausente*; a funcionalidade continua ausente até que os gatilhos de inclusão sejam satisfeitos.
- O roadmap da Seção 3 não tem compromisso de cronograma (sprints/datas) — é uma priorização relativa, não um plano de entrega comprometido.

### Riscos e Mitigações
- **Risco:** esta ADR ser lida como "decisão de nunca implementar" em vez de "decisão consciente de adiar até o gatilho" → **Mitigação:** cada linha da Seção 2 tem gatilho de inclusão explícito e verificável por código (não por data), reavaliável a qualquer momento em que o pipeline de ingestão mudar.
- **Risco:** um novo pipeline de ingestão de labs ser implementado (ex. para outro propósito) e o gatilho de glicemia/Hb ficar satisfeito sem que ninguém atualize `profilaxia.yaml`/nova trilha → **Mitigação:** próxima auditoria ou revisão de ADR deve checar se `LOINC_VITAL_MAP`/job de persistência de `LabResult` mudou desde 2026-07-12, e se sim, reabrir esta ADR para superseder a linha correspondente.

---

## Referências

- `docs/audit/fullspectrum/DIM_E_INNOVATION.md:143,151-165` — achado original (dedução -6) que motiva esta ADR
- `docs/audit/fullspectrum/DIM_E_INNOVATION.md:57-65` — tabela de domínios de cobertura clínica esperados vs. presentes nos 12 YAMLs
- `_work/alerts/pathways/profilaxia.yaml` — trilha de profilaxia atual (checklist booleano de TEV/UGE/mobilização/cabeceira)
- `src/intensicare/mllp_listener.py:59-68,295-301` — `LOINC_VITAL_MAP` do listener HL7/MLLP e descarte de OBX não mapeado
- `src/intensicare/fhir/client.py` — cliente FHIR R4, `FHIRLabResult.from_observation` (genérico, sem persistência automática)
- `src/intensicare/models/lab_result.py` — tabela `LabResult` (genérica, LOINC-agnóstica, hoje sem job de escrita)
- `src/intensicare/models/vital_sign.py` — tabela `VitalSign` (campos de score SOFA/qSOFA já presentes; sem glicemia/Hb)
- `src/intensicare/models/patient_cache.py:30-75` — cache demográfico; sem campos de comorbidade estruturada
- `src/intensicare/services/patient_encryption.py:128` — `age_derivation()`, único item Padua derivável hoje
- `src/intensicare/services/domain_eficiencia.py:247-349` — `evaluate_transfusion_criteria()`, lógica de gatilho restritivo de Hb já implementada, aguardando dado de ingestão real
- `src/intensicare/services/domain_profilaxia.py:58,82,84` — critérios de checklist `tev-imc`, `hg-meta`, `hg-monitor` (booleanos de protocolo-seguido, não valores medidos)
- `docs/adr/0023-estabilidade-scoring-model.md` — precedente de ADR para gap consciente e documentado (ausência de ML), modelo seguido por esta ADR
- `docs/adr/ADR-0031-mvp-pathway-sepsis.md` — declaração das trilhas de MVP, referida na contagem "9 vs 12 vs 27 vs 7" citada por `DIM_E_INNOVATION.md:90-96`
