"""
Model: AuditLog
Registra todas as acoes sensiveis no sistema:
- Downloads de arquivos restritos
- Logins
- Ativacao de licencas
- Mudancas em usuarios/licencas
- Acoes admin
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, ForeignKey, JSON, Integer,
    Index, Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship

from .user import Base


class AuditAction(str, enum.Enum):
    """Tipos de acoes auditadas"""
    # Downloads
    DOWNLOAD_MANUAL = "download_manual"
    DOWNLOAD_FULL_ZIP = "download_full_zip"
    DOWNLOAD_PUBLIC_FILE = "download_public_file"

    # Auth
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    USER_LOGIN_FAILED = "user_login_failed"

    # Licencas
    LICENSE_ACTIVATED = "license_activated"
    LICENSE_REVOKED = "license_revoked"
    LICENSE_CREATED = "license_created"

    # Pagamentos
    PAYMENT_CREATED = "payment_created"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_REFUNDED = "payment_refunded"

    # Admin
    ADMIN_USER_BLACKLIST = "admin_user_blacklist"
    ADMIN_USER_ROLE_CHANGED = "admin_user_role_changed"
    ADMIN_SETTINGS_CHANGED = "admin_settings_changed"

    # Outros
    SECURITY_ALERT = "security_alert"
    API_KEY_CREATED = "api_key_created"
    DATA_EXPORT = "data_export"


class AuditSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Quem fez
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # Backup caso user deletado
    user = relationship("User", foreign_keys=[user_id])

    # O que fez
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    severity = Column(SQLEnum(AuditSeverity), default=AuditSeverity.LOW, index=True)
    resource = Column(String(500), nullable=True)  # arquivo, licenca, etc
    description = Column(Text, nullable=True)

    # Metadata extra (JSON)
    meta = Column(JSON, default=dict)

    # Info da requisicao
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 max 45 chars
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)

    # Quando
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email} at {self.created_at}>"


# Indices compostos para queries comuns
Index("idx_audit_user_action", AuditLog.user_id, AuditLog.action)
Index("idx_audit_created_action", AuditLog.created_at, AuditLog.action)
Index("idx_audit_severity_created", AuditLog.severity, AuditLog.created_at)