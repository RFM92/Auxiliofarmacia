"""
LicenseService - Lógica de negócio de licenciamento
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging
import hashlib

from ..models import User, License, LicenseTier, LicenseStatus, UserRole
from ..utils.security import (
    generate_license_key,
    validate_license_key_format,
    mask_license_key,
)
from ..config import settings

logger = logging.getLogger(__name__)


# Features por tier
TIER_FEATURES = {
    LicenseTier.FREE.value: [
        "basic_calculators",
        "search",
        "glossary",
        "basic_medications",
    ],
    LicenseTier.PRO.value: [
        "basic_calculators",
        "advanced_calculators",
        "search",
        "glossary",
        "basic_medications",
        "complete_medications",
        "history_limited_50",
        "pdf_export",
        "comparison",
        "visual_learning",
    ],
    LicenseTier.PREMIUM.value: [
        "basic_calculators",
        "advanced_calculators",
        "search",
        "glossary",
        "basic_medications",
        "complete_medications",
        "international_bulas",
        "history_unlimited",
        "pdf_export",
        "comparison",
        "visual_learning",
        "all_visual",
        "priority_support",
    ],
    LicenseTier.INSTITUTIONAL.value: [
        "basic_calculators",
        "advanced_calculators",
        "search",
        "glossary",
        "basic_medications",
        "complete_medications",
        "international_bulas",
        "history_unlimited",
        "pdf_export",
        "comparison",
        "visual_learning",
        "all_visual",
        "multi_user",
        "admin_panel",
        "dedicated_support",
    ],
}


# Limites por tier
TIER_LIMITS = {
    LicenseTier.FREE.value: {
        "max_devices": 1,
        "history_limit": 0,
        "advanced_calculators": 0,
    },
    LicenseTier.PRO.value: {
        "max_devices": 2,
        "history_limit": 50,
        "advanced_calculators": 9,
    },
    LicenseTier.PREMIUM.value: {
        "max_devices": 3,
        "history_limit": -1,  # ilimitado
        "advanced_calculators": 9,
    },
    LicenseTier.INSTITUTIONAL.value: {
        "max_devices": 50,
        "history_limit": -1,
        "advanced_calculators": 9,
    },
}


class LicenseService:
    """Serviço de licenciamento"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== GERAÇÃO ==========
    async def create_license(
        self,
        user: User,
        tier: str,
        duration_days: int = 30,
        max_devices: int = None,
        source: str = "manual",
        notes: str = None,
        campaign: str = None,
    ) -> License:
        """Cria nova licença para o usuário"""
        if tier not in [t.value for t in LicenseTier]:
            raise ValueError(f"Tier inválido: {tier}")

        # tier já é string, não precisa de .value
        max_devices = max_devices or TIER_LIMITS[tier]["max_devices"]

        license = License(
            key=generate_license_key(),
            user_id=user.id,
            tier=tier,
            status=LicenseStatus.ACTIVE,
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=duration_days),
            max_devices=max_devices,
            source=source,
            notes=notes,
            campaign=campaign,
            max_activations=max_devices,  # pode ser ativada N vezes
            fingerprints=[],
        )

        self.db.add(license)

        # Atualiza role do usuário
        if tier == "pro":
            user.role = UserRole.PRO
        elif tier == "premium":
            user.role = UserRole.PREMIUM
        elif tier == "institutional":
            user.role = UserRole.PREMIUM  # tier especial
        user.plan_expires_at = license.expires_at

        await self.db.commit()
        await self.db.refresh(license)

        logger.info(f"✅ License {mask_license_key(license.key)} criada para {user.email}")
        return license

    # ========== VALIDAÇÃO ==========
    async def validate_license(
        self,
        key: str,
        fingerprint: str = None,
    ) -> Dict:
        """
        Valida chave de licença

        Returns:
            dict com:
                valid: bool
                reason: str (se inválida)
                license: License (se válida)
                features: list
        """
        # 1. Validar formato
        if not validate_license_key_format(key):
            return {"valid": False, "reason": "invalid_format"}

        key = key.upper().strip()

        # 2. Chave demo?
        if key in settings.LICENSE_DEMO_KEYS:
            tier = self._demo_key_to_tier(key)
            return {
                "valid": True,
                "license": {
                    "key": key,
                    "tier": tier,
                    "status": "active",
                    "is_demo": True,
                },
                "features": TIER_FEATURES[tier],
                "demo": True,
            }

        # 3. Buscar no banco
        result = await self.db.execute(
            select(License).where(License.key == key)
        )
        license = result.scalar_one_or_none()

        if not license:
            return {"valid": False, "reason": "not_found"}

        # 4. Verificar status
        if license.status == LicenseStatus.REVOKED:
            return {"valid": False, "reason": "revoked"}

        if license.status == LicenseStatus.SUSPENDED:
            return {"valid": False, "reason": "suspended"}

        if license.is_expired:
            # Marca como expirada se ainda estiver ativa
            if license.status == LicenseStatus.ACTIVE:
                license.status = LicenseStatus.EXPIRED
                await self.db.commit()
            return {"valid": False, "reason": "expired"}

        # 5. Atualizar last_validated_at
        license.last_validated_at = datetime.utcnow()
        await self.db.commit()

        return {
            "valid": True,
            "license": {
                "key": license.key,
                "tier": license.tier,
                "status": str(license.status),
                "expires_at": license.expires_at.isoformat(),
                "days_remaining": license.days_remaining,
                "user_email": license.user.email,
                "user_name": license.user.name,
            },
            "features": TIER_FEATURES.get(license.tier, []),
        }

    # ========== ATIVAÇÃO ==========
    async def activate_license(
        self,
        key: str,
        fingerprint: str,
        device_name: str = None,
        fingerprint_data: dict = None,
    ) -> Dict:
        """
        Ativa licença em um dispositivo (adiciona fingerprint)
        """
        validation = await self.validate_license(key, fingerprint)

        if not validation["valid"]:
            return {
                "success": False,
                "reason": validation.get("reason", "unknown"),
            }

        # Se for demo key, não vincula
        if validation.get("demo"):
            return {
                "success": True,
                "demo": True,
                "message": "Chave demo ativada",
                "license": validation["license"],
                "features": validation["features"],
            }

        license_data = validation["license"]
        if not license_data.get("key"):
            return {"success": False, "reason": "demo_no_activation"}

        # Busca license real
        result = await self.db.execute(
            select(License).where(License.key == license_data["key"])
        )
        license = result.scalar_one_or_none()

        if not license:
            return {"success": False, "reason": "not_found"}

        # Já vinculado a este fingerprint?
        fingerprints = license.fingerprints or []
        if fingerprint in fingerprints:
            return {
                "success": True,
                "message": "Dispositivo já vinculado",
                "license": self._license_to_dict(license),
                "features": TIER_FEATURES.get(license.tier, []),
            }

        # Tem espaço para novo dispositivo?
        if len(fingerprints) >= license.max_devices:
            return {
                "success": False,
                "reason": "device_limit_reached",
                "max_devices": license.max_devices,
                "current_devices": len(fingerprints),
            }

        # Adiciona fingerprint
        fingerprints.append(fingerprint)
        license.fingerprints = fingerprints
        license.devices_used = len(fingerprints)
        license.activation_count += 1
        if not license.activated_at:
            license.activated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(license)

        logger.info(
            f"✅ License {mask_license_key(license.key)} ativada em fingerprint {fingerprint[:8]}..."
        )

        return {
            "success": True,
            "message": "Licença ativada com sucesso",
            "license": self._license_to_dict(license),
            "features": TIER_FEATURES.get(license.tier, []),
        }

    # ========== DESATIVAÇÃO ==========
    async def deactivate_license(
        self,
        key: str,
        fingerprint: str = None,
    ) -> Dict:
        """Desativa licença (remove fingerprint)"""
        result = await self.db.execute(
            select(License).where(License.key == key.upper().strip())
        )
        license = result.scalar_one_or_none()

        if not license:
            return {"success": False, "reason": "not_found"}

        if fingerprint and license.fingerprints:
            if fingerprint in license.fingerprints:
                license.fingerprints = [f for f in license.fingerprints if f != fingerprint]
                license.devices_used = len(license.fingerprints)
                await self.db.commit()
                return {
                    "success": True,
                    "message": f"Dispositivo {fingerprint[:8]}... removido",
                }
            return {"success": False, "reason": "fingerprint_not_found"}
        else:
            # Revoga licença inteira
            license.status = LicenseStatus.REVOKED
            license.revoked_at = datetime.utcnow()
            license.revoked_reason = "Desativação manual"
            await self.db.commit()
            return {
                "success": True,
                "message": "Licença revogada",
            }

    # ========== REVOGAÇÃO (admin) ==========
    async def revoke_license(self, key: str, reason: str = None) -> bool:
        """Admin revoga licença"""
        result = await self.db.execute(
            select(License).where(License.key == key.upper().strip())
        )
        license = result.scalar_one_or_none()

        if not license:
            return False

        license.status = LicenseStatus.REVOKED
        license.revoked_at = datetime.utcnow()
        license.revoked_reason = reason or "Revogada por administrador"
        await self.db.commit()

        logger.warning(f"🚫 License {mask_license_key(license.key)} revogada: {reason}")
        return True

    # ========== QUERIES ==========
    async def get_user_licenses(self, user: User) -> List[License]:
        """Retorna licenças ativas do usuário"""
        result = await self.db.execute(
            select(License).where(
                and_(
                    License.user_id == user.id,
                    License.status == LicenseStatus.ACTIVE,
                )
            ).order_by(License.expires_at.desc())
        )
        return result.scalars().all()

    async def get_license_by_key(self, key: str) -> Optional[License]:
        result = await self.db.execute(
            select(License).where(License.key == key.upper().strip())
        )
        return result.scalar_one_or_none()

    # ========== HELPERS ==========
    def _demo_key_to_tier(self, key: str) -> str:
        if "DEMO1" in key:
            return "pro"
        if "DEMO5" in key:
            return "premium"
        if "INST1" in key:
            return "institutional"
        return "pro"

    def _license_to_dict(self, license: License) -> dict:
        return {
            "key": license.key,
            "tier": license.tier,
            "status": str(license.status),
            "issued_at": license.issued_at.isoformat(),
            "activated_at": license.activated_at.isoformat() if license.activated_at else None,
            "expires_at": license.expires_at.isoformat(),
            "days_remaining": license.days_remaining,
            "devices_used": license.devices_used,
            "max_devices": license.max_devices,
        }
