"""Normalizador de unidades canônicas no edge (WO-009 — units registry).

Aplica as regras do registry.yaml para converter qualquer unidade de entrada
para a unidade canônica mandatada. Opera EXCLUSIVAMENTE na borda de ingestão
(edge); nunca no boundary de computação.

Regra fundamental:
- ``canonical_unit``: a unidade em que TODOS os cálculos e thresholds operam.
- ``aliases``: sinônimos com fator 1.0 (ex: "mmHg" ↔ "mmhg").
- ``edge_conversions``: conversões com fator NUMÉRICO (ex: kPa → mmHg × 7.50062).
- Fator ``null``: conversão NÃO é um fator fixo (ex: degF → degC é affine,
  mL/h → mcg/kg/min precisa de peso + concentração). Estas requerem serviço
  externo e NÃO são resolvidas aqui — são rejeitadas com erro.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Carregamento do registry
# ---------------------------------------------------------------------------

_REGISTRY_PATH = Path(__file__).parents[3] / "docs" / "plan" / "_work" / "units" / "registry.yaml"

# Cache do registry carregado
_registry: dict[str, Any] | None = None
_params_by_name: dict[str, dict[str, Any]] = {}


def _load_registry() -> None:
    """Carrega o registry.yaml uma única vez (lazy)."""
    global _registry, _params_by_name  # noqa: PLW0603
    if _registry is not None:
        return

    if not _REGISTRY_PATH.exists():
        logger.warning("Units registry não encontrado em %s — normalização desabilitada", _REGISTRY_PATH)
        _registry = {"version": 0, "parameters": []}
        return

    with open(_REGISTRY_PATH, encoding="utf-8") as f:
        _registry = yaml.safe_load(f)

    if _registry is None:
        _registry = {"version": 0, "parameters": []}
        return

    # Indexa por nome de parâmetro (snake_case canônico)
    _params_by_name = {}
    for param in _registry.get("parameters", []):
        name = param.get("parameter", "")
        if name:
            _params_by_name[name] = param

    logger.info("Units registry v%s carregado: %d parâmetros",
                _registry.get("version", "?"), len(_params_by_name))


def _find_param(parameter: str) -> dict[str, Any] | None:
    """Encontra a definição de um parâmetro no registry."""
    _load_registry()
    return _params_by_name.get(parameter)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


class UnitNormalizationError(Exception):
    """Erro ao normalizar unidade — unidade desconhecida ou conversão não suportada."""


def normalize_value(
    parameter: str,
    value: float,
    from_unit: str,
) -> float:
    """Normaliza um valor da unidade de entrada para a unidade canônica.

    Args:
        parameter: Nome canônico do parâmetro (ex: ``"fio2"``, ``"lactato_arterial"``).
        value: Valor numérico na unidade de entrada.
        from_unit: Unidade de entrada (ex: ``"percent"``, ``"kPa"``).

    Returns:
        Valor convertido para a unidade canônica.

    Raises:
        UnitNormalizationError: Se a unidade for desconhecida ou exigir
            conversão não suportada (fator ``null``).

    Exemplos:
        >>> normalize_value("fio2", 40, "percent")
        0.4
        >>> normalize_value("lactato_arterial", 27, "mg/dL")
        2.997
        >>> normalize_value("creatinina", 88.4, "umol/L")
        1.0
    """
    param_def = _find_param(parameter)
    if param_def is None:
        raise UnitNormalizationError(
            f"Parâmetro desconhecido: '{parameter}'. "
            f"Verifique o registry em {_REGISTRY_PATH}"
        )

    canonical_unit = param_def.get("canonical_unit", "")

    # Caso 1: já está na unidade canônica (case-insensitive)
    if from_unit.lower() == canonical_unit.lower():
        return value

    # Caso 2: é um alias (sinônimo 1:1, case-insensitive)
    aliases: list[str] = param_def.get("aliases", [])
    if from_unit.lower() in (a.lower() for a in aliases):
        return value

    # Caso 3: conversão numérica definida no registry
    edge_conversions: list[dict[str, Any]] = param_def.get("edge_conversions", [])
    for conv in edge_conversions:
        if from_unit.lower() == conv["from"].lower():
            factor = conv.get("factor")
            if factor is None:
                raise UnitNormalizationError(
                    f"Conversão '{from_unit}' → '{canonical_unit}' para "
                    f"'{parameter}' NÃO é um fator fixo (factor=null). "
                    f"Nota: {conv.get('note', 'sem detalhes')}"
                )
            return value * factor

    # Caso 4: unidade não reconhecida
    raise UnitNormalizationError(
        f"Unidade '{from_unit}' não reconhecida para '{parameter}'. "
        f"Canônica: '{canonical_unit}'. Aliases: {aliases}. "
        f"Conversões disponíveis: {[c['from'] for c in edge_conversions]}"
    )


def get_canonical_unit(parameter: str) -> str | None:
    """Retorna a unidade canônica para um parâmetro.

    Args:
        parameter: Nome canônico do parâmetro.

    Returns:
        Unidade canônica (string), ou None se o parâmetro não existir.
    """
    param_def = _find_param(parameter)
    if param_def is None:
        return None
    return param_def.get("canonical_unit", "")


def list_parameters() -> list[str]:
    """Retorna a lista de todos os parâmetros conhecidos no registry."""
    _load_registry()
    return sorted(_params_by_name.keys())


def get_parameter_info(parameter: str) -> dict[str, Any] | None:
    """Retorna a definição completa de um parâmetro do registry."""
    return _find_param(parameter)
