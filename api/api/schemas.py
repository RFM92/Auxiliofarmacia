"""
Pydantic Schemas - Validação de entrada/saída
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


# ========== AUTH ==========
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=2, max_length=255)
    crm: Optional[str] = Field(None, max_length=50)
    specialty: Optional[str] = Field(None, max_length=100)
    institution: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)

    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ========== USER ==========
class UserBase(BaseModel):
    email: EmailStr
    name: str
    crm: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: str
    role: str
    is_active: bool
    is_verified: bool
    plan_expires_at: Optional[datetime]
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    crm: Optional[str] = None
    specialty: Optional[str] = None
    institution: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# ========== LICENSE ==========
class LicenseActivate(BaseModel):
    key: str = Field(..., description="Chave AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX")
    fingerprint: str = Field(..., description="Fingerprint do dispositivo")
    fingerprint_data: Optional[Dict[str, Any]] = None
    device_name: Optional[str] = Field(None, description="Ex: 'Chrome MacBook Pro'")

    @validator("key")
    def key_format(cls, v):
        v = v.upper().strip()
        if not re.match(r"^AUXFARMA-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$", v):
            raise ValueError("Formato inválido. Use AUXFARMA-XXXXX-XXXXX-XXXXX-XXXXX")
        return v


class LicenseValidate(BaseModel):
    key: str
    fingerprint: str


class LicenseResponse(BaseModel):
    key: str
    tier: str
    status: str
    issued_at: datetime
    activated_at: Optional[datetime]
    expires_at: datetime
    days_remaining: int
    devices_used: int
    max_devices: int
    features: List[str]
    user_email: str
    user_name: str

    class Config:
        from_attributes = True


class LicenseCreate(BaseModel):
    """Admin cria licença manualmente"""
    email: EmailStr
    tier: str = Field(..., pattern="^(pro|premium|institutional)$")
    duration_days: int = Field(30, ge=1, le=3650)
    max_devices: int = Field(2, ge=1, le=100)
    notes: Optional[str] = None
    campaign: Optional[str] = None


# ========== PAYMENT ==========
class PaymentCreate(BaseModel):
    plan: str = Field(..., pattern="^(pro|premium|institutional)$")
    method: str = Field(..., pattern="^(stripe_card|stripe_pix|stripe_boleto|asaas_pix|asaas_boleto|asaas_card)$")
    coupon: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    installments: int = Field(1, ge=1, le=12)


class PaymentResponse(BaseModel):
    id: str
    plan: str
    value: float
    status: str
    method: str
    created_at: datetime
    paid_at: Optional[datetime]
    invoice_url: Optional[str]

    class Config:
        from_attributes = True


# ========== TELEMETRY ==========
class TelemetryBatch(BaseModel):
    events: List[Dict[str, Any]]


class TelemetryEventIn(BaseModel):
    session_id: str
    event_type: str
    data: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
    referrer: Optional[str] = None
    timestamp: Optional[datetime] = None
    duration_ms: Optional[int] = None


# ========== ADMIN ==========
class AdminStats(BaseModel):
    total_users: int
    active_users_24h: int
    active_users_7d: int
    total_licenses: int
    active_licenses: int
    licenses_by_tier: Dict[str, int]
    total_revenue: float
    revenue_this_month: float
    conversions_7d: int
    churn_rate: float
    top_medications: List[Dict[str, Any]]
    top_calculators: List[Dict[str, Any]]


# Resolve forward references
TokenResponse.model_rebuild()
