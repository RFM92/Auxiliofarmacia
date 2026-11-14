"""
Model: TelemetryEvent
Eventos de uso do dashboard para analytics
"""
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from ..database import Base


class EventType(str, enum.Enum):
    """Tipos de eventos"""
    PAGEVIEW = "pageview"
    CALCULATION = "calculation"
    MEDICATION_VIEW = "medication_view"
    CALCULATOR_USE = "calculator_use"
    PAID_FEATURE_VIEW = "paid_feature_view"
    LICENSE_ACTIVATED = "license_activated"
    LICENSE_VALIDATED = "license_validated"
    LICENSE_REJECTED = "license_rejected"
    LICENSE_EXPIRED = "license_expired"
    CONVERSION = "conversion"
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    PAYWALL_SHOWN = "paywall_shown"
    UPGRADE_CLICKED = "upgrade_clicked"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    FLASH_USED = "flashcard_used"
    TIMELINE_VIEW = "timeline_view"
    SEARCH = "search"
    PDF_EXPORTED = "pdf_exported"
    HISTORICAL_SAVED = "history_saved"


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Session
    session_id = Column(String(50), index=True, nullable=False)

    # User (opcional)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    user = relationship("User", back_populates="events")

    # Event
    event_type = Column(String(50), nullable=False, index=True)
    data = Column(JSON, default=dict)

    # Context
    path = Column(String(255), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    country = Column(String(3), nullable=True)
    city = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Event {self.event_type} @ {self.timestamp}>"
