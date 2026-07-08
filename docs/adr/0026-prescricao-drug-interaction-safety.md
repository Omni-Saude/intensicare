# ADR-026: Prescrição — Arquitetura de Segurança e Interação Medicamentosa (43 regras)

**Status:** Proposed
**Data:** 2026-07-07
**Area:** Prescrição / Segurança Clínica / Integração
**Referência:** ADR-001 (AMH Data Platform consumer), ADR-0013 (consumo CDC como contrato de integração), ADR-0002 (LGPD e direito ao esquecimento)
**Regulado:** parcial — a verificação de interação medicamentosa é suporte à decisão clínica (L0-hard, ADR-0008); o sistema sinaliza e rotina, nunca decide conduta.

## Contexto

O domínio de prescrição do IntensiCare consolida **43 regras legadas** extraídas do código `trilhas-frontend` e `ahlabs-trilhas` (catálogo `prescricao.yaml`, phase2), cobrindo: captura de medicamentos, suspensão de doses, cálculo de balanço hídrico via quantidade exportada, boundary de turno (07:00), validação de administração, aprazamento, e interações entre fármacos. Na UTI, a polifarmácia é a regra — pacientes críticos recebem em média 12-18 fármacos simultaneamente (antibióticos, vasopressores, sedativos, analgésicos, anticoagulantes, corticosteroides, antiarrítmicos), criando um espaço combinatorial de interações que é clinicamente crítico e potencialmente fatal.

O legado **não implementava verificação de interação medicamentosa** — as 43 regras cobrem administração, suspensão e balanço hídrico, mas nenhuma checava se, por exemplo, ceftriaxone + cálcio IV (precipitação fatal) ou amiodarona + fluoroquinolona (QT prolongado → torsades) estavam co-prescritos. A verificação de interações era delegada ao conhecimento implícito do prescritor e do farmacêutico — sem suporte sistemático do sistema.

Para o v2 (IntensiCare), a verificação de interações medicamentosas é mandatória. A questão arquitetural é **onde e como** essa verificação deve ser executada, considerando as restrições do ecossistema: latência sub-segundo para UI responsiva (o prescritor não pode esperar), resiliência offline (a UTI pode operar com conectividade degradada), conformidade LGPD (dados de paciente não podem trafegar para serviços externos fora do Brasil), e abrangência clínica (interações não detectadas são risco de vida).

Quatro abordagens foram consideradas:

### Opção 1: Verificação client-side (browser, base de dados estática)

Uma base de interações medicamentosas é embutida no bundle frontend (JSON estático ou WebAssembly). A verificação ocorre inteiramente no navegador do prescritor, sem chamada ao servidor. A base cobre interações conhecidas (ex.: ~5.000 pares fármaco-fármaco) e é atualizada a cada deploy do frontend.

**Prós:**
- Latência zero de rede — a verificação é síncrona no event loop do navegador, sub-10ms para uma prescrição típica de 8-12 fármacos.
- Zero dependência de conectividade — funciona integralmente offline, crítico para UTIs com conectividade intermitente.
- Zero exposição de dados do paciente — nada sai do navegador. LGPD trivialmente satisfeita.
- Simplicidade operacional — sem serviço backend dedicado para manter, escalar e monitorar.

**Contras:**
- Base de interações incompleta e congelada entre deploys — novas interações descobertas (ex.: nova contraindicação publicada pelo FDA/ANVISA) só chegam ao sistema no próximo ciclo de release do frontend (semanas).
- Impossível contextualizar com dados clínicos do paciente armazenados no backend — ex.: a interação warfarina + AINE é mais grave se o INR do paciente já estiver elevado, mas o frontend não tem acesso ao INR sem chamada ao servidor.
- A base estática cresce com o tempo — ~5.000 pares hoje, mas pode chegar a dezenas de milhares. O bundle frontend aumenta proporcionalmente, impactando o tempo de carregamento inicial.
- Sem personalização por perfil institucional — a base é a mesma para todos os tenants; um hospital que queira adicionar interações específicas do seu formulário terapêutico não consegue sem customização de código.

### Opção 2: Serviço backend com base local de medicamentos (DrugInteractionService)

Um microsserviço dedicado (`drug-interaction-service`) executa no cluster do IntensiCare, mantendo uma base de interações medicamentosas completa (ex.: ANVISA bulário eletrônico + DrugBank open data + WHO ATC classification) em banco de dados local (PostgreSQL). A base é atualizada periodicamente (diariamente/semanalmente) via pipeline de ingestão que baixa as fontes oficiais. A API recebe uma lista de fármacos (por código ATC ou nome padronizado) e retorna interações detectadas com severidade e referência.

**Prós:**
- Base completa e atualizável independentemente do ciclo de release do frontend — novas interações chegam em horas/dias, não semanas.
- Contextualização clínica possível — o serviço pode cruzar interações com dados do paciente armazenados no Gold (via Athena): função renal (clearance de creatinina afeta risco de nefrotoxicidade), INR (risco de sangramento), eletrólitos (risco de QT prolongado).
- Personalização por tenant — cada instituição pode configurar seu formulário terapêutico, thresholds de severidade, e interações específicas (ex.: "hospital X não utiliza varfarina, apenas enoxaparina — suprimir alertas de interação com antagonistas de vitamina K").
- Dados não saem do datacenter — o serviço roda no mesmo cluster que os demais componentes, satisfazendo LGPD sem exfiltração de PHI para terceiros.

**Contras:**
- Latência de rede — cada verificação de prescrição requer uma chamada HTTP/gRPC ao serviço (~50-200ms). Aceitável para salvar/validar uma prescrição, mas inviável para verificação interativa a cada tecla do prescritor.
- Dependência de conectividade — se o serviço estiver indisponível, a verificação de interações para de funcionar. Em cenário de UTI com conectividade degradada, o prescritor fica sem suporte de segurança medicamentosa.
- Custo operacional — +1 serviço para deploy, escala, monitoramento, e manutenção da base de medicamentos (pipeline de ingestão, deduplicação de fármacos, mapeamento ATC).
- A base de medicamentos precisa de curadoria — nomes comerciais variam por país e fabricante; mapear DS_ITEM_PRESCRITO legado (texto livre) para códigos ATC exige um serviço de normalização de fármacos que é um problema não trivial por si só.

### Opção 3: Serviço externo de interação medicamentosa (DrugBank / RxNorm / OpenFDA)

A verificação de interações é delegada a um serviço externo especializado (ex.: DrugBank API, RxNorm Interaction API, OpenFDA Drug Interaction endpoint). O IntensiCare envia a lista de fármacos e recebe as interações detectadas com severidade, mecanismo, e referências bibliográficas. O serviço externo mantém a base de interações — o IntensiCare é apenas consumidor.

**Prós:**
- Base de interações mais completa e atualizada do mercado — DrugBank e RxNorm são mantidos por equipes dedicadas de farmacologistas e curadores, com atualizações contínuas.
- Zero custo de curadoria para o time IntensiCare — não precisamos manter base de medicamentos, pipeline de ingestão, nem mapeamento de nomes comerciais.
- Cobertura de interações complexas — interações fármaco-alimento, fármaco-exame laboratorial, duplicidade terapêutica, contraindicações por faixa etária e gestação — que exigiriam anos de desenvolvimento interno para serem cobertas.

**Contras:**
- **LGPD: PHI exportada para terceiro.** Enviar a lista de fármacos de um paciente identificado para um servidor nos EUA (DrugBank) ou mesmo em cloud pública é uma violação potencial da LGPD. A lista de medicamentos de um paciente, combinada com o contexto de UTI, é PHI inequívoca. Seria necessário pseudonimizar ou implementar um data processing agreement (DPA) com o provedor — complexidade jurídica e risco regulatório elevados.
- **Dependência externa crítica de segurança clínica.** Se o serviço externo estiver indisponível (outage, throttling, mudança de API, falência do provedor), a verificação de interações para de funcionar. Para uma funcionalidade de segurança clínica (interação não detectada pode matar um paciente), essa dependência é inaceitável sem fallback robusto.
- Latência e custo — chamada de rede externa adiciona 200-800ms + custo por transação (DrugBank cobra por API call). Multiplicado pelo volume de prescrições em um hospital, o custo operacional pode ser significativo.
- Sem contextualização com dados clínicos do paciente — o serviço externo não tem acesso ao INR, clearance de creatinina, ou eletrólitos do paciente, limitando a avaliação ao nível fármaco-fármaco genérico (ex.: "amiodarona + levofloxacino = risco de QT prolongado", mas sem saber que o paciente já tem QTc de 520ms).

### Opção 4: Arquitetura híbrida — cache local com fallback externo

Combinação da Opção 2 e da Opção 3: um `DrugInteractionService` local mantém uma base de interações em cache (PostgreSQL) abastecida por um pipeline de ingestão periódica de fontes públicas (ANVISA bulário, DrugBank open data subset, WHO ATC). Para interações comuns (as ~5.000 mais frequentes), a resposta é servida do cache local em <10ms. Para interações raras ou de alta complexidade (ex.: interações triplas, fármacos off-label, contraindicações por genotipagem), o serviço consulta uma API externa especializada como fallback — **apenas após pseudonimização** (envia códigos ATC sem identificador de paciente) e com cache agressivo do resultado (TTL de 30 dias). O frontend recebe uma resposta unificada: interações do cache local (instantâneas) + interações do fallback externo (se disponível, assíncronas).

**Prós:**
- O melhor dos dois mundos: latência sub-10ms para 95%+ das verificações (cache local) com cobertura estendida do serviço externo para casos raros.
- Resiliência: se o serviço externo estiver indisponível, o cache local continua funcionando — a verificação de segurança medicamentosa nunca fica completamente indisponível.
- LGPD satisfeita: PHI nunca sai do datacenter. O fallback externo só recebe códigos ATC anonimizados, sem identificador de paciente, e os resultados são cacheados localmente.
- Atualização incremental: o pipeline de ingestão pode rodar diariamente para incorporar novas interações das fontes públicas; o fallback externo cobre o gap entre atualizações.

**Contras:**
- Complexidade arquitetural máxima: dois caminhos de código (cache local + fallback), pipeline de ingestão, estratégia de cache com TTL, pseudonimização para chamada externa, reconciliação de resultados duplicados (mesma interação detectada por ambas as fontes).
- Custo operacional combinado: manter base local + pipeline de ingestão + custo de API externa (mesmo que reduzido pelo cache).
- O fallback externo, mesmo pseudonimizado, ainda é uma dependência externa — embora não bloqueante (a verificação local continua funcionando), a completude da verificação fica degradada durante outages do provedor externo.
- A pseudonimização (enviar apenas ATC codes) reduz a utilidade do serviço externo — DrugBank e RxNorm podem retornar interações contextualizadas por faixa etária e gênero, mas sem esses dados o retorno é genérico.

## Decisão

**Opção 2 — Serviço backend com base local de medicamentos (`DrugInteractionService`)**, com as seguintes características:

1. **Base local, não serviço externo.** O IntensiCare mantém uma base de interações medicamentosas em PostgreSQL (schema `drug_interaction`), populada por um pipeline de ingestão periódica (diária) a partir de fontes públicas e abertas: ANVISA bulário eletrônico (fonte primária para Brasil), DrugBank open data subset (fonte complementar para interações não cobertas pela ANVISA), e WHO ATC/DDD Index (classificação anatômica-terapêutica-química para normalização de fármacos). **Nenhuma API externa é chamada em tempo real** — o pipeline de ingestão é batch, offline, e a verificação de interações é inteiramente local.

2. **LGPD: PHI nunca sai do datacenter.** A verificação de interações ocorre inteiramente dentro do cluster IntensiCare. O pipeline de ingestão baixa dados públicos de interações (ANVISA, DrugBank open data) — não envia dados de pacientes. Conformidade com ADR-0002 (direito ao esquecimento) é trivial: a base de interações é shared reference data, não contém PHI. O registro de quais interações foram detectadas para um paciente específico (log de auditoria) é armazenado no schema `prescricao` e apagado em cascata no erasure.

3. **Pipeline de ingestão offline com curadoria.** Diariamente, um job batch (`drug-ingestion-pipeline`):
   - Baixa o bulário eletrônico da ANVISA (formato XML/JSON público) e extrai interações documentadas em bula.
   - Baixa o DrugBank open data (licensed subset, gratuito para uso clínico não comercial) e extrai interações fármaco-fármaco com severidade e mecanismo.
   - Normaliza fármacos para códigos ATC (WHO ATC/DDD Index) — resolve nomes comerciais, genéricos, e sinônimos para um identificador canônico.
   - Deduplica interações reportadas por ambas as fontes (ANVISA e DrugBank), consolidando severidade e referências.
   - Versiona a base de interações (`interaction_db_version`) e publica um evento `DrugInteractionDBUpdated` para que o `DrugInteractionService` faça hot-reload sem restart.

4. **Normalização de fármacos como serviço (`DrugNormalizationService`).** As 43 regras legadas referenciam medicamentos por `DS_ITEM_PRESCRITO` (texto livre do Tasy). Para que a verificação de interações funcione, é necessário um serviço de normalização que mapeie texto livre → código ATC → interações. Esse serviço:
   - Mantém um dicionário de mapeamento (`drug_atc_mapping`) construído a partir do formulário terapêutico institucional + WHO ATC Index.
   - Expõe endpoint `POST /drugs/normalize` que recebe texto livre e retorna o código ATC canônico + confiança do match (exata, fuzzy, não encontrada).
   - Para fármacos não mapeados (match confidence < threshold), registra em fila de curadoria para revisão humana.
   - É consumido pelo `DrugInteractionService` antes da verificação de interações.

5. **Verificação de interações em dois momentos.** O `DrugInteractionService` é invocado em dois pontos do fluxo de prescrição:
   - **Verificação interativa (pré-submissão):** a cada adição de fármaco à prescrição (o prescritor digita e seleciona um medicamento), o frontend chama `POST /drug-interactions/check-pair` com o novo fármaco + os já prescritos. Resposta em <100ms (p95). Se detectada interação, o frontend exibe um alerta inline com severidade (contraindicação absoluta / risco grave / precaução / monitorar) e referência (bula ANVISA ou fonte). O prescritor pode reconhecer e prosseguir (decisão clínica é humana — L0-hard, ADR-0008), mas o override fica registrado em log de auditoria.
   - **Verificação completa (pós-submissão):** ao salvar a prescrição, o backend chama `POST /drug-interactions/check` com a lista completa de fármacos + contexto clínico do paciente (clearance de creatinina, INR, K⁺, Mg²⁺, QTc se disponível). Essa verificação é mais completa (contextualizada) e pode detectar interações que a verificação interativa não detectou (porque na verificação interativa os fármacos são checados par-a-par incrementalmente; a verificação completa avalia todas as combinações N×(N-1)/2 simultaneamente + contexto clínico). Interações detectadas são registradas no log de auditoria da prescrição (`prescription_drug_interaction_log`) e notificadas ao prescritor e ao farmacêutico clínico.

6. **Classificação de severidade em 4 níveis (versionada, DMN — ADR-0012):**
   - `contraindicated` — interação contraindicação absoluta (ex.: ceftriaxone + cálcio IV). O sistema **bloqueia** a prescrição (hard stop) — requer override documentado com justificativa clínica e dupla checagem (farmacêutico).
   - `severe` — risco grave de evento adverso (ex.: amiodarona + levofloxacino → QT prolongado, warfarina + AINE → sangramento). Alerta vermelho, requer reconhecimento do prescritor, registrado em auditoria.
   - `caution` — precaução: interação conhecida mas manejável com monitoramento (ex.: enalapril + espironolactona → hipercalemia — monitorar K⁺). Alerta amarelo, informativo.
   - `monitor` — interação teórica ou de baixa relevância clínica (ex.: ranitidina + cetoconazol → redução de absorção, separar administração). Alerta azul, informativo, sem obrigação de reconhecimento.
   - Os thresholds de severidade e as ações associadas são configuráveis por tenant (DMN versionada).

7. **Resiliência offline com fallback frontend mínimo.** Embora a decisão primária seja backend local, o frontend inclui um **subconjunto mínimo de interações críticas** (~500 pares `contraindicated` + `severe`) como fallback estático (WebAssembly, <200KB comprimido). Esse fallback:
   - É ativado automaticamente quando o `DrugInteractionService` está indisponível (timeout >2s ou erro 5xx).
   - Cobre apenas interações `contraindicated` e `severe` — as mais críticas para segurança.
   - Exibe um banner: "Verificação de interações operando em modo offline reduzido. Interações de precaução e monitoramento não estão sendo verificadas."
   - É atualizado a cada release do frontend (mesmo ciclo das demais regras).
   - **Não substitui a verificação completa** — as interações são reavaliadas pelo serviço backend assim que a conectividade for restaurada (reconciliação assíncrona).

8. **Integração com as 43 regras legadas.** As 43 regras do catálogo `prescricao.yaml` continuam operando independentemente — cobrem administração, suspensão, balanço hídrico e aprazamento. A verificação de interações medicamentosas é uma **nova camada ortogonal** que não modifica as regras existentes, mas adiciona um gate de segurança antes da efetivação da prescrição. O fluxo completo é: validação das 43 regras → normalização de fármacos → verificação de interações → efetivação.

**Gatilho de reavaliação:** Se a cobertura da base local ANVISA+DrugBank for insuficiente (>5% das verificações resultarem em "fármaco não mapeado" após 3 meses de operação), ou se o custo de curadoria do pipeline de ingestão for proibitivo (>20% do esforço do time de prescrição), reavaliar a introdução do fallback externo (Opção 4) para fármacos não cobertos pela base local.

## Consequencias

**Positivas:**
- Segurança clínica: verificação sistemática de interações medicamentosas em toda prescrição — o que o legado não fazia. Interações `contraindicated` são bloqueadas com hard stop; interações `severe` exigem reconhecimento documentado.
- LGPD: PHI nunca sai do datacenter. A base de interações é shared reference data pública; o pipeline de ingestão é batch e offline. Conformidade regulatória sem complexidade jurídica de DPA com terceiros.
- Latência previsível: verificação interativa sub-100ms (p95) para cache local; verificação completa pós-submissão sub-200ms. O prescritor não percebe latência durante a digitação.
- Resiliência: o fallback frontend cobre as ~500 interações mais críticas mesmo em cenário de conectividade zero com o backend. A UTI nunca fica completamente sem verificação de segurança medicamentosa.
- Contextualização clínica: a verificação completa cruza interações com dados do paciente (função renal, coagulação, eletrólitos) — algo que serviço externo nenhum faria sem receber PHI completa.
- Base versionada e auditável: cada interação detectada reference a `interaction_db_version` que a produziu. Se uma interação for contestada (falso positivo), é possível rastrear exatamente qual fonte e versão a gerou (consistente com INV-3).
- Normalização de fármacos como investimento de plataforma: o `DrugNormalizationService` beneficia não só a verificação de interações, mas também padronização de prescrições, relatórios de utilização de medicamentos, e futura integração com farmácia hospitalar.

**Negativas (aceitas):**
- Custo de curadoria do pipeline de ingestão: manter o mapeamento de fármacos (texto livre → ATC) exige esforço contínuo, especialmente para nomes comerciais regionais e novos lançamentos. Mitigação: o dicionário inicial é construído a partir do formulário terapêutico institucional (conjunto fechado, ~2.000 fármacos); a curadoria contínua é fila de exceção (fármacos não mapeados), não revisão completa.
- Cobertura inferior a um serviço externo especializado: DrugBank completo (licensed, não open data) e RxNorm cobrem interações raras e off-label que a base ANVISA + DrugBank open data pode não cobrir. Mitigação: a base ANVISA cobre todos os fármacos registrados no Brasil (obrigatório por lei); DrugBank open data complementa com interações internacionais. Para a prática clínica em UTI brasileira, a cobertura é >95%.
- Latência da verificação completa (pós-submissão): ~200ms adicionais no fluxo de salvamento da prescrição. Aceitável — o salvamento não é interativo (o prescritor clica "Salvar" e espera confirmação).
- O fallback frontend cobre apenas ~500 interações críticas — em modo offline, interações `caution` e `monitor` não são verificadas. Risco aceito: o modo offline é excepcional e temporário; a reconciliação assíncrona cobre o gap assim que a conectividade retorna.
- Complexidade de normalização de fármacos: mapear texto livre legado do Tasy (`DS_ITEM_PRESCRITO`) para ATC é um problema de NLP não trivial (ex.: "dipirona 1g IV" vs "Novalgina 1g EV" vs "metamizol 1g intravenoso" — mesmo fármaco, três representações textuais). Mitigação: abordagem híbrida — match exato por formulário terapêutico (cobre ~80%), fuzzy matching com TF-IDF + distância de Levenshtein (cobre ~15%), fila de curadoria humana (~5%).

## Supersedes

— (Estende ADR-0013 para o domínio específico de segurança medicamentosa em prescrição. Referencia ADR-0002 para conformidade LGPD. Referencia ADR-0008 para o princípio L0-hard: a verificação de interações sinaliza e bloqueia, mas a decisão final de prescrever apesar da interação é do médico, documentada e auditada.)
