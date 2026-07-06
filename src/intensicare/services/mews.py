"""
MEWS (Modified Early Warning Score) — engine de scoring determinístico e versionado.

Implementa o algoritmo MEWS conforme especificação clínica:
- heart_rate
- systolic_bp
- respiratory_rate
- temperature
- avpu

Cada componente retorna 0-3 pontos. Score total = soma dos componentes avaliáveis.
Componentes ausentes (None) contribuem com 0 pontos e são marcados como 'missing'.
"""

from __future__ import annotations

from typing import Any

MEWS_VERSION = "MEWS-v2.0.0"  # CLINICALLY RATIFIED per RAT-MEWS-SUBBE-2001 (AUDIT-001)

# ─────────────────────────────────────────────────────────────────────────────
# Published MEWS thresholds (Subbe et al., QJM 2001;94:521-526).
# Corrected bands per AUDIT-001 (RATIFIED per RAT-MEWS-SUBBE-2001).
# HR ≤40:2, 41-50:1, RR ≤8:2, Temp ≤35.0:2 — aligned to Subbe 2001 original.
# ─────────────────────────────────────────────────────────────────────────────

# Heart rate (bpm); inclusive upper bound of each band
MEWS_HR_BRADY_SEVERE_MAX = 40  # <= 40 -> 2
MEWS_HR_BRADY_MODERATE_MAX = 50  # <= 50 -> 1
MEWS_HR_NORMAL_MAX = 100  # <= 100 -> 0
MEWS_HR_TACHY_MILD_MAX = 110  # <= 110 -> 1
MEWS_HR_TACHY_MODERATE_MAX = 129  # <= 129 -> 2, else -> 3

# Systolic BP (mmHg); inclusive upper bound of each band
MEWS_SBP_HYPO_SEVERE_MAX = 70  # <= 70 -> 3
MEWS_SBP_HYPO_MODERATE_MAX = 80  # <= 80 -> 2
MEWS_SBP_HYPO_MILD_MAX = 100  # <= 100 -> 1
MEWS_SBP_NORMAL_MAX = 199  # <= 199 -> 0, else -> 2

# Respiratory rate (rpm); inclusive upper bound of each band
MEWS_RR_BRADY_SEVERE_MAX = 8  # <= 8 -> 2
MEWS_RR_NORMAL_MAX = 14  # <= 14 -> 0
MEWS_RR_TACHY_MILD_MAX = 20  # <= 20 -> 1
MEWS_RR_TACHY_MODERATE_MAX = 29  # <= 29 -> 2, else -> 3

# Temperature (°C); inclusive upper bound of each band
MEWS_TEMP_HYPOTHERMIA_MAX = 35.0  # <= 35.0 -> 2
MEWS_TEMP_LOW_MAX = 36.0  # <= 36.0 -> 1
MEWS_TEMP_NORMAL_MAX = 38.0  # <= 38.0 -> 0
MEWS_TEMP_MILD_FEVER_MAX = 38.5  # <= 38.5 -> 1, else -> 2

# Trend analysis requires at least this many consecutive scores
MEWS_TREND_MIN_SAMPLES = 2


def _score_heart_rate(value: int | None) -> dict[str, Any]:
    """MEWS sub-score para frequência cardíaca (bpm).

    ≤40   = 2 (bradicardia severa)
    41-50 = 1 (bradicardia moderada)
    51-100 = 0 (normal)
    101-110 = 1 (taquicardia leve)
    111-129 = 2 (taquicardia moderada)
    ≥130  = 3 (taquicardia severa)
    """
    if value is None:
        return {"heart_rate": 0, "heart_rate_status": "missing"}
    if value <= MEWS_HR_BRADY_SEVERE_MAX:
        pts = 2
    elif value <= MEWS_HR_BRADY_MODERATE_MAX:
        pts = 1
    elif value <= MEWS_HR_NORMAL_MAX:
        pts = 0
    elif value <= MEWS_HR_TACHY_MILD_MAX:
        pts = 1
    elif value <= MEWS_HR_TACHY_MODERATE_MAX:
        pts = 2
    else:
        pts = 3
    return {"heart_rate": pts}


def _score_systolic_bp(value: int | None) -> dict[str, Any]:
    """MEWS sub-score para pressão sistólica (mmHg).

    ≤70   = 3 (hipotensão severa)
    71-80 = 2 (hipotensão moderada)
    81-100 = 1 (hipotensão leve)
    101-199 = 0 (normal)
    ≥200  = 2 (hipertensão severa)
    """
    if value is None:
        return {"systolic_bp": 0, "systolic_bp_status": "missing"}
    if value <= MEWS_SBP_HYPO_SEVERE_MAX:
        pts = 3
    elif value <= MEWS_SBP_HYPO_MODERATE_MAX:
        pts = 2
    elif value <= MEWS_SBP_HYPO_MILD_MAX:
        pts = 1
    elif value <= MEWS_SBP_NORMAL_MAX:
        pts = 0
    else:
        pts = 2
    return {"systolic_bp": pts}


def _score_respiratory_rate(value: int | None) -> dict[str, Any]:
    """MEWS sub-score para frequência respiratória (rpm).

    ≤8    = 2 (bradipneia severa)
    9-14  = 0 (normal)
    15-20 = 1 (taquipneia leve)
    21-29 = 2 (taquipneia moderada)
    ≥30   = 3 (taquipneia severa)
    """
    if value is None:
        return {"respiratory_rate": 0, "respiratory_rate_status": "missing"}
    if value <= MEWS_RR_BRADY_SEVERE_MAX:
        pts = 2
    elif value <= MEWS_RR_NORMAL_MAX:
        pts = 0
    elif value <= MEWS_RR_TACHY_MILD_MAX:
        pts = 1
    elif value <= MEWS_RR_TACHY_MODERATE_MAX:
        pts = 2
    else:
        pts = 3
    return {"respiratory_rate": pts}


def _score_temperature(value: float | None) -> dict[str, Any]:
    """MEWS sub-score para temperatura (°C).

    ≤35.0      = 2 (hipotermia)
    35.1-36.0  = 1 (temperatura baixa)
    36.1-38.0  = 0 (normal)
    38.1-38.5  = 1 (febre leve)
    ≥38.6      = 2 (febre)
    """
    if value is None:
        return {"temperature": 0, "temperature_status": "missing"}
    if value <= MEWS_TEMP_HYPOTHERMIA_MAX:
        pts = 2
    elif value <= MEWS_TEMP_LOW_MAX:
        pts = 1
    elif value <= MEWS_TEMP_NORMAL_MAX:
        pts = 0
    elif value <= MEWS_TEMP_MILD_FEVER_MAX:
        pts = 1
    else:
        pts = 2
    return {"temperature": pts}


def _score_avpu(value: str | None) -> dict[str, Any]:
    """MEWS sub-score para nível de consciência (AVPU).

    Alert        = 0
    Voice        = 1
    Pain         = 2
    Unresponsive = 3
    """
    if value is None:
        return {"avpu": 0, "avpu_status": "missing"}

    avpu_map: dict[str, int] = {"A": 0, "V": 1, "P": 2, "U": 3}
    upper = value.upper().strip()
    pts = avpu_map.get(upper, 0)
    return {"avpu": pts}


def calculate_mews(
    heart_rate: int | None = None,
    systolic_bp: int | None = None,
    respiratory_rate: int | None = None,
    temperature: float | None = None,
    avpu: str | None = None,
) -> tuple[int, dict[str, Any]]:
    """Calcula o MEWS (Modified Early Warning Score).

    Função determinística e pura: mesmos inputs sempre produzem mesmos outputs.
    Cada parâmetro é um componente do score; ausentes contribuem com 0.

    Args:
        heart_rate: Frequência cardíaca em bpm.
        systolic_bp: Pressão sistólica em mmHg.
        respiratory_rate: Frequência respiratória em rpm.
        temperature: Temperatura em °C.
        avpu: Nível de consciência (A/V/P/U).

    Returns:
        Tuple de (score_total, components_dict) onde:
        - score_total: int com a soma dos sub-scores (0-15).
        - components_dict: dict com sub-scores individuais e status.
          Inclui 'algorithm_version' = 'MEWS-v2.0.0' e 'missing_components' se houver.
    """
    components: dict[str, Any] = {"algorithm_version": MEWS_VERSION}

    hr = _score_heart_rate(heart_rate)
    sbp = _score_systolic_bp(systolic_bp)
    rr = _score_respiratory_rate(respiratory_rate)
    temp = _score_temperature(temperature)
    avpu_score = _score_avpu(avpu)

    components.update(hr)
    components.update(sbp)
    components.update(rr)
    components.update(temp)
    components.update(avpu_score)

    # Identifica componentes ausentes
    missing = [k.replace("_status", "") for k, v in components.items() if k.endswith("_status")]
    if missing:
        components["missing_components"] = missing

    # Remove chaves de status do dicionário final de componentes de score
    status_keys = [k for k in components if k.endswith("_status")]
    for k in status_keys:
        del components[k]

    # Soma apenas os sub-scores numéricos
    score_total = int(
        components.get("heart_rate", 0)
        + components.get("systolic_bp", 0)
        + components.get("respiratory_rate", 0)
        + components.get("temperature", 0)
        + components.get("avpu", 0)
    )

    return score_total, components


def compute_trend(scores: list[int]) -> str | None:
    """Determina a tendência a partir de uma lista de scores consecutivos.

    Compara o último score com o primeiro da lista.

    Args:
        scores: Lista de valores de score em ordem cronológica (mais antigo primeiro).

    Returns:
        'increasing', 'decreasing', 'stable', ou None se lista tiver < 2 elementos.
    """
    if len(scores) < MEWS_TREND_MIN_SAMPLES:
        return None
    first, last = scores[0], scores[-1]
    if last > first:
        return "increasing"
    if last < first:
        return "decreasing"
    return "stable"
