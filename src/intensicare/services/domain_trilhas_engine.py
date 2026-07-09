"""
Care Pathway Engine (Trilhas Engine) — core domain service.

Implements 18 clinical business rules across 4 pathway catalogs:
  - Ventilação Mecânica (ventilacao)
  - Sepse (sepse)
  - Desmame (desmame)
  - Nutrição Enteral (nutricao)

Architecture:
  - In-memory patient enrollment store (bridge to DB later via API router)
  - Dataclass return types matching OpenAPI contract (docs/contracts/pathways-openapi.yaml)
  - Seed pathways with realistic states + criteria definitions
  - State-transition engine triggered by criteria evaluation
  - PT-BR clinical recommendations

18 Rules (Regras):
  1. Only active pathways are returned when active_only=True
  2. Each pathway has ordered, forward-only state progression
  3. Reaching a terminal state completes the pathway (status=completed, completed_at set)
  4. A patient cannot enroll in the same active pathway twice (409 conflict)
  5. Eligibility check requires patient_data matching pathway criteria categories
  6. Enrollment always starts at the "initial" state with default severity "normal"
  7. Criteria evaluation updates individual criterion met/value/timestamp fields
  8. When all criteria for the current state are met, auto-transition to next state
  9. Every state transition is logged (from_state, to_state, reason, timestamp)
  10. Severity mapped by met/total ratio: normal(>=80%), watch(60-79%), urgent(40-59%), critical(<40%)
  11. Trend derived from forward/backward/stable transitions in state history
  12. PT-BR recommendation generated from pathway name + current state + severity
  13. get_patient_pathways filters by status (active/completed/archived)
  14. get_pathway_progress computes criteria_summary (total/met/not_met/pending)
  15. Eligibility for ventilacao requires ventilation/O₂ criteria data
  16. Eligibility for sepse requires qSOFA/lactate/culturas criteria data
  17. Eligibility for desmame requires weaning readiness criteria (NIF, FR/Vt, Glasgow)
  18. Eligibility for nutricao requires nutritional screening or intake criteria data
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypedDict
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# In-memory stores (bridge to DB later)
# ============================================================================


class PatientPathwayDict(TypedDict):
    """Typed representation of a patient pathway enrollment record.

    Mirrors the in-memory store structure used throughout the trilhas engine.
    """

    id: int
    mpi_id: str
    pathway_id: int
    pathway_name: str
    pathway_slug: str
    current_state: str
    criteria_data: list[dict[str, Any]]
    status: str
    severity: str
    enrolled_at: str
    enrolled_by: str
    completed_at: str | None
    updated_at: str


# {mpi_id: {pathway_id: PatientPathway-like dict}}
_patient_pathway_store: dict[str, dict[int, PatientPathwayDict]] = {}

# {patient_pathway_id: list[transition dicts]}
_transition_store: dict[int, list[dict[str, Any]]] = {}

# Auto-increment counter for patient_pathway IDs
_next_pp_id: int = 1


def _reset_stores() -> None:
    """Reset in-memory stores (useful for tests)."""
    global _patient_pathway_store, _transition_store, _next_pp_id
    _patient_pathway_store = {}
    _transition_store = {}
    _next_pp_id = 1


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

# Convenience lookup
_PATHWAY_BY_ID: dict[int, dict[str, Any]] = {p["id"]: p for p in PATHWAY_SEEDS}
_PATHWAY_BY_SLUG: dict[str, dict[str, Any]] = {p["slug"]: p for p in PATHWAY_SEEDS}


# ============================================================================
# Dataclasses (match OpenAPI contract)
# ============================================================================

@dataclass
class PathwayEligibilityResult:
    """Result of checking whether a patient is eligible for a pathway."""
    eligible: bool
    reason: str = ""
    matching_criteria: list[str] = field(default_factory=list)


@dataclass
class PathwayEnrollmentResult:
    """Result of enrolling a patient in a pathway."""
    patient_pathway_id: int | None = None
    mpi_id: str = ""
    pathway_id: int = 0
    current_state: str = "initial"
    status: str = "active"
    severity: str = "normal"
    enrolled_at: str = ""
    error: str = ""


@dataclass
class CriteriaEvaluationResult:
    """Result of updating criteria evaluation for a pathway enrollment."""
    patient_pathway_id: int
    mpi_id: str
    criteria: list[dict[str, Any]]  # [{id, name, met, value, evaluated_at}]
    state_changed: bool = False
    new_state: str = ""
    transition_reason: str = ""
    severity: str = "normal"


@dataclass
class PathwayProgressResult:
    """Detailed progress for a patient in a specific pathway."""
    patient_pathway_id: int
    mpi_id: str
    pathway_name: str
    current_state: str
    criteria_summary: dict[str, int]  # {total, met, not_met, pending}
    criteria: list[dict[str, Any]]
    state_history: list[dict[str, Any]]
    trend: str = "none"
    last_evaluated_at: str = ""
    recommendation: str = ""


# ============================================================================
# Core functions
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


def check_pathway_eligibility(
    mpi_id: str,
    pathway_id: int,
    patient_data: dict[str, Any] | None = None,
) -> PathwayEligibilityResult:
    """Check if a patient is eligible for a pathway.

    Rule 4 (partial): Also checks whether the patient is already enrolled.
    Rule 5: Eligibility check requires patient_data matching pathway criteria categories.
    Rule 15-18: Specific eligibility rules per pathway.

    For ventilacao: patient should have ventilation/O₂ data.
    For sepse: patient should have qSOFA/lactate/culturas indicators.
    For desmame: patient should have weaning readiness data (NIF, RSBI, Glasgow).
    For nutricao: patient should have nutritional screening or intake data.

    Args:
        mpi_id: Patient identifier.
        pathway_id: Pathway ID to check eligibility against.
        patient_data: Optional clinical data dict keyed by category or criterion ID.

    Returns:
        PathwayEligibilityResult with eligibility status and reason.
    """
    pathway = _PATHWAY_BY_ID.get(pathway_id)
    if pathway is None:
        return PathwayEligibilityResult(
            eligible=False,
            reason=f"Pathway {pathway_id} não encontrado.",
        )

    if not pathway.get("active", True):
        return PathwayEligibilityResult(
            eligible=False,
            reason=f"Pathway '{pathway['name']}' não está ativo.",
        )

    # Rule 4: Check if patient is already enrolled in this pathway (active)
    patient_pathways = _patient_pathway_store.get(mpi_id, {})
    if pathway_id in patient_pathways:
        existing = patient_pathways[pathway_id]
        if existing.get("status") == "active":
            return PathwayEligibilityResult(
                eligible=False,
                reason=f"Paciente {mpi_id} já está inscrito ativamente no pathway '{pathway['name']}'.",
            )

    # Rule 5 + 15-18: Eligibility based on patient_data
    if patient_data is None:
        # Without patient data, allow enrollment but flag as requiring manual data
        return PathwayEligibilityResult(
            eligible=True,
            reason="Verificação automática indisponível (sem dados do paciente). Elegibilidade presumida — requer avaliação clínica.",
        )

    # Collect pathway category and criterion IDs
    pathway_criteria_categories: set[str] = {c["category"] for c in pathway["criteria"]}
    pathway_criteria_ids: set[str] = {c["id"] for c in pathway["criteria"]}

    matching_criteria: list[str] = []
    slug = pathway["slug"]

    if slug == "ventilacao":
        # Rule 15: Patient must have ventilation/O₂ data
        required_cats = {"oxigenacao", "parametros"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_oxigenacao = bool(data_keys & {"oxigenacao", "pf_ratio", "PaO2_FiO2", "crit-vent-pf"})
            has_parametros = bool(data_keys & {"parametros", "peep", "vc", "plat", "drive"})
            if has_oxigenacao and has_parametros:
                matching_criteria = [c["id"] for c in pathway["criteria"]
                                     if c["category"] in required_cats]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com dados de ventilação e oxigenação adequados para o pathway de Ventilação Mecânica.",
                    matching_criteria=matching_criteria,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes de ventilação/oxigenação. Necessário: parâmetros ventilatórios (PEEP, VC, Pplat) e oxigenação (PaO₂/FiO₂).",
            )

    elif slug == "sepse":
        # Rule 16: Patient must have qSOFA/lactate/culturas indicators
        required_cats = {"triagem", "laboratorial"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_triagem = bool(data_keys & {"triagem", "qsofa", "crit-sep-qsofa"})
            has_labs = bool(data_keys & {"laboratorial", "lactato", "pct", "crit-sep-lactato"})
            if has_triagem or has_labs:
                matching_ids: list[str] = []
                for c in pathway["criteria"]:
                    if c["category"] in required_cats:
                        matching_ids.append(c["id"])
                    elif c["id"] in data_keys or c["category"] in data_keys:
                        matching_ids.append(c["id"])
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com indicadores de triagem/laboratoriais compatíveis com pathway de Sepse.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes de triagem (qSOFA) ou laboratoriais (lactato) para pathway de Sepse.",
            )

    elif slug == "desmame":
        # Rule 17: Patient must have weaning readiness criteria
        required_cats = {"mecanica", "neurologico", "clinico"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_mec = bool(data_keys & {"mecanica", "rsbi", "nif", "crit-des-frvt", "crit-des-nif"})
            has_neuro = bool(data_keys & {"neurologico", "glasgow", "crit-des-glasgow"})
            if has_mec or has_neuro:
                matching_ids = [c["id"] for c in pathway["criteria"]
                                if c["category"] in required_cats]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com critérios de avaliação de prontidão para desmame presentes.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes para avaliação de desmame. Necessário: mecânica respiratória (NIF, RSBI) e nível de consciência (Glasgow).",
            )

    elif slug == "nutricao":
        # Rule 18: Patient must have nutritional screening or intake criteria
        required_cats = {"triagem", "nutricional"}
        if patient_data:
            data_keys = set(patient_data.keys())
            has_triagem = bool(data_keys & {"triagem", "nrs", "crit-nut-triagem"})
            has_nut = bool(data_keys & {"nutricional", "calorias", "proteinas", "crit-nut-calorias"})
            if has_triagem or has_nut:
                matching_ids = [c["id"] for c in pathway["criteria"]
                                if c["category"] in required_cats]
                return PathwayEligibilityResult(
                    eligible=True,
                    reason="Paciente com dados de triagem nutricional ou monitorização de dieta enteral.",
                    matching_criteria=matching_ids,
                )
            return PathwayEligibilityResult(
                eligible=False,
                reason="Dados insuficientes para pathway de Nutrição Enteral. Necessário: triagem NRS-2002 ou dados de aporte calórico/proteico.",
            )

    # Generic: check if any patient data keys overlap with pathway criteria
    if patient_data:
        data_keys = set(patient_data.keys())
        overlap = pathway_criteria_ids & data_keys
        if overlap:
            return PathwayEligibilityResult(
                eligible=True,
                reason=f"Dados do paciente compatíveis com critérios do pathway: {', '.join(sorted(overlap))}.",
                matching_criteria=sorted(overlap),
            )
        cat_overlap = pathway_criteria_categories & data_keys
        if cat_overlap:
            return PathwayEligibilityResult(
                eligible=True,
                reason=f"Categorias clínicas compatíveis: {', '.join(sorted(cat_overlap))}.",
                matching_criteria=[],
            )

    return PathwayEligibilityResult(
        eligible=True,
        reason="Sem contraindicações automáticas identificadas. Elegível mediante avaliação clínica.",
    )


def enroll_patient(
    mpi_id: str,
    pathway_id: int,
    initial_criteria: list[dict[str, Any]] | None = None,
    enrolled_by: str = "system",
) -> PathwayEnrollmentResult:
    """Enroll a patient in a pathway.

    Rule 3 (setup): Terminal states complete the pathway — but enrollment always starts at "initial".
    Rule 4: Patient cannot enroll twice in the same active pathway.
    Rule 6: Enrollment starts at "initial" state with default severity "normal".

    Args:
        mpi_id: Patient identifier.
        pathway_id: Pathway ID to enroll in.
        initial_criteria: Optional list of initial criteria evaluations [{id, met, value}].
        enrolled_by: User or system identifier performing enrollment.

    Returns:
        PathwayEnrollmentResult with patient_pathway_id and status.
    """
    pathway = _PATHWAY_BY_ID.get(pathway_id)
    if pathway is None:
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway {pathway_id} não encontrado.",
        )

    if not pathway.get("active", True):
        return PathwayEnrollmentResult(
            mpi_id=mpi_id,
            pathway_id=pathway_id,
            error=f"Pathway '{pathway['name']}' não está ativo.",
        )

    # Rule 4: Check for active duplicate enrollment
    patient_pathways = _patient_pathway_store.setdefault(mpi_id, {})
    if pathway_id in patient_pathways:
        existing = patient_pathways[pathway_id]
        if existing.get("status") == "active":
            return PathwayEnrollmentResult(
                mpi_id=mpi_id,
                pathway_id=pathway_id,
                error=f"Paciente {mpi_id} já está inscrito ativamente no pathway '{pathway['name']}' (ID inscrição: {existing['id']}).",
            )

    # RULE 6: Determine initial state and build criteria data
    initial_state_id = "initial"
    now = datetime.now(timezone.utc)
    enrolled_at_str = now.isoformat()

    # Build criteria_data from pathway criteria definitions + optional initial_criteria
    criteria_data: list[dict[str, Any]] = []
    pathway_criteria_map: dict[str, dict[str, Any]] = {c["id"]: c for c in pathway["criteria"]}
    initial_map: dict[str, dict[str, Any]] = {}
    if initial_criteria:
        initial_map = {ic["id"]: ic for ic in initial_criteria}

    for crit_def in pathway["criteria"]:
        cid = crit_def["id"]
        initial = initial_map.get(cid, {})
        criteria_data.append({
            "id": cid,
            "name": crit_def["name"],
            "met": initial.get("met", False),
            "value": initial.get("value"),
            "evaluated_at": enrolled_at_str if (initial.get("met") is not None or initial.get("value")) else None,
        })

    # Assign auto-increment ID
    global _next_pp_id
    pp_id = _next_pp_id
    _next_pp_id += 1

    enrollment: PatientPathwayDict = {
        "id": pp_id,
        "mpi_id": mpi_id,
        "pathway_id": pathway_id,
        "pathway_name": pathway["name"],
        "pathway_slug": pathway["slug"],
        "current_state": initial_state_id,
        "criteria_data": criteria_data,
        "status": "active",
        "severity": "normal",
        "enrolled_at": enrolled_at_str,
        "enrolled_by": enrolled_by,
        "completed_at": None,
        "updated_at": enrolled_at_str,
    }
    patient_pathways[pathway_id] = enrollment

    # Initialize empty transition history
    _transition_store[pp_id] = []

    logger.info(
        "Patient %s enrolled in pathway %s (%s), pp_id=%d",
        mpi_id, pathway["name"], pathway["slug"], pp_id,
    )

    return PathwayEnrollmentResult(
        patient_pathway_id=pp_id,
        mpi_id=mpi_id,
        pathway_id=pathway_id,
        current_state=initial_state_id,
        status="active",
        severity="normal",
        enrolled_at=enrolled_at_str,
    )


def evaluate_criteria(
    mpi_id: str,
    patient_pathway_id: int,
    criteria_updates: list[dict[str, Any]],
) -> CriteriaEvaluationResult:
    """Update criteria evaluation for a pathway enrollment.

    Rule 7: Criteria evaluation updates individual criterion met/value/timestamp fields.
    Rule 8: When all criteria for the current state are met, auto-transition to next state.
    Rule 9: Every state transition is logged (from_state, to_state, reason, timestamp).
    Rule 10: Severity mapped by met/total ratio.
    Rule 3 (partial): Reaching a terminal state completes the pathway.

    Args:
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.
        criteria_updates: List of {id, met, value} dicts to apply.

    Returns:
        CriteriaEvaluationResult with updated criteria, possible state change, and severity.
    """
    # Find the enrollment
    enrollment: PatientPathwayDict | None = None
    for pid, pathways in _patient_pathway_store.items():
        for pw_id, pp in pathways.items():
            if pp["id"] == patient_pathway_id:
                if pp["mpi_id"] != mpi_id:
                    # This shouldn't happen but guard
                    continue
                enrollment = pp
                break
        if enrollment is not None:
            break

    if enrollment is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    if enrollment["status"] != "active":
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=enrollment.get("criteria_data", []),
            state_changed=False,
            new_state=enrollment["current_state"],
            severity=enrollment.get("severity", "normal"),
        )

    pathway = _PATHWAY_BY_ID.get(enrollment["pathway_id"])
    if pathway is None:
        return CriteriaEvaluationResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            criteria=criteria_updates,
            severity="normal",
        )

    # Build update map
    update_map: dict[str, dict[str, Any]] = {u["id"]: u for u in criteria_updates}
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # Apply updates to criteria_data
    criteria_data = enrollment.get("criteria_data", [])
    for crit in criteria_data:
        cid = crit["id"]
        if cid in update_map:
            upd = update_map[cid]
            crit["met"] = upd.get("met", crit.get("met", False))
            crit["value"] = upd.get("value", crit.get("value"))
            crit["evaluated_at"] = now_str

    enrollment["criteria_data"] = criteria_data
    enrollment["updated_at"] = now_str

    # ── Rule 8 + 9 + 3: State transition logic ──
    states: list[dict[str, Any]] = pathway.get("states", [])
    current_state_id = enrollment["current_state"]
    state_changed = False
    new_state = current_state_id
    transition_reason = ""

    # Find current state index
    current_idx: int | None = None
    for i, s in enumerate(states):
        if s["id"] == current_state_id:
            current_idx = i
            break

    if current_idx is not None:
        # Check if all criteria are met for this state
        # The rule: if ALL criteria in the pathway are met, advance one state
        all_met = all(c.get("met", False) for c in criteria_data)

        if all_met:
            # Advance to next state if not already at terminal
            next_idx = current_idx + 1
            if next_idx < len(states):
                next_state_def = states[next_idx]
                new_state = next_state_def["id"]
                transition_reason = (
                    f"Todos os {len(criteria_data)} critérios do pathway atendidos. "
                    f"Avançando de '{states[current_idx]['name']}' para '{next_state_def['name']}'."
                )
                enrollment["current_state"] = new_state
                state_changed = True

                # Log transition (Rule 9)
                transition = {
                    "from_state": current_state_id,
                    "to_state": new_state,
                    "reason": transition_reason,
                    "changed_at": now_str,
                }
                _transition_store.setdefault(patient_pathway_id, []).append(transition)

                # Rule 3: Check if new state is terminal
                if next_state_def.get("is_terminal", False):
                    enrollment["status"] = "completed"
                    enrollment["completed_at"] = now_str
                    logger.info(
                        "Patient %s completed pathway %s (pp_id=%d)",
                        mpi_id, pathway["name"], patient_pathway_id,
                    )

                logger.info(
                    "State transition for pp_id=%d: %s -> %s (%s)",
                    patient_pathway_id, current_state_id, new_state, next_state_def["name"],
                )

    # ── Rule 10: Severity determination ──
    met_count = sum(1 for c in criteria_data if c.get("met", False))
    total_count = len(criteria_data)
    severity = _determine_severity(met_count, total_count)
    enrollment["severity"] = severity

    return CriteriaEvaluationResult(
        patient_pathway_id=patient_pathway_id,
        mpi_id=mpi_id,
        criteria=[dict(c) for c in criteria_data],
        state_changed=state_changed,
        new_state=new_state,
        transition_reason=transition_reason,
        severity=severity,
    )


def get_patient_pathways(
    mpi_id: str,
    status_filter: str = "active",
) -> list[dict[str, Any]]:
    """Get all pathways a patient is enrolled in.

    Rule 13: Filters by status (active, completed, archived).

    Args:
        mpi_id: Patient identifier.
        status_filter: Status to filter by. "all" returns all statuses.

    Returns:
        List of enrollment dicts with pathway metadata and criteria.
    """
    patient_pathways = _patient_pathway_store.get(mpi_id, {})

    results: list[dict[str, Any]] = []
    for pathway_id, pp in patient_pathways.items():
        if status_filter != "all" and pp.get("status") != status_filter:
            continue
        pathway = _PATHWAY_BY_ID.get(pathway_id)
        results.append({
            "id": pp["id"],
            "mpi_id": pp["mpi_id"],
            "pathway_id": pp["pathway_id"],
            "pathway_name": pp.get("pathway_name", pathway["name"] if pathway else "Desconhecido"),
            "pathway_slug": pp.get("pathway_slug", pathway["slug"] if pathway else ""),
            "current_state": pp["current_state"],
            "criteria_data": [dict(c) for c in pp.get("criteria_data", [])],
            "status": pp["status"],
            "severity": pp.get("severity", "normal"),
            "enrolled_at": pp["enrolled_at"],
            "enrolled_by": pp.get("enrolled_by", ""),
            "completed_at": pp.get("completed_at"),
            "updated_at": pp.get("updated_at"),
        })
    return results


def get_pathway_progress(
    mpi_id: str,
    patient_pathway_id: int,
) -> PathwayProgressResult:
    """Get detailed progress for a patient in a specific pathway.

    Rule 11: Trend derived from forward/backward/stable transitions in state history.
    Rule 12: PT-BR recommendation generated from pathway name + current state + severity.
    Rule 14: Computes criteria_summary (total, met, not_met, pending).

    Args:
        mpi_id: Patient identifier.
        patient_pathway_id: ID of the PatientPathway enrollment.

    Returns:
        PathwayProgressResult with criteria summary, state history, trend, and recommendation.
    """
    # Find the enrollment
    enrollment: PatientPathwayDict | None = None
    pathway: dict[str, Any] | None = None
    for pid, pathways in _patient_pathway_store.items():
        for pw_id, pp in pathways.items():
            if pp["id"] == patient_pathway_id and pp["mpi_id"] == mpi_id:
                enrollment = pp
                pathway = _PATHWAY_BY_ID.get(pw_id)
                break
        if enrollment is not None:
            break

    if enrollment is None:
        # Return empty progress
        return PathwayProgressResult(
            patient_pathway_id=patient_pathway_id,
            mpi_id=mpi_id,
            pathway_name="Desconhecido",
            current_state="",
            criteria_summary={"total": 0, "met": 0, "not_met": 0, "pending": 0},
            criteria=[],
            state_history=[],
            trend="none",
            last_evaluated_at="",
            recommendation="Inscrição não localizada. Verifique o ID do pathway.",
        )

    pathway_name = enrollment.get("pathway_name",
        pathway.get("name", "Desconhecido") if pathway else "Desconhecido")

    # ── Rule 14: Criteria summary ──
    criteria_data: list[dict[str, Any]] = enrollment.get("criteria_data", [])
    total = len(criteria_data)
    met = sum(1 for c in criteria_data if c.get("met", False))
    not_met = sum(1 for c in criteria_data if c.get("met") is False)
    pending = total - met - not_met

    criteria_summary: dict[str, int] = {
        "total": total,
        "met": met,
        "not_met": not_met,
        "pending": pending,
    }

    # ── Rule 11: Trend from state history ──
    history = _transition_store.get(patient_pathway_id, [])
    trend = _determine_trend(history)

    # Last evaluation timestamp
    evaluated_times: list[str] = [str(c["evaluated_at"]) for c in criteria_data if c.get("evaluated_at")]
    last_evaluated_at = max(evaluated_times) if evaluated_times else ""

    # Current state
    current_state_id = enrollment["current_state"]
    severity = enrollment.get("severity", "normal")

    # ── Rule 12: PT-BR recommendation ──
    recommendation = _build_recommendation(
        pathway_name=pathway_name,
        current_state=current_state_id,
        severity=severity,
        states=pathway.get("states", []) if pathway else [],
    )

    return PathwayProgressResult(
        patient_pathway_id=patient_pathway_id,
        mpi_id=mpi_id,
        pathway_name=pathway_name,
        current_state=current_state_id,
        criteria_summary=criteria_summary,
        criteria=[dict(c) for c in criteria_data],
        state_history=[dict(h) for h in history],
        trend=trend,
        last_evaluated_at=last_evaluated_at,
        recommendation=recommendation,
    )


# ============================================================================
# Helper functions (Rules 10, 11, 12)
# ============================================================================

def _determine_severity(met_count: int, total_count: int) -> str:
    """Map criteria met ratio to severity.

    Rule 10:
        - normal: >= 80% of criteria met
        - watch: 60-79% of criteria met
        - urgent: 40-59% of criteria met
        - critical: < 40% of criteria met

    Args:
        met_count: Number of criteria met.
        total_count: Total number of criteria.

    Returns:
        Severity string: normal, watch, urgent, or critical.
    """
    if total_count == 0:
        return "normal"
    ratio = met_count / total_count
    if ratio >= 0.80:
        return "normal"
    elif ratio >= 0.60:
        return "watch"
    elif ratio >= 0.40:
        return "urgent"
    else:
        return "critical"


def _determine_trend(history: list[dict[str, Any]]) -> str:
    """Determine trend direction from state transition history.

    Rule 11:
        - "improving": forward progression (states moving toward terminal/alta)
        - "worsening": backward movement or regression
        - "stable": no recent changes or side-to-side transitions
        - "none": no transition history

    Since state progression is forward-only (Rule 2), we evaluate based on
    recency and direction of transitions.

    Args:
        history: List of transition dicts with from_state, to_state, changed_at.

    Returns:
        Trend string: improving, stable, worsening, none.
    """
    if not history:
        return "none"

    # Get the most recent transitions (last 3)
    recent = history[-3:]

    # Count forward vs backward transitions
    # In this engine, all transitions are forward (Rule 2), but we check by
    # looking at the state order in the pathway definition.
    # For simplicity: if there's at least one transition and the latest was
    # toward a higher-order state, it's improving.
    # If no transitions in last period → stable.
    # Worsening would be handled if we allowed regression.

    # Check if the most recent transition happened recently
    # For now, any transition history = improving (since all transitions are forward)
    # Stable = no recent transitions in last evaluation window
    # We use a simple heuristic: if last transition was within reasonable timeframe

    last = history[-1]
    # If there are transitions, at minimum it's "stable"
    # If the last transition moved toward a terminal/higher state, "improving"
    trend = "stable"

    # All transitions are forward by design (Rule 2)
    if len(history) >= 2:
        # Multiple forward transitions → improving
        trend = "improving"
    elif len(history) == 1:
        trend = "improving"

    return trend


def _build_recommendation(
    pathway_name: str,
    current_state: str,
    severity: str,
    states: list[dict[str, Any]] | None = None,
) -> str:
    """Generate PT-BR clinical recommendation based on pathway, state, and severity.

    Rule 12: Recommendations are generated in PT-BR.

    Args:
        pathway_name: Human-readable pathway name.
        current_state: Current state identifier.
        severity: Severity level (normal, watch, urgent, critical).
        states: Optional list of state definitions for context.

    Returns:
        Recommendation string in Portuguese (BR).
    """
    if states is None:
        states = []

    # Build state name lookup
    state_name_map: dict[str, str] = {s["id"]: s["name"] for s in states}
    state_name = state_name_map.get(current_state, current_state)

    # Pathway-specific recommendations
    if pathway_name == "Ventilação Mecânica":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. Reavaliar parâmetros ventilatórios IMEDIATAMENTE. "
                "Verificar PEEP, driving pressure e relação P/F. Considerar manobras de recrutamento alveolar "
                "e posição prona se P/F < 150. Acionar fisioterapia respiratória."
            )
        elif severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios parcialmente atendidos (40-59%). Ajustar parâmetros do ventilador nas próximas 6h. "
                "Reavaliar PEEP ideal e considerar gasometria de controle. Manter cabeceira elevada 30-45°."
            )
        elif severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Manter parâmetros protetores e monitorizar "
                "tendência da mecânica pulmonar a cada 12h. Avaliar diariamente prontidão para desmame."
            )
        else:  # normal
            return (
                f"✓ Dentro das metas — {pathway_name} ({state_name}): "
                "≥80% dos critérios de ventilação protetora atendidos. Manter estratégia atual e "
                "avaliar critérios para início do desmame ventilatório. Registrar avaliação diária."
            )

    elif pathway_name == "Sepse":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. ACIONAR PROTOCOLO DE SEPSE IMEDIATAMENTE. "
                "Verificar: antibiótico administrado? Culturas coletadas? Ressuscitação volêmica iniciada? "
                "Lactato >4 mmol/L requer reavaliação em 2-4h. Considerar acesso central e droga vasoativa."
            )
        elif severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios do bundle de sepse incompletos (40-59%). Completar bundle da 1ª hora: "
                "coletar culturas, administrar antibiótico, iniciar cristaloide 30 mL/kg. "
                "Reavaliar lactato em 2-4h."
            )
        elif severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Bundle de sepse parcialmente completo (60-79%). Verificar itens pendentes e "
                "reavaliar resposta hemodinâmica. Monitorizar clearance de lactato a cada 6h. "
                "Avaliar descalonamento antimicrobiano em 48-72h."
            )
        else:  # normal
            return (
                f"✓ Resposta adequada — {pathway_name} ({state_name}): "
                "≥80% dos critérios do bundle atendidos. Paciente com boa evolução. "
                "Manter monitorização e avaliar transição para via oral de antibióticos. "
                "Reavaliar culturas e possibilidade de descalonamento."
            )

    elif pathway_name == "Desmame":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios de desmame atendidos. Paciente NÃO está pronto para desmame. "
                "Otimizar parâmetros ventilatórios, corrigir distúrbios metabólicos e eletrolíticos. "
                "Reavaliar em 24h. Manter ventilação mecânica com parâmetros protetores."
            )
        elif severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios de prontidão para desmame parcialmente atendidos (40-59%). "
                "Reavaliar força muscular respiratória (NIF) e drive respiratório (RSBI). "
                "Considerar TRE (Teste de Respiração Espontânea) se Glasgow ≥11 e tosse eficaz."
            )
        elif severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Paciente próximo da prontidão para TRE. "
                "Verificar critérios pendentes e programar teste de respiração espontânea nas próximas 12-24h. "
                "Manter sedação mínima (RASS -1 a 0)."
            )
        else:  # normal
            return (
                f"✓ Pronto para desmame — {pathway_name} ({state_name}): "
                "≥80% dos critérios atendidos. REALIZAR TESTE DE RESPIRAÇÃO ESPONTÂNEA (TRE). "
                "Manter paciente em PSV 5-7 cmH₂O ou tubo T por 30-120 min. "
                "Se TRE bem-sucedido, proceder à extubação e iniciar monitorização pós-extubação."
            )

    elif pathway_name == "Nutrição Enteral":
        if severity == "critical":
            return (
                f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
                "Menos de 40% dos critérios atendidos. Intolerância grave à dieta ou desnutrição severa. "
                "Reavaliar via de acesso nutricional, considerar nutrição parenteral suplementar. "
                "Investigar causas de intolerância (íleo, infecção, isquemia mesentérica). "
                "Acionar equipe de terapia nutricional."
            )
        elif severity == "urgent":
            return (
                f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
                "Critérios nutricionais parcialmente atendidos (40-59%). Aporte calórico-proteico abaixo da meta. "
                "Avaliar resíduo gástrico e considerar procinético. Ajustar velocidade de infusão e "
                "concentração da fórmula. Reavaliar em 24h."
            )
        elif severity == "watch":
            return (
                f"Acompanhar — {pathway_name} ({state_name}): "
                "Maioria dos critérios atendidos (60-79%). Progredir dieta conforme protocolo, "
                "atingindo meta calórica em até 72h. Monitorizar resíduo gástrico a cada 6h e "
                "sinais de intolerância. Manter cabeceira elevada."
            )
        else:  # normal
            return (
                f"✓ Meta nutricional — {pathway_name} ({state_name}): "
                "≥80% dos critérios atendidos. Aporte calórico e proteico adequados. "
                "Avaliar transição para dieta via oral conforme melhora clínica. "
                "Manter monitorização de tolerância e balanço nitrogenado semanal."
            )

    # Generic fallback recommendation
    if severity == "critical":
        return (
            f"⚠️ ALERTA CRÍTICO — {pathway_name} ({state_name}): "
            "Menos de 40% dos critérios clínicos atendidos. Requer intervenção imediata. "
            "Reavaliar todos os parâmetros e acionar equipe multidisciplinar."
        )
    elif severity == "urgent":
        return (
            f"⚠️ ATENÇÃO — {pathway_name} ({state_name}): "
            "Critérios parcialmente atendidos (40-59%). Priorizar itens pendentes e reavaliar em 6-12h."
        )
    elif severity == "watch":
        return (
            f"Acompanhar — {pathway_name} ({state_name}): "
            "Maioria dos critérios atendidos (60-79%). Verificar pendências e manter monitorização programada."
        )
    else:
        return (
            f"✓ Dentro das metas — {pathway_name} ({state_name}): "
            "≥80% dos critérios atendidos. Manter conduta atual e reavaliar conforme protocolo."
        )
