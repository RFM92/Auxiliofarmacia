"""
Model: License
Chaves de licença e seus dispositivos autorizados
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from ..database import Base


class LicenseTier(str, enum.Enum):
    """Tiers de licença"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"


class LicenseStatus(str, enum.Enum):
    """Status da licença"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING = "pending"


class License(Base):
    __tablename__ = "licenses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Key (AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX)
    key = Column(String(50), unique=True, index=True, nullable=False)

    # Owner
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="licenses")

    # Plan
    tier = Column(String(20), nullable=False, default=LicenseTier.PRO, index=True)
    status = Column(String(20), nullable=False, default=LicenseStatus.ACTIVE, index=True)

    # Datas
    issued_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_validated_at = Column(DateTime, nullable=True)

    # Limits
    max_devices = Column(Integer, default=2)  # conforme tier
    devices_used = Column(Integer, default=0)

    # Metadata
    notes = Column(String(500), nullable=True)  # notas internas do admin
    source = Column(String(50), default="manual")  # manual, stripe, asaas, promo
    campaign = Column(String(100), nullable=True)  # ex: "BLACK_FRIDAY_2025"

    # Anti-pirataria
    fingerprints = Column(JSON, default=list)  # lista de fingerprints autorizados
    ip_whitelist = Column(JSON, default=list)  # opcional
    max_activations = Column(Integer, default=1)  # vezes que pode ser ativada
    activation_count = Column(Integer, default=0)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    revoked_reason = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<License {self.key} ({self.tier})>"

    @property
    def is_active(self) -> bool:
        return (
            self.status == LicenseStatus.ACTIVE
            and self.expires_at > datetime.utcnow()
            and self.activation_count < self.max_activations
        )

    @property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()

    @property
    def days_remaining(self) -> int:
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)

    def can_add_fingerprint(self, fingerprint: str) -> bool:
        """Verifica se pode adicionar novo fingerprint"""
        if fingerprint in (self.fingerprints or []):
            return True
        return len(self.fingerprints or []) < self.max_devices
