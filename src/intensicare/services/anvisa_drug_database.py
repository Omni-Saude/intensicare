"""ANVISA Drug Database Integration Stub.

Provides a local, swappable drug database that can be replaced with the
real ANVISA (Agência Nacional de Vigilância Sanitária) API when available.

This module serves as a facade: the ``ANVISADrugDatabase`` class offers the
same interface whether backed by the local knowledge base or a remote API.

Integration points:
    - ``anvisa_drug_database.py`` (this file):
      Replace ``LocalDrugDatabase`` with ``ANVISADrugAPIClient`` when the
      ANVISA API key and endpoint are provisioned.

    - ``drug_interactions.py``:
      Import from this module instead of using hardcoded ``DRUG_INTERACTIONS``
      dict for drug lookups. See the ``_check_interactions_via_anvisa``
      function in that file.

    - ``domain_prescricao.py``:
      The ``_check_interactions`` function delegates to either the local
      knowledge base or the ANVISA-backed checker depending on configuration.

Architecture::

    ┌──────────────────────────────────────────┐
    │         domain_prescricao.py             │
    │  _check_interactions(db_session)         │
    │      │                                   │
    │      ├── ANVISA_ENABLED=False            │
    │      │   └── drug_interactions.py        │
    │      │       └── DRUG_INTERACTIONS dict  │
    │      │                                   │
    │      └── ANVISA_ENABLED=True             │
    │          └── anvisa_drug_database.py     │
    │              └── ANVISADrugAPIClient     │
    │                  └── HTTPS → api.anvisa.gov.br │
    └──────────────────────────────────────────┘

References:
    - ANVISA API documentation: https://consultas.anvisa.gov.br/
    - Bulário Eletrônico: https://consultas.anvisa.gov.br/#/bulario/
    - Future endpoint (speculative): POST https://api.anvisa.gov.br/v2/interactions/check
"""

from __future__ import annotations

from dataclasses import dataclass, field

# =============================================================================
# Configuration
# =============================================================================

# Toggle to switch between local stub and real ANVISA API.
# Set to True when ANVISA_API_KEY and ANVISA_API_BASE_URL are provisioned.
ANVISA_ENABLED: bool = False
ANVISA_API_KEY: str | None = None  # Provision via environment: ANVISA_API_KEY
ANVISA_API_BASE_URL: str = "https://api.anvisa.gov.br/v2"


# =============================================================================
# Data structures
# =============================================================================


@dataclass
class ANVISADrugInfo:
    """Drug information as returned by ANVISA Bulário Eletrônico.

    Mirrors the expected response from ANVISA's drug registry API.
    """

    registro_anvisa: str  # e.g. "1.0047.0123.001-1"
    principio_ativo: str  # Active ingredient (DCB name)
    nome_comercial: str  # Brand name
    apresentacao: str  # Dosage form (e.g. "Pó para solução injetável 500mg")
    classe_terapeutica: str  # Therapeutic class
    via_administracao: list[str] = field(default_factory=list)
    categoria_risco_gestacao: str = ""  # Pregnancy risk category (A, B, C, D, X)
    necessita_receita: bool = True  # Prescription required
    tarja: str = ""  # "preta", "vermelha", or ""
    data_vencimento_registro: str = ""  # Registration expiry date
    fabricante: str = ""


@dataclass
class ANVISAInteractionResult:
    """Drug interaction result from ANVISA DDI service.

    Expected response from POST /v2/interactions/check.
    """

    drug_a: str
    drug_b: str
    severity: str  # "contraindicated", "severe", "moderate", "minor"
    description: str
    mechanism: str | None = None
    recommendation: str | None = None
    references: list[str] = field(default_factory=list)


# =============================================================================
# Abstract interface
# =============================================================================


class AbstractDrugDatabase:
    """Interface for drug database lookups — swappable backend.

    Implementations:
        - ``LocalDrugDatabase``: In-memory stub for development/testing.
        - ``ANVISADrugAPIClient``: Real HTTPS client for ANVISA API (future).
    """

    async def lookup_drug(self, drug_name: str) -> ANVISADrugInfo | None:
        """Look up a drug by name (princípio ativo or nome comercial)."""
        raise NotImplementedError

    async def check_interaction(self, drug_a: str, drug_b: str) -> ANVISAInteractionResult | None:
        """Check for interaction between two drugs."""
        raise NotImplementedError

    async def check_interactions_bulk(self, drugs: list[str]) -> list[ANVISAInteractionResult]:
        """Check all pairwise interactions in a drug list."""
        raise NotImplementedError

    async def is_available(self) -> bool:
        """Return True if the database backend is reachable."""
        raise NotImplementedError


# =============================================================================
# Local stub implementation
# =============================================================================


class LocalDrugDatabase(AbstractDrugDatabase):
    """In-memory drug database stub for development and testing.

    Uses the same knowledge base as ``drug_interactions.py`` but exposes
    the ``AbstractDrugDatabase`` interface so callers can swap backends
    without changing their code.

    When ANVISA API credentials are provisioned, replace this with
    ``ANVISADrugAPIClient``:
        db = ANVISADrugAPIClient(api_key=..., base_url=...)
    """

    def __init__(self) -> None:
        # Local registry mirrors ANVISA Bulário Eletrônico subset
        self._drugs: dict[str, ANVISADrugInfo] = {
            "meropenem": ANVISADrugInfo(
                registro_anvisa="1.0047.0123.001-1",
                principio_ativo="meropeném",
                nome_comercial="Meronem",
                apresentacao="Pó para solução injetável 500 mg",
                classe_terapeutica="Antibacteriano carbapenêmico",
                via_administracao=["IV"],
                categoria_risco_gestacao="B",
                necessita_receita=True,
                tarja="vermelha",
                fabricante="AstraZeneca",
            ),
            "vancomicina": ANVISADrugInfo(
                registro_anvisa="1.0180.0045.002-8",
                principio_ativo="cloridrato de vancomicina",
                nome_comercial="Vancocina",
                apresentacao="Pó para solução injetável 500 mg",
                classe_terapeutica="Antibacteriano glicopeptídeo",
                via_administracao=["IV"],
                categoria_risco_gestacao="C",
                necessita_receita=True,
                tarja="vermelha",
                fabricante="Blau Farmacêutica",
            ),
            "midazolam": ANVISADrugInfo(
                registro_anvisa="1.0047.0124.002-9",
                principio_ativo="midazolam",
                nome_comercial="Dormonid",
                apresentacao="Solução injetável 5 mg/mL",
                classe_terapeutica="Benzodiazepínico",
                via_administracao=["IV", "IM", "PO"],
                categoria_risco_gestacao="D",
                necessita_receita=True,
                tarja="preta",
                fabricante="Roche",
            ),
            "fentanil": ANVISADrugInfo(
                registro_anvisa="1.7057.0032.001-5",
                principio_ativo="citrato de fentanila",
                nome_comercial="Fentanil",
                apresentacao="Solução injetável 0,05 mg/mL",
                classe_terapeutica="Analgésico opioide",
                via_administracao=["IV"],
                categoria_risco_gestacao="C",
                necessita_receita=True,
                tarja="preta",
                fabricante="Cristália",
            ),
            "noradrenalina": ANVISADrugInfo(
                registro_anvisa="1.0047.0125.003-7",
                principio_ativo="hemitartarato de norepinefrina",
                nome_comercial="Noradrenalina",
                apresentacao="Solução injetável 1 mg/mL",
                classe_terapeutica="Catecolamina vasopressora",
                via_administracao=["IV"],
                categoria_risco_gestacao="C",
                necessita_receita=True,
                tarja="vermelha",
                fabricante="Hipolabor",
            ),
            "insulina_regular": ANVISADrugInfo(
                registro_anvisa="1.0047.0126.004-5",
                principio_ativo="insulina humana regular",
                nome_comercial="Novolin R",
                apresentacao="Solução injetável 100 UI/mL",
                classe_terapeutica="Hormônio hipoglicemiante",
                via_administracao=["IV", "SC"],
                categoria_risco_gestacao="B",
                necessita_receita=True,
                tarja="",
                fabricante="Novo Nordisk",
            ),
            "propofol": ANVISADrugInfo(
                registro_anvisa="1.0047.0127.005-3",
                principio_ativo="propofol",
                nome_comercial="Diprivan",
                apresentacao="Emulsão injetável 10 mg/mL",
                classe_terapeutica="Anestésico geral",
                via_administracao=["IV"],
                categoria_risco_gestacao="B",
                necessita_receita=True,
                tarja="preta",
                fabricante="Aspen Pharma",
            ),
            "amiodarona": ANVISADrugInfo(
                registro_anvisa="1.0047.0128.006-1",
                principio_ativo="cloridrato de amiodarona",
                nome_comercial="Ancoron",
                apresentacao="Solução injetável 50 mg/mL",
                classe_terapeutica="Antiarritmico classe III",
                via_administracao=["IV", "PO"],
                categoria_risco_gestacao="D",
                necessita_receita=True,
                tarja="vermelha",
                fabricante="Libbs",
            ),
            "morfina": ANVISADrugInfo(
                registro_anvisa="1.0047.0129.007-9",
                principio_ativo="sulfato de morfina",
                nome_comercial="Dimorf",
                apresentacao="Solução injetável 1 mg/mL",
                classe_terapeutica="Analgésico opioide",
                via_administracao=["IV", "SC", "PO"],
                categoria_risco_gestacao="C",
                necessita_receita=True,
                tarja="preta",
                fabricante="Cristália",
            ),
            "heparina_nao_fracionada": ANVISADrugInfo(
                registro_anvisa="1.0047.0130.008-7",
                principio_ativo="heparina sódica",
                nome_comercial="Heparina",
                apresentacao="Solução injetável 5.000 UI/mL",
                classe_terapeutica="Anticoagulante",
                via_administracao=["IV", "SC"],
                categoria_risco_gestacao="C",
                necessita_receita=True,
                tarja="vermelha",
                fabricante="Blau",
            ),
        }

        # This mirrors DRUG_INTERACTIONS from drug_interactions.py
        # but structured as ANVISAInteractionResult objects
        self._interactions: list[ANVISAInteractionResult] = []

    async def lookup_drug(self, drug_name: str) -> ANVISADrugInfo | None:
        """Look up by principio_ativo (normalized key)."""
        key = drug_name.lower().replace(" ", "_")
        return self._drugs.get(key)

    async def check_interaction(self, drug_a: str, drug_b: str) -> ANVISAInteractionResult | None:
        """Check pairwise interaction using local knowledge base.

        In production, this would call:
            POST {ANVISA_API_BASE_URL}/interactions/check
            Headers: Authorization: Bearer {ANVISA_API_KEY}
            Body: {"drug_a": drug_a, "drug_b": drug_b}
        """
        # Delegate to the existing local interaction checker
        # (see drug_interactions.py DRUG_INTERACTIONS dict)
        from intensicare.services.drug_interactions import DRUG_INTERACTIONS

        key_a = drug_a.lower().replace(" ", "_")
        key_b = drug_b.lower().replace(" ", "_")

        pair = (key_a, key_b)
        if pair in DRUG_INTERACTIONS:
            severity, _itype, desc = DRUG_INTERACTIONS[pair]
            return ANVISAInteractionResult(
                drug_a=drug_a,
                drug_b=drug_b,
                severity=severity,
                description=desc,
                mechanism=None,
                recommendation=None,
            )
        return None

    async def check_interactions_bulk(self, drugs: list[str]) -> list[ANVISAInteractionResult]:
        """Check all pairwise interactions in a drug list.

        In production, this would call:
            POST {ANVISA_API_BASE_URL}/interactions/check-bulk
            Headers: Authorization: Bearer {ANVISA_API_KEY}
            Body: {"drugs": drugs}
        """
        results: list[ANVISAInteractionResult] = []
        for i, drug_a in enumerate(drugs):
            for drug_b in drugs[i + 1 :]:
                result = await self.check_interaction(drug_a, drug_b)
                if result:
                    results.append(result)
        return results

    async def is_available(self) -> bool:
        """Local database is always available."""
        return True


# =============================================================================
# Future: ANVISA API Client (to be implemented when API credentials available)
# =============================================================================


class ANVISADrugAPIClient(AbstractDrugDatabase):
    """Real ANVISA API client — NOT YET IMPLEMENTED.

    This is a placeholder. To activate, provision:
        - ANVISA_API_KEY environment variable
        - ANVISA_API_BASE_URL (default: https://api.anvisa.gov.br/v2)

    Then replace ``LocalDrugDatabase`` with this class::

        from intensicare.services.anvisa_drug_database import ANVISADrugAPIClient

        anvisa_db = ANVISADrugAPIClient(
            api_key=os.environ["ANVISA_API_KEY"],
            base_url="https://api.anvisa.gov.br/v2",
        )

    API endpoints (speculative — to be confirmed with ANVISA):
        GET  /v2/drugs/{registro_anvisa}       → ANVISADrugInfo
        GET  /v2/drugs?q={principio_ativo}     → list[ANVISADrugInfo]
        POST /v2/interactions/check             → ANVISAInteractionResult
        POST /v2/interactions/check-bulk        → list[ANVISAInteractionResult]
        POST /v2/allergies/check               → allergy cross-reactivity
    """

    def __init__(self, api_key: str, base_url: str = ANVISA_API_BASE_URL) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        # In production, use httpx.AsyncClient or aiohttp.ClientSession:
        # self._client = httpx.AsyncClient(
        #     base_url=self.base_url,
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     timeout=30.0,
        # )

    async def lookup_drug(self, drug_name: str) -> ANVISADrugInfo | None:
        """Look up drug via ANVISA API.

        Production implementation::

            response = await self._client.get("/drugs", params={"q": drug_name})
            response.raise_for_status()
            data = response.json()
            if data["results"]:
                return ANVISADrugInfo(**data["results"][0])
            return None
        """
        raise NotImplementedError(
            "ANVISA API client not yet implemented. "
            "Set ANVISA_API_KEY and ANVISA_API_BASE_URL to activate."
        )

    async def check_interaction(self, drug_a: str, drug_b: str) -> ANVISAInteractionResult | None:
        """Check pairwise interaction via ANVISA API.

        Production implementation::

            response = await self._client.post(
                "/interactions/check",
                json={"drug_a": drug_a, "drug_b": drug_b},
            )
            response.raise_for_status()
            data = response.json()
            return ANVISAInteractionResult(**data)
        """
        raise NotImplementedError("ANVISA API client not yet implemented.")

    async def check_interactions_bulk(self, drugs: list[str]) -> list[ANVISAInteractionResult]:
        """Check all pairwise interactions via ANVISA API.

        Production implementation::

            response = await self._client.post(
                "/interactions/check-bulk",
                json={"drugs": drugs},
            )
            response.raise_for_status()
            return [ANVISAInteractionResult(**r) for r in response.json()["interactions"]]
        """
        raise NotImplementedError("ANVISA API client not yet implemented.")

    async def is_available(self) -> bool:
        """Check if ANVISA API is reachable.

        Production implementation::

            try:
                response = await self._client.get("/health")
                return response.status_code == 200
            except Exception:
                return False
        """
        return False  # Not yet implemented


# =============================================================================
# Factory — returns the appropriate backend based on configuration
# =============================================================================

_anvisa_database: AbstractDrugDatabase | None = None


def get_anvisa_database() -> AbstractDrugDatabase:
    """Return the configured ANVISA drug database backend.

    Uses ``LocalDrugDatabase`` (in-memory stub) by default.
    Switches to ``ANVISADrugAPIClient`` when ``ANVISA_ENABLED=True`` and
    ``ANVISA_API_KEY`` is provisioned.
    """
    global _anvisa_database

    if _anvisa_database is None:
        if ANVISA_ENABLED and ANVISA_API_KEY:
            _anvisa_database = ANVISADrugAPIClient(
                api_key=ANVISA_API_KEY,
                base_url=ANVISA_API_BASE_URL,
            )
        else:
            _anvisa_database = LocalDrugDatabase()

    return _anvisa_database
