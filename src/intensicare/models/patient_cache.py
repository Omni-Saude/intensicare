"""Cache local de dados demográficos do paciente.

Campos PHI (display_name, mrn, birth_date, cpf, cns) são armazenados
como BYTEA criptografado via pgcrypto (pgp_sym_encrypt).
A chave de criptografia por tenant é injetada via GUC ``app.encryption_key``.

mrn_bidx é um blind-index (HMAC-SHA256) que permite busca por MRN
sem descriptografar o valor armazenado.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class PatientCache(Base):
    """Cache local de dados demográficos. Fonte primária: MPI da AMH."""

    __tablename__ = "patient_cache"

    mpi_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # ── PHI — encrypted at rest (BYTEA, pgp_sym_encrypt) ──────────────
    display_name: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    mrn: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    birth_date: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    cpf: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    cns: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # ── Blind index for MRN lookup without decryption ──────────────────
    mrn_bidx: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    # ── Non-PHI fields (plaintext) ─────────────────────────────────────
    gender: Mapped[str | None] = mapped_column(String(16))
    admission_dt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bed_id: Mapped[str | None] = mapped_column(String(32))
    unit: Mapped[str | None] = mapped_column(String(64))
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
