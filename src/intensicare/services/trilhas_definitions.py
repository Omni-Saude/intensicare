"""Care Pathway seed definitions and catalog functions.

Extracted from domain_trilhas_engine.py as part of F-CODE-013 component refactoring.

Contains:
- PATHWAY_SEEDS: seed pathway definitions with states and criteria
- _PATHWAY_BY_ID, _PATHWAY_BY_SLUG: convenience lookups
- get_pathway_catalog: return pathway catalog
- get_pathway_by_id: get single pathway by ID
"""

from __future__ import annotations

from typing import Any

# ============================================================================
# Seed pathway definitions
# ============================================================================

PATHWAY_SEEDS: list[dict[str, Any]] = [
    # ── Pathway 1: Ventilação Mecânica ──
    {
        "id": 1,
        "name": "Ventilação Mecânica",
        "description": (
            "Acompanhamento de pacientes em ventilação mecânica invasiva. "
            "Monitora parâmetros ventilatórios, oxigenação e mecânica pulmonar "
            "para otimização e preparo para desmame."
        ),
        "slug": "ventilacao",
        "active": True,
        "states": [
            {
                "id": "initial",
                "name": "Avaliação Inicial",
                "order": 0,
                "description": "Paciente recém-inscrito no pathway de ventilação mecânica. Aguardando avaliação dos parâmetros ventilatórios iniciais.",
                "is_terminal": False,
            },
            {
                "id": "otimizacao",
                "name": "Otimização de Parâmetros",
                "order": 1,
                "description": "Ajuste fino dos parâmetros do ventilador: PEEP ideal, driving pressure ≤15 cmH₂O, volume corrente protetor (6-8 mL/kg PBW).",
                "is_terminal": False,
            },
            {
                "id": "estabilizacao",
                "name": "Estabilização",
                "order": 2,
                "description": "Parâmetros ventilatórios estáveis. Paciente mantém oxigenação adequada com FiO₂ em redução e mecânica pulmonar dentro de metas protetoras.",
                "is_terminal": False,
            },
            {
                "id": "desmame",
                "name": "Preparo para Desmame",
                "order": 3,
                "description": "Paciente com critérios para iniciar desmame ventilatório. Avaliação diária de prontidão para teste de respiração espontânea (TRE).",
                "is_terminal": False,
            },
            {
                "id": "alta",
                "name": "Alta do Pathway",
                "order": 4,
                "description": "Paciente extubado com sucesso ou em ventilação não invasiva estável. Encerramento do acompanhamento intensivo de ventilação mecânica.",
                "is_terminal": True,
            },
        ],
        "criteria": [
            {
                "id": "crit-vent-pf",
                "name": "Relação PaO₂/FiO₂",
                "category": "oxigenacao",
                "description": "Relação entre pressão parcial de oxigênio arterial e fração inspirada de oxigênio. Indicador de oxigenação pulmonar.",
                "unit": "mmHg",
                "normal_range": "> 300",
                "alert_threshold": "< 200",
            },
            {
                "id": "crit-vent-peep",
                "name": "PEEP",
                "category": "parametros",
                "description": "Pressão expiratória final positiva. Deve ser titulada para manter recrutamento alveolar sem causar hiperdistensão.",
                "unit": "cmH₂O",
                "normal_range": "5 - 10",
                "alert_threshold": "> 15",
            },
            {
                "id": "crit-vent-vc",
                "name": "Volume Corrente (PBW)",
                "category": "parametros",
                "description": "Volume corrente ajustado ao peso predito (PBW). Meta de ventilação protetora: 6-8 mL/kg PBW.",
                "unit": "mL/kg",
                "normal_range": "6 - 8",
                "alert_threshold": "> 10",
            },
            {
                "id": "crit-vent-plat",
                "name": "Pressão de Platô",
                "category": "parametros",
                "description": "Pressão de platô medida em pausa inspiratória. Deve ser mantida ≤30 cmH₂O para prevenir barotrauma.",
                "unit": "cmH₂O",
                "normal_range": "< 30",
                "alert_threshold": "> 35",
            },
            {
                "id": "crit-vent-drive",
                "name": "Driving Pressure",
                "category": "parametros",
                "description": "Diferença entre pressão de platô e PEEP (ΔP = Pplat - PEEP). Alvo protetor ≤15 cmH₂O.",
                "unit": "cmH₂O",
                "normal_range": "< 15",
                "alert_threshold": "> 20",
            },
        ],
    },
    # ── Pathway 2: Sepse ──
    {
        "id": 2,
        "name": "Sepse",
        "description": (
            "Acompanhamento de pacientes com sepse ou choque séptico conforme "
            "diretrizes SSC-2021. Inclui triagem (qSOFA), confirmação diagnóstica "
            "(lactato, PCT), bundle de 1ª hora e monitorização de resposta."
        ),
        "slug": "sepse",
        "active": True,
        "states": [
            {
                "id": "initial",
                "name": "Triagem Inicial",
                "order": 0,
                "description": "Paciente com suspeita de infecção e alteração de sinais clínicos. Aguardando confirmação com qSOFA e coleta de exames.",
                "is_terminal": False,
            },
            {
                "id": "confirmacao",
                "name": "Confirmação Diagnóstica",
                "order": 1,
                "description": "Sepse confirmada: qSOFA ≥2 + lactato elevado. Coleta de culturas e início da antibioticoterapia empírica em até 1 hora.",
                "is_terminal": False,
            },
            {
                "id": "tratamento",
                "name": "Tratamento Ativo",
                "order": 2,
                "description": "Bundle de 1ª hora em andamento: antibiótico administrado, ressuscitação volêmica iniciada, reavaliação hemodinâmica em curso.",
                "is_terminal": False,
            },
            {
                "id": "estabilizacao",
                "name": "Estabilização Clínica",
                "order": 3,
                "description": "Paciente hemodinamicamente estável, lactato em clearance, culturas em andamento. Reavaliação diária do esquema antimicrobiano.",
                "is_terminal": False,
            },
            {
                "id": "alta",
                "name": "Resolução",
                "order": 4,
                "description": "Resolução da sepse: lactato normalizado, PAM estável, descalonamento antimicrobiano concluído. Encerramento do pathway sepse.",
                "is_terminal": True,
            },
        ],
        "criteria": [
            {
                "id": "crit-sep-qsofa",
                "name": "qSOFA ≥ 2",
                "category": "triagem",
                "description": "Quick SOFA: FR ≥22 irpm, PAS ≤100 mmHg, Glasgow <15. ≥2 pontos configura disfunção orgânica suspeita de sepse.",
                "unit": "pontos",
                "normal_range": "0 - 1",
                "alert_threshold": "≥ 2",
            },
            {
                "id": "crit-sep-lactato",
                "name": "Lactato Sérico",
                "category": "laboratorial",
                "description": "Marcador de hipoperfusão tecidual. Níveis elevados indicam metabolismo anaeróbico e maior gravidade.",
                "unit": "mmol/L",
                "normal_range": "< 2.0",
                "alert_threshold": "> 4.0",
            },
            {
                "id": "crit-sep-pct",
                "name": "Procalcitonina (PCT)",
                "category": "laboratorial",
                "description": "Biomarcador de infecção bacteriana. Útil para guiar antibioticoterapia e descalonamento.",
                "unit": "ng/mL",
                "normal_range": "< 0.5",
                "alert_threshold": "> 2.0",
            },
            {
                "id": "crit-sep-pam",
                "name": "PAM ≥ 65 mmHg",
                "category": "hemodinamica",
                "description": "Pressão arterial média alvo durante a ressuscitação inicial da sepse (SSC-2021).",
                "unit": "mmHg",
                "normal_range": "≥ 65",
                "alert_threshold": "< 65",
            },
            {
                "id": "crit-sep-culturas",
                "name": "Culturas Coletadas",
                "category": "microbiologia",
                "description": "Coleta de 2 pares de hemoculturas e culturas de sítios relevantes antes do início do antibiótico.",
                "unit": "-",
                "normal_range": "coletadas",
                "alert_threshold": "pendentes",
            },
            {
                "id": "crit-sep-atb",
                "name": "Antibiótico em 1h",
                "category": "bundle",
                "description": "Administração de antibioticoterapia empírica de amplo espectro em até 1 hora do diagnóstico de sepse.",
                "unit": "-",
                "normal_range": "administrado",
                "alert_threshold": "não administrado",
            },
            {
                "id": "crit-sep-fluid",
                "name": "Ressuscitação Volêmica",
                "category": "bundle",
                "description": "Cristaloide 30 mL/kg nas primeiras 3 horas para pacientes com hipoperfusão ou lactato ≥4 mmol/L.",
                "unit": "mL/kg",
                "normal_range": "≥ 30",
                "alert_threshold": "< 20",
            },
        ],
    },
    # ── Pathway 3: Desmame ──
    {
        "id": 3,
        "name": "Desmame",
        "description": (
            "Protocolo de desmame ventilatório baseado em evidências. Avaliação "
            "sistemática de prontidão, teste de respiração espontânea (TRE), "
            "extubação e monitorização pós-extubação."
        ),
        "slug": "desmame",
        "active": True,
        "states": [
            {
                "id": "initial",
                "name": "Avaliação de Prontidão",
                "order": 0,
                "description": "Avaliação diária dos critérios de prontidão para desmame: causa da insuficiência respiratória resolvida, estabilidade hemodinâmica, drive respiratório adequado.",
                "is_terminal": False,
            },
            {
                "id": "tps",
                "name": "Teste de Respiração Espontânea",
                "order": 1,
                "description": "Realização do TRE (tubo T, PSV 5-7 cmH₂O, ou CPAP). Paciente mantém ventilação espontânea por 30-120 minutos sem sinais de falência.",
                "is_terminal": False,
            },
            {
                "id": "extubacao",
                "name": "Pós-Extubação",
                "order": 2,
                "description": "Paciente extubado. Monitorização de sinais de desconforto respiratório, gasometria de controle e necessidade de suporte não invasivo.",
                "is_terminal": False,
            },
            {
                "id": "alta",
                "name": "Desmame Completo",
                "order": 3,
                "description": "Paciente em ar ambiente ou oxigenoterapia de baixo fluxo por >48h após extubação. Encerramento do pathway de desmame.",
                "is_terminal": True,
            },
        ],
        "criteria": [
            {
                "id": "crit-des-frvt",
                "name": "FR/Vt (RSBI)",
                "category": "mecanica",
                "description": "Índice de respiração rápida e superficial (Rapid Shallow Breathing Index). FR / Vt (L). Prediz sucesso do desmame.",
                "unit": "ciclos/min/L",
                "normal_range": "< 105",
                "alert_threshold": "> 105",
            },
            {
                "id": "crit-des-nif",
                "name": "NIF (Pressão Inspiratória Máxima)",
                "category": "mecanica",
                "description": "Negative Inspiratory Force. Mede a força muscular inspiratória. Valores mais negativos indicam melhor força.",
                "unit": "cmH₂O",
                "normal_range": "< -25",
                "alert_threshold": "> -20",
            },
            {
                "id": "crit-des-glasgow",
                "name": "Escala de Glasgow",
                "category": "neurologico",
                "description": "Nível de consciência adequado para proteção de via aérea e cooperação com o desmame.",
                "unit": "-",
                "normal_range": "≥ 11",
                "alert_threshold": "< 9",
            },
            {
                "id": "crit-des-tosse",
                "name": "Tosse Eficaz",
                "category": "clinico",
                "description": "Capacidade de tossir e mobilizar secreções. Essencial para manutenção da via aérea pérvia pós-extubação.",
                "unit": "-",
                "normal_range": "presente",
                "alert_threshold": "ausente",
            },
            {
                "id": "crit-des-secrecao",
                "name": "Controle de Secreção",
                "category": "clinico",
                "description": "Quantidade e qualidade das secreções traqueais. Secreção excessiva ou purulenta contraindica extubação eletiva.",
                "unit": "-",
                "normal_range": "adequado",
                "alert_threshold": "excessivo",
            },
            {
                "id": "crit-des-gasometria",
                "name": "Gasometria Pós-EXT",
                "category": "gasometria",
                "description": "Gasometria arterial após extubação para confirmar manutenção de trocas gasosas adequadas sem suporte ventilatório invasivo.",
                "unit": "-",
                "normal_range": "estável",
                "alert_threshold": "alterada",
            },
        ],
    },
    # ── Pathway 4: Nutrição Enteral ──
    {
        "id": 4,
        "name": "Nutrição Enteral",
        "description": (
            "Acompanhamento da terapia nutricional enteral (TNE) em pacientes "
            "críticos. Triagem nutricional, progressão da dieta até meta calórico-proteica, "
            "monitorização de tolerância e transição para via oral."
        ),
        "slug": "nutricao",
        "active": True,
        "states": [
            {
                "id": "initial",
                "name": "Avaliação Nutricional",
                "order": 0,
                "description": "Triagem nutricional (NRS-2002) e avaliação inicial. Definição de meta calórico-proteica individualizada.",
                "is_terminal": False,
            },
            {
                "id": "progressao",
                "name": "Progressão da Dieta",
                "order": 1,
                "description": "Aumento gradual do volume e concentração da dieta enteral conforme tolerância gastrointestinal. Monitorização de resíduo gástrico.",
                "is_terminal": False,
            },
            {
                "id": "meta",
                "name": "Meta Nutricional",
                "order": 2,
                "description": "Aporte calórico ≥80% da meta e proteico ≥1.2 g/kg/dia. Paciente tolerando dieta sem intercorrências significativas.",
                "is_terminal": False,
            },
            {
                "id": "alta",
                "name": "Via Oral Plena",
                "order": 3,
                "description": "Transição completa para dieta por via oral. Paciente com ingestão oral adequada (>75% das necessidades). Encerramento do pathway de nutrição enteral.",
                "is_terminal": True,
            },
        ],
        "criteria": [
            {
                "id": "crit-nut-triagem",
                "name": "Triagem NRS-2002",
                "category": "triagem",
                "description": "Nutritional Risk Screening 2002. Identifica pacientes com risco nutricional que se beneficiam de TNE precoce.",
                "unit": "pontos",
                "normal_range": "< 3",
                "alert_threshold": "≥ 5",
            },
            {
                "id": "crit-nut-calorias",
                "name": "Aporte Calórico",
                "category": "nutricional",
                "description": "Percentual da meta calórica diária atingida via nutrição enteral. Alvo: atingir ≥80% da meta em até 72h de TNE.",
                "unit": "% meta/dia",
                "normal_range": "≥ 80%",
                "alert_threshold": "< 60%",
            },
            {
                "id": "crit-nut-proteinas",
                "name": "Aporte Proteico",
                "category": "nutricional",
                "description": "Oferta proteica diária ajustada ao peso. Meta mínima: 1.2 g/kg/dia, podendo chegar a 2.0 g/kg/dia em situações de catabolismo acentuado.",
                "unit": "g/kg/dia",
                "normal_range": "≥ 1.2",
                "alert_threshold": "< 0.8",
            },
            {
                "id": "crit-nut-residuo",
                "name": "Resíduo Gástrico",
                "category": "tolerancia",
                "description": "Volume de resíduo gástrico medido a cada 4-6h. Indicador de intolerância à dieta enteral e risco de broncoaspiração.",
                "unit": "mL",
                "normal_range": "< 200",
                "alert_threshold": "> 500",
            },
            {
                "id": "crit-nut-albumina",
                "name": "Albumina Sérica",
                "category": "laboratorial",
                "description": "Marcador do estado nutricional e resposta inflamatória. Hipoalbuminemia associa-se a piores desfechos em UTI.",
                "unit": "g/dL",
                "normal_range": "≥ 3.0",
                "alert_threshold": "< 2.5",
            },
            {
                "id": "crit-nut-diarreia",
                "name": "Diarreia",
                "category": "tolerancia",
                "description": "Frequência de episódios diarreicos. Pode indicar intolerância à fórmula, infecção ou necessidade de ajuste na velocidade de infusão.",
                "unit": "episódios/dia",
                "normal_range": "0",
                "alert_threshold": "> 3",
            },
        ],
    },
]

# Convenience lookup — built lazily for module-load performance
_PATHWAY_BY_ID: dict[int, dict[str, Any]] = {}
_PATHWAY_BY_SLUG: dict[str, dict[str, Any]] = {}


def _ensure_lookups() -> None:
    """Build convenience lookup dicts if not already populated."""
    if not _PATHWAY_BY_ID:
        for p in PATHWAY_SEEDS:
            _PATHWAY_BY_ID[p["id"]] = p
            _PATHWAY_BY_SLUG[p["slug"]] = p


# ============================================================================
# Catalog functions
# ============================================================================


def get_pathway_catalog(active_only: bool = True) -> list[dict[str, Any]]:
    """Return the pathway catalog (seed data for now).

    Rule 1: Only active pathways are returned when active_only=True.

    Args:
        active_only: If True, return only active pathways.

    Returns:
        List of pathway dicts with states and criteria.
    """
    catalog: list[dict[str, Any]] = []
    for p in PATHWAY_SEEDS:
        if active_only and not p.get("active", True):
            continue
        # Return a shallow copy so callers don't mutate seeds
        catalog.append({
            "id": p["id"],
            "name": p["name"],
            "description": p["description"],
            "slug": p["slug"],
            "active": p["active"],
            "states": [dict(s) for s in p["states"]],
            "criteria": [dict(c) for c in p["criteria"]],
        })
    return catalog


def get_pathway_by_id(pathway_id: int) -> dict[str, Any] | None:
    """Get a single pathway with its criteria.

    Args:
        pathway_id: Numeric pathway ID.

    Returns:
        Pathway dict with states and criteria, or None if not found.
    """
    _ensure_lookups()
    p = _PATHWAY_BY_ID.get(pathway_id)
    if p is None:
        return None
    return {
        "id": p["id"],
        "name": p["name"],
        "description": p["description"],
        "slug": p["slug"],
        "active": p["active"],
        "states": [dict(s) for s in p["states"]],
        "criteria": [dict(c) for c in p["criteria"]],
    }
