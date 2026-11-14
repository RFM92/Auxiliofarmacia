"""
Model: Payment
Histórico de pagamentos e assinaturas
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import uuid

from ..database import Base


class PaymentStatus(str, enum.Enum):
    """Status do pagamento"""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


class PaymentMethod(str, enum.Enum):
    """Métodos de pagamento"""
    STRIPE_CARD = "stripe_card"
    STRIPE_PIX = "stripe_pix"
    STRIPE_BOLETO = "stripe_boleto"
    ASAAS_PIX = "asaas_pix"
    ASAAS_BOLETO = "asaas_boleto"
    ASAAS_CARD = "asaas_card"
    MANUAL = "manual"  # admin manual
    PROMO = "promo"  # código promocional


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="payments")

    # Plan
    plan = Column(String(20), nullable=False)  # pro, premium, institutional
    value = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="BRL")

    # Status
    status = Column(String(20), nullable=False, default=PaymentStatus.PENDING, index=True)
    method = Column(String(30), nullable=False, index=True)

    # Gateway
    gateway = Column(String(20), nullable=True)  # stripe, asaas, manual
    gateway_id = Column(String(255), nullable=True, index=True)  # ID no gateway
    gateway_response = Column(JSON, default=dict)  # resposta completa

    # Coupon/Discount
    coupon_code = Column(String(50), nullable=True)
    discount = Column(Numeric(10, 2), default=0)

    # License gerada
    license_id = Column(String(36), ForeignKey("licenses.id"), nullable=True)
    license = relationship("License")

    # Datas
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # quando a licença expira

    # Refund
    refunded_at = Column(DateTime, nullable=True)
    refund_reason = Column(String(500), nullable=True)

    # Invoice
    invoice_url = Column(String(500), nullable=True)
    invoice_number = Column(String(50), nullable=True)

    # Metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    country = Column(String(3), nullable=True)

    def __repr__(self):
        return f"<Payment {self.id} {self.status} R${self.value}>"
