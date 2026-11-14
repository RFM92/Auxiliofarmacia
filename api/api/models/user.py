"""
Model: User
Usuários do sistema (pediatras, residentes, administradores)
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from ..database import Base


class UserRole(str, enum.Enum):
    """Roles de usuário"""
    USER = "user"
    PRO = "pro"
    PREMIUM = "premium"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Auth
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Profile
    name = Column(String(255), nullable=False)
    crm = Column(String(50), nullable=True)  # CRM
    specialty = Column(String(100), nullable=True)  # Pediatria, Neonatologia, etc
    institution = Column(String(255), nullable=True)  # Hospital/Clínica
    phone = Column(String(20), nullable=True)

    # Plan
    role = Column(SQLEnum(UserRole), default=UserRole.USER, index=True)
    plan_expires_at = Column(DateTime, nullable=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)

    # Anti-fraud
    is_blacklisted = Column(Boolean, default=False)
    blacklist_reason = Column(String(500), nullable=True)
    fraud_score = Column(Integer, default=0)  # 0-100

    # Email verification
    verification_token = Column(String(100), nullable=True)
    reset_token = Column(String(100), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    # Relations
    licenses = relationship("License", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    events = relationship("TelemetryEvent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        return self.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)

    @property
    def is_premium(self) -> bool:
        return self.role in (UserRole.PRO, UserRole.PREMIUM, UserRole.SUPER_ADMIN)
