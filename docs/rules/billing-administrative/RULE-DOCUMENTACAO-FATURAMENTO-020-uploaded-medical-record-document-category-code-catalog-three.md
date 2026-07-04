# RULE-DOCUMENTACAO-FATURAMENTO-020 — Uploaded medical-record/document category code catalog — three divergent hand-maintained copies (54-code runtime map vs 34-value vs 33-value TS union types)

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
Fixed code->label dictionary classifying uploaded medical-record attachments (fiscal notes, TISS/SADT insurance guides, prescriptions, exam results, authorization guides, homecare evolution notes by discipline, etc.).


This runtime label dictionary (categoriaArquivo.ts, `as Record<Models.Arquivo.Categoria, string>`) is a 54-code superset of two separate, independently hand-maintained TypeScript union types that constrain which categoria values can actually be assigned/selected at compile time: Models.Arquivo.Categoria (34 values; types Arquivo.Upload/Download/Filter.categoria) and Models.Leito.CategoriaArquivo (33 values; types Leito.Upload.categoria), and the three have drifted out of sync with each other.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| categoriaCode | string |  | 54 codes with runtime labels (categoriaArquivo.ts) |
| categoria (Arquivo.Upload/Download/Filter) | string enum |  | 34 of those 54 codes (Arquivo.Categoria) |
| categoria (Leito.Upload) | string enum |  | 33 of those 54 codes (Leito.CategoriaArquivo, additionally missing 'EI') |

## Outputs
| Name | Type | Unit |
|---|---|---|
| label | string |  |
| categoria (typed) | string enum |  |

## Logic
```text
# --- (A) PRIMARY / most complete: runtime label dictionary (src/utils/categoriaArquivo.ts:1-54), 54 codes ---
categoriaArquivo: Record<Models.Arquivo.Categoria, string> = {
  nao_informado->"Não informado", ID->"Nota Fiscal", AT->"Atendimento", RG->"Documento Identidade",
  CC->"Carteira do Convênio", PE->"Pedido de Exame", GT->"Guia TISS/ SADT", DC->"Documentos Pessoais",
  AS->"Documentos Assitencias", GC->"Guias", EC->"Exames Eletrocardiograma (ECG)",
  RM->"Exame Ressonancia Magnética", CT->"Contrato ", GS->"Guia de Solicitação de Internação Externa",
  GI->"Guia de Internação Interna", EE->"Evolução externa", EI->"Evolução interna",
  EP->"Prescrição Externa", FR->"Formulario de Remoção", TG->"Ticket Gasometria",
  RT->"Requisição de Transfusão", TC->"Consentimento", PX->"Prontuário externo",
  RE->"Resultado de Exames/ Procedimentos", PM->"Parecer Médico", PU->"Prescrição Emergência",
  IM->"Invólucros", LI->"Laudo Imagem", RH->"Requisição de Hemodiálise", LL->"Laudo Laboratorial",
  AI->"Guia Autorização Internação", AP->"Guia Autorização de Prorrogação",
  AR->"Guia Autorização de Procedimento", AM->"Guia Autorização Mat/Med/Dieta/OPME",
  DO->"Declaração de Óbito", EX->"Exame externo", FG->"Folha de Gastos de Cirurgia",
  EHCMED->"Evolução HC de Médico", EHCTEC->"Evolução HC de Técnico de Enfermagem",
  EHCENF->"Evolução HC de Enfermagem", EHCFIS->"Evolução HC de Fisioterapeuta",
  EHCTER->"Evolução HC de Terapeuta", EHCMUS->"Evolução HC de Musicoterapeuta",
  EHCNUT->"Evolução HC de Nutricionista", EHCPSI->"Evolução HC de Psicólogo",
  EHCFON->"Evolução HC de Fonoaudiólogo", EHCFCT->"Evolução HC de Farmacêutico",
  EHCINT->"Evolução HC de Intercorrência", PRHC->"Prescrição Vida Conecta",
  BHHC->"Balanço Hídrico Vida Conecta",
}   // 54 keys total; TS "as" type-assertion suppresses excess-property checking against the 34-value type below

# --- (B) src/@types/models/Arquivo.d.ts:26-60 — Models.Arquivo.Categoria, 34 values (used by Arquivo.Upload/Download/Filter.categoria) ---
type Arquivo.Categoria =
  nao_informado | AT | ID | RG | CC | PE | GT | DC | AS | GC | EC | RM | CT | GS | GI |
  EE | EI | EP | FR | TG | RT | TC | PX | RE | PM | PU | IM | LI | RH | LL | AI | AP | AR | AM

# --- (C) src/@types/models/Leito.d.ts:17-50 — Models.Leito.CategoriaArquivo, 33 values (used by Leito.Upload.categoria) ---
type Leito.CategoriaArquivo =
  nao_informado | AT | ID | RG | CC | PE | GT | DC | AS | GC | EC | RM | CT | GS | GI |
  EE | /* EI missing here */ EP | FR | TG | RT | TC | PX | RE | PM | PU | IM | LI | RH | LL | AI | AP | AR | AM
```

## Edge cases (as implemented)
Verbatim typos preserved: "Documentos Assitencias" (should be Assistenciais), "Contrato " (trailing space). "EHC*" codes are homecare (HC / "Vida Conecta") evolution notes per discipline; PRHC/BHHC are Vida Conecta prescription / fluid balance. "nao_informado" is the explicit not-informed default. No runtime validator exists for the Arquivo.Categoria/Leito.CategoriaArquivo types (compiler-enforced only). If Leito.Upload uses CategoriaArquivo, uploading category "EI" (Evolução interna) against a Leito.Upload payload is a type error even though the same code is valid for Arquivo.Upload and has a runtime label.

## Divergence
Three independently hand-maintained catalogs of the same "document category" concept disagree in scope: (1) categoriaArquivo.ts (runtime label dictionary, rendered wherever a category needs a human-readable label) defines 54 codes; (2) Models.Arquivo.Categoria (Arquivo.d.ts, compile-time union type constraining Arquivo.Upload/Download/Filter.categoria) recognizes only 34 of those 54 — DO, EX, FG, all 11 EHC* homecare-evolution codes, PRHC and BHHC have runtime labels but are NOT valid Arquivo.Categoria values, so assigning them to an Arquivo.Upload/Filter.categoria field is a TypeScript type error even though the shared label map can render them (this gap was not flagged by Phase 1 and was found by reconciling categoriaArquivo.ts against Arquivo.d.ts directly); (3) Models.Leito.CategoriaArquivo (Leito.d.ts, constraining Leito.Upload.categoria) recognizes only 33 of the 34 Arquivo.Categoria values, additionally omitting "EI" (Evolução interna) — so uploading category="EI" via Leito.Upload is a type error even though the same code is valid for Arquivo.Upload and has a runtime label (this narrower divergence was already flagged by Phase 1 as RULE-arquivo-FE-07-002).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/categoriaArquivo.ts | 1-54 | f9656be2 | primary |
| trilhas-frontend | src/@types/models/Arquivo.d.ts | 26-60 | f9656be2 | duplicate |
| trilhas-frontend | src/@types/models/Leito.d.ts | 17-50 | f9656be2 | duplicate |
- Merged from: RULE-arquivo-FE-02-001, RULE-arquivo-FE-07-001, RULE-arquivo-FE-07-002
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-012, RULE-DOCUMENTACAO-FATURAMENTO-013

## Notes
DO = Declaração de Óbito (death certificate). OPME = orthotics/prosthetics/special materials. Distinguishes internal vs external (interna/externa) documents. Also used to type Arquivo.Filter (categoria/data_arquivo_inicio/data_arquivo_fim search filters). The 54-vs-34-vs-33 triple divergence is a maintenance/consistency risk to flag for the rebuild: a single source-of-truth enum (ideally generated, not hand-copied three times) is recommended.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
