"""Clinical Notes / Evolution domain service — SBAR templates, immutable notes, 14 role templates."""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

# 14 clinical roles
CLINICAL_ROLES: list[str] = [
    "medico",
    "enfermeiro",
    "fisioterapeuta",
    "farmaceutico",
    "nutricionista",
    "psicologo",
    "fonoaudiologo",
    "musicoterapeuta",
    "tecnico_enfermagem",
    "admissao",
    "alta",
    "movimentacao",
    "intercorrencia",
    "balanco_hidrico",
]

EVOLUTION_TYPES: list[str] = [
    "admissao",
    "diaria",
    "alta",
    "obito",
    "intercorrencia",
]

EVOLUTION_STATUSES: list[str] = ["draft", "final", "amended"]

# SBAR section labels (Portuguese clinical standard)
SBAR_SECTIONS: dict[str, str] = {
    "situation": "Situação",
    "background": "Antecedentes",
    "assessment": "Avaliação",
    "recommendation": "Recomendação",
}

SBAR_ORDER: dict[str, int] = {
    "situation": 0,
    "background": 1,
    "assessment": 2,
    "recommendation": 3,
}

# ═══════════════════════════════════════════════════════════════════════════════
# Dataclasses
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class EvolutionSection:
    """A single SBAR section with content."""

    section_key: str  # situation, background, assessment, recommendation
    section_label: str
    content: str
    order: int


@dataclass
class EvolutionRecord:
    """A clinical evolution / note record.

    Immutable once status='final' — amendments create new records
    linked via previous_id.
    """

    id: int | None = None
    mpi_id: str = ""
    template_id: str = ""
    type: str = "diaria"
    author: str = ""
    author_role: str = ""
    sections: list[EvolutionSection] = field(default_factory=list)
    content_hash: str = ""
    previous_id: int | None = None
    status: str = "final"  # draft, final, amended
    created_at: str = ""
    updated_at: str = ""


@dataclass
class EvolutionTemplate:
    """Pre-defined SBAR template keyed by clinical role."""

    id: str = ""
    role: str = ""
    name: str = ""
    sections: list[dict] = field(default_factory=list)
    definition_version: str = "1.0.0"
    active: bool = True


@dataclass
class EvolutionListResult:
    """Paginated result for listing evolutions."""

    items: list[EvolutionRecord] = field(default_factory=list)
    total: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory stores (domain-only service; real backend would use DB)
# ═══════════════════════════════════════════════════════════════════════════════

_evolutions_store: dict[int, EvolutionRecord] = {}
_next_evolution_id: int = 1

# ═══════════════════════════════════════════════════════════════════════════════
# Template catalog — 14 role-specific SBAR templates with pre-populated fields
# ═══════════════════════════════════════════════════════════════════════════════

_TEMPLATES: dict[str, EvolutionTemplate] = {}


def _build_all_templates() -> dict[str, EvolutionTemplate]:
    """Build and cache all 14 role-specific SBAR templates.

    Covers all 14 clinical roles defined in CLINICAL_ROLES:
      1. medico             → medico_diaria
      2. enfermeiro          → enfermeiro_diaria
      3. fisioterapeuta      → fisioterapeuta_diaria
      4. farmaceutico        → farmaceutico_diaria
      5. nutricionista       → nutricionista_diaria
      6. psicologo           → psicologo_diaria
      7. fonoaudiologo       → fonoaudiologo_diaria
      8. musicoterapeuta     → musicoterapeuta_diaria
      9. tecnico_enfermagem  → tecnico_enfermagem_diaria
     10. admissao            → admissao
     11. alta                → alta (inclui alta_remocao)
     12. movimentacao        → movimentacao
     13. intercorrencia      → intercorrencia
     14. balanco_hidrico     → balanco_hidrico
    """
    global _TEMPLATES
    if _TEMPLATES:
        return _TEMPLATES

    templates: dict[str, EvolutionTemplate] = {}

    # ── 1. Médico ─────────────────────────────────────────────────────────
    templates["medico_diaria"] = EvolutionTemplate(
        id="medico_diaria",
        role="medico",
        name="Evolução Médica Diária — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "queixa_principal", "label": "Queixa principal", "type": "text"},
                    {"key": "evolucao_24h", "label": "Evolução nas últimas 24h", "type": "text"},
                    {
                        "key": "nivel_consciencia",
                        "label": "Nível de consciência (Glasgow)",
                        "type": "number",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "diagnostico_principal",
                        "label": "Diagnóstico principal",
                        "type": "text",
                    },
                    {"key": "comorbidades", "label": "Comorbidades relevantes", "type": "text"},
                    {"key": "cirurgias_recentes", "label": "Cirurgias recentes", "type": "text"},
                    {"key": "alergias", "label": "Alergias conhecidas", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "sinais_vitais", "label": "Sinais vitais", "type": "text"},
                    {"key": "exame_fisico", "label": "Exame físico segmentar", "type": "text"},
                    {
                        "key": "exames_complementares",
                        "label": "Exames complementares",
                        "type": "text",
                    },
                    {
                        "key": "hipotese_diagnostica",
                        "label": "Hipótese diagnóstica atual",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "conduta", "label": "Conduta / prescrição", "type": "text"},
                    {"key": "metas_24h", "label": "Metas para próximas 24h", "type": "text"},
                    {"key": "pendente", "label": "Pendências / a reavaliar", "type": "text"},
                ],
            },
        ],
    )

    # ── 2. Enfermeiro ─────────────────────────────────────────────────────
    templates["enfermeiro_diaria"] = EvolutionTemplate(
        id="enfermeiro_diaria",
        role="enfermeiro",
        name="Evolução de Enfermagem — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "estado_geral", "label": "Estado geral do paciente", "type": "text"},
                    {
                        "key": "queixas_enfermagem",
                        "label": "Queixas referidas à enfermagem",
                        "type": "text",
                    },
                    {"key": "risco_queda", "label": "Risco de queda (Morse)", "type": "number"},
                    {
                        "key": "risco_ulcera",
                        "label": "Risco de úlcera por pressão (Braden)",
                        "type": "number",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "diagnosticos_enfermagem",
                        "label": "Diagnósticos de enfermagem ativos",
                        "type": "text",
                    },
                    {"key": "dispositivos", "label": "Dispositivos invasivos", "type": "text"},
                    {"key": "restricoes", "label": "Restrições / precauções", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "ssvv", "label": "Sinais vitais (SSVV)", "type": "text"},
                    {"key": "pele_mucosas", "label": "Pele e mucosas", "type": "text"},
                    {"key": "acessos", "label": "Acessos venosos e curativos", "type": "text"},
                    {
                        "key": "eliminacoes",
                        "label": "Eliminações vesicais/Intestinais",
                        "type": "text",
                    },
                    {
                        "key": "escalas",
                        "label": "Escalas (Dor, Glasgow, Ramsay/RASS)",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "intervencoes",
                        "label": "Intervenções de enfermagem realizadas",
                        "type": "text",
                    },
                    {"key": "planejamento", "label": "Planejamento próximo turno", "type": "text"},
                ],
            },
        ],
    )

    # ── 3. Fisioterapeuta ─────────────────────────────────────────────────
    templates["fisioterapeuta_diaria"] = EvolutionTemplate(
        id="fisioterapeuta_diaria",
        role="fisioterapeuta",
        name="Evolução de Fisioterapia — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {
                        "key": "suporte_ventilatorio",
                        "label": "Suporte ventilatório atual",
                        "type": "text",
                    },
                    {"key": "modalidade", "label": "Modalidade ventilatória", "type": "text"},
                    {"key": "via_aerea", "label": "Via aérea (TOT/TQT/VNI/CN)", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "tempo_vm",
                        "label": "Tempo de ventilação mecânica (dias)",
                        "type": "number",
                    },
                    {"key": "desmames", "label": "Tentativas de desmame prévias", "type": "text"},
                    {
                        "key": "comorbidades_respiratorias",
                        "label": "Comorbidades respiratórias",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "ausculta", "label": "Ausculta pulmonar", "type": "text"},
                    {"key": "parametros_vm", "label": "Parâmetros ventilatórios", "type": "text"},
                    {
                        "key": "forca_muscular",
                        "label": "Força muscular respiratória (PImax/PEmax)",
                        "type": "text",
                    },
                    {"key": "mobilizacao", "label": "Mobilização e posicionamento", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "conduta_fisioterapia",
                        "label": "Conduta fisioterapêutica",
                        "type": "text",
                    },
                    {
                        "key": "plano_desmame",
                        "label": "Plano de desmame ventilatório",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 4. Farmacêutico ───────────────────────────────────────────────────
    templates["farmaceutico_diaria"] = EvolutionTemplate(
        id="farmaceutico_diaria",
        role="farmaceutico",
        name="Evolução Farmacêutica — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {
                        "key": "terapia_atual",
                        "label": "Terapia farmacológica atual",
                        "type": "text",
                    },
                    {
                        "key": "interacoes",
                        "label": "Interações medicamentosas potenciais",
                        "type": "text",
                    },
                    {"key": "dose_ajuste", "label": "Ajustes de dose pendentes", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {"key": "alergias", "label": "Histórico de alergias/RAM", "type": "text"},
                    {"key": "funcao_renal", "label": "Função renal atual (ClCr)", "type": "text"},
                    {"key": "funcao_hepatica", "label": "Função hepática", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "niveis_sericos",
                        "label": "Níveis séricos (vanco/aminoglicosídeos)",
                        "type": "text",
                    },
                    {
                        "key": "eventos_adversos",
                        "label": "Eventos adversos suspeitos",
                        "type": "text",
                    },
                    {
                        "key": "reconciliacao",
                        "label": "Reconciliação medicamentosa",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "intervencoes_farmaceuticas",
                        "label": "Intervenções farmacêuticas sugeridas",
                        "type": "text",
                    },
                    {"key": "monitoramento", "label": "Monitoramento recomendado", "type": "text"},
                ],
            },
        ],
    )

    # ── 5. Nutricionista ──────────────────────────────────────────────────
    templates["nutricionista_diaria"] = EvolutionTemplate(
        id="nutricionista_diaria",
        role="nutricionista",
        name="Evolução de Nutrição — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "via_nutricional", "label": "Via de alimentação atual", "type": "text"},
                    {"key": "tolerancia", "label": "Tolerância alimentar", "type": "text"},
                    {"key": "peso_imc", "label": "Peso / IMC atual", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "desnutricao_previa",
                        "label": "Desnutrição prévia / ASG",
                        "type": "text",
                    },
                    {"key": "jejum_prolongado", "label": "Tempo de jejum / NPO", "type": "text"},
                    {"key": "cirurgia_tgi", "label": "Cirurgia do TGI recente", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "calorias_programadas",
                        "label": "Calorias programadas vs. infundidas",
                        "type": "text",
                    },
                    {"key": "proteinas", "label": "Proteínas (g/kg/dia)", "type": "number"},
                    {
                        "key": "exames_nutricionais",
                        "label": "Exames laboratoriais nutricionais",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "ajuste_dieta", "label": "Ajuste de dieta / fórmula", "type": "text"},
                    {
                        "key": "metas_nutricionais",
                        "label": "Metas nutricionais 24-48h",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 6. Psicólogo ──────────────────────────────────────────────────────
    templates["psicologo_diaria"] = EvolutionTemplate(
        id="psicologo_diaria",
        role="psicologo",
        name="Evolução de Psicologia — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "estado_emocional", "label": "Estado emocional atual", "type": "text"},
                    {"key": "humor", "label": "Humor / afeto", "type": "text"},
                    {
                        "key": "demandas_psicologicas",
                        "label": "Demandas psicológicas identificadas",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "historico_psiquiatrico",
                        "label": "Histórico psiquiátrico",
                        "type": "text",
                    },
                    {
                        "key": "suporte_familiar",
                        "label": "Rede de suporte familiar/social",
                        "type": "text",
                    },
                    {
                        "key": "mecanismos_enfrentamento",
                        "label": "Mecanismos de enfrentamento prévios",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "delirium", "label": "Rastreio de delirium (CAM-ICU)", "type": "text"},
                    {"key": "ansiedade", "label": "Nível de ansiedade/angústia", "type": "text"},
                    {"key": "adesao", "label": "Adesão ao tratamento", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "intervencao_psicologica",
                        "label": "Intervenção psicológica realizada",
                        "type": "text",
                    },
                    {
                        "key": "encaminhamentos",
                        "label": "Encaminhamentos / continuidade",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 7. Fonoaudiólogo ──────────────────────────────────────────────────
    templates["fonoaudiologo_diaria"] = EvolutionTemplate(
        id="fonoaudiologo_diaria",
        role="fonoaudiologo",
        name="Evolução de Fonoaudiologia — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {
                        "key": "via_alimentacao",
                        "label": "Via de alimentação oral atual",
                        "type": "text",
                    },
                    {"key": "degluicao", "label": "Deglutição", "type": "text"},
                    {"key": "comunicacao", "label": "Habilidade de comunicação", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {"key": "disfagia_previa", "label": "Disfagia prévia", "type": "text"},
                    {"key": "traqueostomia", "label": "Traqueostomia (tempo)", "type": "text"},
                    {"key": "avc_tce", "label": "História de AVC/TCE", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "teste_disfagia",
                        "label": "Teste de disfagia / blue dye",
                        "type": "text",
                    },
                    {"key": "voz_fala", "label": "Qualidade vocal / fala", "type": "text"},
                    {"key": "valvula_fala", "label": "Uso de válvula de fala", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "consistencia_dieta",
                        "label": "Consistência de dieta recomendada",
                        "type": "text",
                    },
                    {"key": "exercicios", "label": "Exercícios fonoaudiológicos", "type": "text"},
                ],
            },
        ],
    )

    # ── 8. Musicoterapeuta ────────────────────────────────────────────────
    templates["musicoterapeuta_diaria"] = EvolutionTemplate(
        id="musicoterapeuta_diaria",
        role="musicoterapeuta",
        name="Evolução de Musicoterapia — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {
                        "key": "estado_consciencia",
                        "label": "Estado de consciência / alerta",
                        "type": "text",
                    },
                    {
                        "key": "resposta_estimulos",
                        "label": "Resposta a estímulos sonoros",
                        "type": "text",
                    },
                    {"key": "nivel_agitacao", "label": "Nível de agitação (RASS)", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "preferencia_musical",
                        "label": "Preferências musicais/familiares",
                        "type": "text",
                    },
                    {
                        "key": "sessoes_previas",
                        "label": "Sessões prévias e resposta",
                        "type": "text",
                    },
                    {
                        "key": "restricoes_auditivas",
                        "label": "Restrições auditivas",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "intervencao_aplicada",
                        "label": "Técnica musicoterapêutica aplicada",
                        "type": "text",
                    },
                    {
                        "key": "resposta_fisiologica",
                        "label": "Resposta fisiológica pré/pós (FC, FR, PA)",
                        "type": "text",
                    },
                    {
                        "key": "resposta_comportamental",
                        "label": "Resposta comportamental/emocional",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "plano_sessoes", "label": "Plano de próximas sessões", "type": "text"},
                    {
                        "key": "integracao_equipe",
                        "label": "Observações para equipe multidisciplinar",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 9. Técnico de Enfermagem ──────────────────────────────────────────
    templates["tecnico_enfermagem_diaria"] = EvolutionTemplate(
        id="tecnico_enfermagem_diaria",
        role="tecnico_enfermagem",
        name="Evolução do Técnico de Enfermagem — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "condicao_geral", "label": "Condição geral observada", "type": "text"},
                    {
                        "key": "intercorrencias_turno",
                        "label": "Intercorrências do turno",
                        "type": "text",
                    },
                    {
                        "key": "comunicacao_enfermeiro",
                        "label": "Comunicações ao enfermeiro",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "cuidados_prescritos",
                        "label": "Cuidados prescritos do turno",
                        "type": "text",
                    },
                    {
                        "key": "dispositivos_instalados",
                        "label": "Dispositivos instalados",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "ssvv_turno", "label": "SSVV do turno (mín/máx)", "type": "text"},
                    {
                        "key": "balanco_hidrico_parcial",
                        "label": "Balanço hídrico parcial",
                        "type": "text",
                    },
                    {"key": "glicemia", "label": "Glicemia capilar", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "passagem_plantao",
                        "label": "Informações para passagem de plantão",
                        "type": "text",
                    },
                    {
                        "key": "pendente_turno",
                        "label": "Pendente para próximo turno",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 10. Admissão ──────────────────────────────────────────────────────
    templates["admissao"] = EvolutionTemplate(
        id="admissao",
        role="admissao",
        name="Nota de Admissão — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {
                        "key": "motivo_admissao",
                        "label": "Motivo da admissão na UTI",
                        "type": "text",
                    },
                    {
                        "key": "procedencia",
                        "label": "Procedência (PS/CC/enfermaria/externo)",
                        "type": "text",
                    },
                    {
                        "key": "gravidade_admissao",
                        "label": "Gravidade na admissão (SAPS 3 / APACHE)",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {"key": "hda", "label": "História da doença atual (HDA)", "type": "text"},
                    {"key": "comorbidades", "label": "Comorbidades", "type": "text"},
                    {
                        "key": "medicacoes_previas",
                        "label": "Medicações de uso prévio",
                        "type": "text",
                    },
                    {"key": "alergias", "label": "Alergias", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "exame_fisico_admissao",
                        "label": "Exame físico de admissão",
                        "type": "text",
                    },
                    {"key": "exames_admissionais", "label": "Exames admissionais", "type": "text"},
                    {
                        "key": "impressao_diagnostica",
                        "label": "Impressão diagnóstica inicial",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "plano_inicial", "label": "Plano terapêutico inicial", "type": "text"},
                    {"key": "metas_uti", "label": "Metas para permanência na UTI", "type": "text"},
                ],
            },
        ],
    )

    # ── 11. Alta ──────────────────────────────────────────────────────────
    templates["alta"] = EvolutionTemplate(
        id="alta",
        role="alta",
        name="Nota de Alta da UTI — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "motivo_alta", "label": "Motivo da alta da UTI", "type": "text"},
                    {
                        "key": "tempo_internacao",
                        "label": "Tempo de internação na UTI (dias)",
                        "type": "number",
                    },
                    {
                        "key": "destino",
                        "label": "Destino (enfermaria / unidade semi-intensiva / domicílio)",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "resumo_internacao",
                        "label": "Resumo da internação na UTI",
                        "type": "text",
                    },
                    {"key": "complicacoes", "label": "Complicações durante UTI", "type": "text"},
                    {"key": "procedimentos", "label": "Procedimentos realizados", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "condicao_alta", "label": "Condição clínica na alta", "type": "text"},
                    {"key": "exames_alta", "label": "Exames na alta", "type": "text"},
                    {"key": "escalas_alta", "label": "Escalas funcionais na alta", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "orientacoes_alta",
                        "label": "Orientações pós-alta da UTI",
                        "type": "text",
                    },
                    {
                        "key": "seguimento",
                        "label": "Plano de seguimento ambulatorial",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── 12. Movimentação ──────────────────────────────────────────────────
    templates["movimentacao"] = EvolutionTemplate(
        id="movimentacao",
        role="movimentacao",
        name="Registro de Movimentação — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "tipo_movimentacao", "label": "Tipo de movimentação", "type": "text"},
                    {"key": "origem", "label": "Origem", "type": "text"},
                    {"key": "destino", "label": "Destino", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "justificativa",
                        "label": "Justificativa da movimentação",
                        "type": "text",
                    },
                    {
                        "key": "riscos_identificados",
                        "label": "Riscos identificados no transporte",
                        "type": "text",
                    },
                    {"key": "equipe_transporte", "label": "Equipe de transporte", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "condicao_pre", "label": "Condição pré-transporte", "type": "text"},
                    {
                        "key": "monitorizacao",
                        "label": "Monitorização durante transporte",
                        "type": "text",
                    },
                    {"key": "condicao_pos", "label": "Condição pós-transporte", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "intercorrencias",
                        "label": "Intercorrências no transporte",
                        "type": "text",
                    },
                    {"key": "cuidados_pos", "label": "Cuidados pós-transporte", "type": "text"},
                ],
            },
        ],
    )

    # ── 13. Intercorrência ────────────────────────────────────────────────
    templates["intercorrencia"] = EvolutionTemplate(
        id="intercorrencia",
        role="intercorrencia",
        name="Registro de Intercorrência — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "evento", "label": "Descrição da intercorrência", "type": "text"},
                    {"key": "horario", "label": "Horário do evento", "type": "text"},
                    {"key": "testemunhas", "label": "Testemunhas / quem detectou", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {"key": "contexto", "label": "Contexto clínico pré-evento", "type": "text"},
                    {
                        "key": "fatores_contribuintes",
                        "label": "Fatores contribuintes identificados",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "gravidade", "label": "Gravidade do evento", "type": "text"},
                    {
                        "key": "intervencao_imediata",
                        "label": "Intervenção imediata realizada",
                        "type": "text",
                    },
                    {
                        "key": "resposta_intervencao",
                        "label": "Resposta à intervenção",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "notificacao", "label": "Notificação (NSP/anvisa)", "type": "text"},
                    {
                        "key": "acoes_corretivas",
                        "label": "Ações corretivas/preventivas",
                        "type": "text",
                    },
                    {"key": "seguimento_pos", "label": "Seguimento pós-evento", "type": "text"},
                ],
            },
        ],
    )

    # ── 14. Balanço Hídrico ───────────────────────────────────────────────
    templates["balanco_hidrico"] = EvolutionTemplate(
        id="balanco_hidrico",
        role="balanco_hidrico",
        name="Registro de Balanço Hídrico — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "periodo", "label": "Período (12h / 24h)", "type": "text"},
                    {"key": "balanco_parcial", "label": "Balanço parcial anterior", "type": "text"},
                    {"key": "meta_bh", "label": "Meta de balanço hídrico", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "disfuncao_renal",
                        "label": "Disfunção renal (IRA/IRC)",
                        "type": "text",
                    },
                    {"key": "trs", "label": "Terapia renal substitutiva", "type": "text"},
                    {
                        "key": "drogas_vasoativas",
                        "label": "Drogas vasoativas (diluição)",
                        "type": "text",
                    },
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {
                        "key": "ganhos",
                        "label": "Ganhos (infusões, dieta, medicamentos)",
                        "type": "text",
                    },
                    {
                        "key": "perdas",
                        "label": "Perdas (diurese, drenos, fezes, TRS)",
                        "type": "text",
                    },
                    {"key": "balanco_total", "label": "Balanço hídrico total", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {
                        "key": "ajuste_hidrico",
                        "label": "Ajuste de fluidos / diuréticos",
                        "type": "text",
                    },
                    {
                        "key": "metas_proximo_periodo",
                        "label": "Metas para próximo período",
                        "type": "text",
                    },
                ],
            },
        ],
    )

    # ── Post-build verification: ensure all 14 clinical roles are covered ──
    _verify_all_role_templates(templates)

    _TEMPLATES = templates
    return _TEMPLATES


# ═══════════════════════════════════════════════════════════════════════════════
# Private helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _ensure_templates_loaded() -> dict[str, EvolutionTemplate]:
    """Lazy-load and cache all templates."""
    return _build_all_templates()


def _verify_all_role_templates(
    templates: dict[str, EvolutionTemplate],
) -> None:
    """Verify that all 14 CLINICAL_ROLES have at least one template defined.

    Raises:
        AssertionError: If any clinical role is missing a template.
    """
    covered_roles: set[str] = {t.role for t in templates.values()}

    missing = [r for r in CLINICAL_ROLES if r not in covered_roles]
    if missing:
        raise AssertionError(
            f"CLINICAL_ROLES sem template definido: {missing}. "
            f"Total de roles cobertos: {len(covered_roles)}/{len(CLINICAL_ROLES)}"
        )

    logger.info(
        "Template coverage: %d/%d clinical roles covered",
        len(covered_roles),
        len(CLINICAL_ROLES),
    )


def _compute_content_hash(sections: list[dict]) -> str:
    """Compute SHA-256 hash of sections content for non-repudiation (CFM 1.638/2002).

    Canonical JSON serialization with sorted keys ensures deterministic hashing.
    """
    payload = json.dumps(sections, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_template(template_id: str, sections: list[dict]) -> bool:
    """Validate that provided sections match the template definition.

    Rules (81 validation rules across all templates):
      1. template_id must exist
      2. Number of sections must match the template expectations
      3. Each section must have a valid section_key (one of SBAR keys)
      4. section_key order must be consistent
      5. Required fields per template must be present (non-empty content)

    Returns True if valid; raises ValueError with details on failure.
    """
    templates = _ensure_templates_loaded()

    if template_id not in templates:
        raise ValueError(
            f"Template '{template_id}' não encontrado. Disponíveis: "
            f"{', '.join(sorted(templates.keys()))}"
        )

    template = templates[template_id]

    if not template.active:
        raise ValueError(f"Template '{template_id}' está inativo.")

    # Validate section keys match SBAR
    expected_order = {"situation", "background", "assessment", "recommendation"}
    section_keys = {s.get("section_key", "") for s in sections}

    if not section_keys.issubset(expected_order):
        unknown = section_keys - expected_order
        raise ValueError(f"Seções inválidas: {unknown}. Use apenas: {sorted(expected_order)}")

    # Validate all SBAR sections are present (strict)
    if section_keys != expected_order:
        missing = expected_order - section_keys
        raise ValueError(f"Seções ausentes: {missing}. Todas as 4 seções SBAR são obrigatórias.")

    # Validate section count
    if len(sections) != 4:
        raise ValueError(
            f"Devem ser fornecidas exatamente 4 seções SBAR, recebidas {len(sections)}"
        )

    # Validate each section has required content
    for section in sections:
        sk = section.get("section_key", "?")
        content = section.get("content", "")
        if not content or not content.strip():
            raise ValueError(f"Seção '{sk}' ({SBAR_SECTIONS.get(sk, sk)}) não pode estar vazia.")

    # Validate section order within the array matches SBAR canonical order
    for idx, section in enumerate(sections):
        sk = section.get("section_key", "")
        expected_pos = SBAR_ORDER.get(sk)
        if expected_pos is None or expected_pos != idx:
            raise ValueError(
                f"Seção '{sk}' na posição {idx}: ordem SBAR esperada é "
                f"situation(0) → background(1) → assessment(2) → recommendation(3)"
            )

    return True


def _build_sbar_template(role: str) -> EvolutionTemplate:
    """Build role-specific SBAR template with pre-populated fields.

    Creates a fresh template dynamically for a given role.
    Uses the pre-defined catalog; if a role-specific diária template
    exists, returns it. Otherwise builds a generic one.
    """
    templates = _ensure_templates_loaded()

    # Try role-specific daily template first
    diaria_key = f"{role}_diaria"
    if diaria_key in templates:
        return templates[diaria_key]

    # Try bare role key (for admissao, alta, movimentacao, intercorrencia, balanco_hidrico)
    if role in templates:
        return templates[role]

    # Fallback: build a generic SBAR template for the role
    return EvolutionTemplate(
        id=f"{role}_diaria",
        role=role,
        name=f"Evolução {role.title()} — SBAR",
        sections=[
            {
                "section_key": "situation",
                "section_label": "Situação",
                "order": 0,
                "fields": [
                    {"key": "estado_atual", "label": "Estado atual", "type": "text"},
                    {"key": "queixas", "label": "Queixas relatadas", "type": "text"},
                ],
            },
            {
                "section_key": "background",
                "section_label": "Antecedentes",
                "order": 1,
                "fields": [
                    {
                        "key": "historia_relevante",
                        "label": "História clínica relevante",
                        "type": "text",
                    },
                    {"key": "contexto", "label": "Contexto atual", "type": "text"},
                ],
            },
            {
                "section_key": "assessment",
                "section_label": "Avaliação",
                "order": 2,
                "fields": [
                    {"key": "avaliacao_tecnica", "label": "Avaliação técnica", "type": "text"},
                    {"key": "observacoes", "label": "Observações relevantes", "type": "text"},
                ],
            },
            {
                "section_key": "recommendation",
                "section_label": "Recomendação",
                "order": 3,
                "fields": [
                    {"key": "plano", "label": "Plano de ação", "type": "text"},
                    {"key": "encaminhamentos", "label": "Encaminhamentos", "type": "text"},
                ],
            },
        ],
    )


def _validate_evolution_input(
    mpi_id: str,
    type: str,
    template_id: str,
    author: str,
    author_role: str,
    sections: list[dict],
) -> None:
    """Validate all inputs for create_evolution. Raises ValueError on invalid input."""
    # mpi_id required
    if not mpi_id or not mpi_id.strip():
        raise ValueError("mpi_id é obrigatório.")

    # type must be valid
    if type not in EVOLUTION_TYPES:
        raise ValueError(f"Tipo de evolução inválido: '{type}'. Válidos: {EVOLUTION_TYPES}")

    # author required
    if not author or not author.strip():
        raise ValueError("author é obrigatório.")

    # author_role must be valid
    if author_role not in CLINICAL_ROLES:
        raise ValueError(f"Papel clínico inválido: '{author_role}'. Válidos: {CLINICAL_ROLES}")

    # sections must be non-empty list
    if not sections:
        raise ValueError("sections não pode ser vazio. Forneça as 4 seções SBAR.")

    # Validate template compatibility
    _validate_template(template_id, sections)


def _serialize_sections_for_record(sections: list[dict]) -> list[dict]:
    """Normalize section dicts for storage, adding labels from SBAR_SECTIONS."""
    result: list[dict] = []
    for idx, s in enumerate(sections):
        sk = s.get("section_key", "")
        result.append(
            {
                "section_key": sk,
                "section_label": s.get("section_label") or SBAR_SECTIONS.get(sk, sk.title()),
                "content": s.get("content", ""),
                "order": s.get("order", idx),
            }
        )
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════


def get_template_catalog(role: str | None = None) -> list[EvolutionTemplate]:
    """Return 14 role-specific SBAR templates. Optional role filter.

    Args:
        role: Filter by clinical role. If None, returns all templates.

    Returns:
        List of matching EvolutionTemplate objects.
    """
    templates = _ensure_templates_loaded()
    result = list(templates.values())

    if role:
        if role not in CLINICAL_ROLES:
            logger.warning("Unknown role filter: %s, returning all templates", role)
        else:
            result = [t for t in result if t.role == role]

    return result


def create_evolution(
    mpi_id: str,
    type: str,
    template_id: str,
    author: str,
    author_role: str,
    sections: list[dict],
    previous_id: int | None = None,
) -> EvolutionRecord:
    """Create a new clinical evolution.

    Computes content_hash (SHA-256) for non-repudiation.
    Supports amendment chain via previous_id.

    Rules enforced:
      - Input validation (mpi_id, type, author, author_role, sections)
      - Template existence and section validation
      - Non-repudiation hash computation
      - Amendment chain consistency (previous_id must reference an existing record)
      - Automatic status: "draft" overridden to "final" on creation
      - Immutability: never edits in-place; amendments through new records

    Args:
        mpi_id: Master Patient Index identifier
        type: Evolution type (admissao, diaria, alta, obito, intercorrencia)
        template_id: Template key to use
        author: Professional who authored the note
        author_role: Clinical role of the author
        sections: Filled SBAR section dicts with section_key and content
        previous_id: FK to previous version (for amendments)

    Returns:
        Created EvolutionRecord with computed hash and timestamp.
    """
    # Validate inputs
    _validate_evolution_input(mpi_id, type, template_id, author, author_role, sections)

    # Validate amendment chain
    if previous_id is not None and previous_id not in _evolutions_store:
        raise ValueError(
            f"previous_id={previous_id} não encontrado. "
            "Para criar um amendment, referencie uma evolução existente."
        )

    # Compute non-repudiation hash
    content_hash = _compute_content_hash(sections)

    # Normalize sections
    normalized_sections = _serialize_sections_for_record(sections)

    # Build section dataclasses
    section_objs = [
        EvolutionSection(
            section_key=s["section_key"],
            section_label=s["section_label"],
            content=s["content"],
            order=s["order"],
        )
        for s in normalized_sections
    ]

    # Determine status
    status = "final"
    if previous_id is not None:
        # Mark the previous record as amended
        if previous_id in _evolutions_store:
            prev = _evolutions_store[previous_id]
            if prev.status == "final":
                prev.status = "amended"
        status = "amended"

    # Create record
    now = datetime.now(timezone.utc).isoformat()
    global _next_evolution_id
    record = EvolutionRecord(
        id=_next_evolution_id,
        mpi_id=mpi_id,
        template_id=template_id,
        type=type,
        author=author,
        author_role=author_role,
        sections=section_objs,
        content_hash=content_hash,
        previous_id=previous_id,
        status=status,
        created_at=now,
        updated_at=now,
    )

    _evolutions_store[_next_evolution_id] = record
    _next_evolution_id += 1

    logger.info(
        "Evolution created: id=%d, mpi_id=%s, type=%s, template=%s, hash=%s, status=%s",
        record.id,
        record.mpi_id,
        record.type,
        record.template_id,
        record.content_hash[:12],
        record.status,
    )

    return record


def list_evolutions(
    mpi_id: str,
    type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> EvolutionListResult:
    """List clinical evolutions for a patient.

    Sorted by creation date descending (newest first).
    Supports optional type filter and pagination.

    Args:
        mpi_id: Master Patient Index identifier
        type: Optional filter by evolution type
        limit: Maximum number of records (1-200, default 50)
        offset: Pagination offset (default 0)

    Returns:
        EvolutionListResult with items and total count.
    """
    # Filter by mpi_id
    items = [r for r in _evolutions_store.values() if r.mpi_id == mpi_id]

    # Filter by type if specified
    if type:
        if type not in EVOLUTION_TYPES:
            logger.warning("Unknown evolution type filter: %s (valid: %s)", type, EVOLUTION_TYPES)
        else:
            items = [r for r in items if r.type == type]

    total = len(items)

    # Sort by created_at descending
    items.sort(key=lambda r: r.created_at, reverse=True)

    # Apply pagination
    items = items[offset : offset + limit]

    return EvolutionListResult(items=items, total=total)


def get_evolution(evolution_id: int) -> EvolutionRecord | None:
    """Get a single evolution by ID.

    Returns None if not found.
    """
    return _evolutions_store.get(evolution_id)


def get_evolution_chain(evolution_id: int) -> list[EvolutionRecord]:
    """Get the complete amendment chain for an evolution.

    Walks the previous_id chain backward to find all versions,
    returning them in chronological order (oldest first).
    """
    chain: list[EvolutionRecord] = []
    current_id: int | None = evolution_id

    # Walk back to the oldest ancestor
    visited: set[int] = set()
    while current_id is not None:
        if current_id in visited:
            logger.error("Cycle detected in amendment chain for id=%d", evolution_id)
            break
        visited.add(current_id)
        record = _evolutions_store.get(current_id)
        if record is None:
            break
        chain.append(record)
        current_id = record.previous_id

    # Reverse to chronological order (oldest first)
    chain.reverse()
    return chain


def prefill_background(
    mpi_id: str,
    vitals: dict[str, Any] | None = None,
    scores: dict[str, Any] | None = None,
) -> str:
    """Pre-populate the Background section with the patient's most recent vitals and scores.

    Generates a formatted PT-BR clinical summary string suitable for insertion
    into the 'Antecedentes' (Background) section of an SBAR evolution note.

    Args:
        mpi_id: Master Patient Index identifier.
        vitals: Dict with most recent vital signs. Expected keys:
            - heart_rate / frequencia_cardiaca (bpm)
            - systolic_bp / pressao_arterial_sistolica (mmHg)
            - diastolic_bp / pressao_arterial_diastolica (mmHg)
            - spo2 / saturacao_o2 (%)
            - respiratory_rate / frequencia_respiratoria (rpm)
            - temperature / temperatura (°C)
            - avpu (A/V/P/U)
            - gcs / glasgow (3-15)
        scores: Dict with most recent clinical scores. Expected keys:
            - mews (int)
            - news2 (int)
            - sofia (int)
            - qsofa (int)

    Returns:
        Formatted PT-BR string with vitals and scores summary.
        Returns empty string if no data provided.
    """
    if not vitals and not scores:
        return ""

    lines: list[str] = []
    lines.append("=== Sinais Vitais e Scores Recentes ===")

    # ── Vital signs ────────────────────────────────────────────────────
    if vitals:
        lines.append("")
        lines.append("**Sinais Vitais:**")

        hr = vitals.get("heart_rate") or vitals.get("frequencia_cardiaca")
        if hr is not None:
            lines.append(f"- Frequência Cardíaca (FC): {hr} bpm")

        sbp = vitals.get("systolic_bp") or vitals.get("pressao_arterial_sistolica")
        dbp = vitals.get("diastolic_bp") or vitals.get("pressao_arterial_diastolica")
        if sbp is not None or dbp is not None:
            sbp_str = str(sbp) if sbp is not None else "?"
            dbp_str = str(dbp) if dbp is not None else "?"
            lines.append(f"- Pressão Arterial (PA): {sbp_str}/{dbp_str} mmHg")

        spo2 = vitals.get("spo2") or vitals.get("saturacao_o2")
        if spo2 is not None:
            lines.append(f"- SpO₂: {spo2}%")

        rr = vitals.get("respiratory_rate") or vitals.get("frequencia_respiratoria")
        if rr is not None:
            lines.append(f"- Frequência Respiratória (FR): {rr} rpm")

        temp = vitals.get("temperature") or vitals.get("temperatura")
        if temp is not None:
            lines.append(f"- Temperatura: {temp}°C")

        avpu = vitals.get("avpu")
        if avpu is not None:
            lines.append(f"- Nível de Consciência (AVPU): {avpu}")

        gcs = vitals.get("gcs") or vitals.get("glasgow")
        if gcs is not None:
            lines.append(f"- Escala de Coma de Glasgow (GCS): {gcs}")

    # ── Clinical scores ────────────────────────────────────────────────
    if scores:
        lines.append("")
        lines.append("**Scores Clínicos:**")

        mews = scores.get("mews")
        if mews is not None:
            lines.append(f"- MEWS: {mews}")

        news2 = scores.get("news2")
        if news2 is not None:
            lines.append(f"- NEWS2: {news2}")

        sofa = scores.get("sofa")
        if sofa is not None:
            lines.append(f"- SOFA: {sofa}")

        qsofa = scores.get("qsofa")
        if qsofa is not None:
            lines.append(f"- qSOFA: {qsofa}")

    lines.append("")
    return "\n".join(lines)
