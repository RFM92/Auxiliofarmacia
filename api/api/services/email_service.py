"""
EmailService - Envio de emails transacionais
Suporta SMTP e SendGrid
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
from pathlib import Path
import jinja2

from ..config import settings

logger = logging.getLogger(__name__)


# Jinja2 templates
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "emails"
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)


class EmailService:
    """Serviço de envio de emails"""

    def __init__(self):
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.reply_to = settings.EMAIL_REPLY_TO
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.sendgrid_key = settings.SENDGRID_API_KEY

    async def send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
    ) -> bool:
        """
        Envia email transacional
        """
        try:
            # Tenta SendGrid primeiro (se configurado)
            if self.sendgrid_key:
                return await self._send_via_sendgrid(
                    to_email, subject, html_content, text_content, attachments
                )

            # Senão usa SMTP
            return await self._send_via_smtp(
                to_email, subject, html_content, text_content, attachments
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email para {to_email}: {e}")
            return False

    # ========== TEMPLATES PRÉ-DEFINIDOS ==========
    async def send_welcome(self, user_name: str, user_email: str) -> bool:
        """Email de boas-vindas"""
        try:
            template = jinja_env.get_template("welcome.html")
            html = template.render(
                user_name=user_name,
                dashboard_url="https://auxfarmacia.com.br/dashboard",
            )
            return await self.send(
                to_email=user_email,
                subject="🎉 Bem-vindo ao Auxílio Farmácia!",
                html_content=html,
                text_content=f"Olá {user_name}, bem-vindo ao Auxílio Farmácia!",
            )
        except Exception as e:
            logger.error(f"Erro no template welcome: {e}")
            return False

    async def send_verification(
        self,
        user_name: str,
        user_email: str,
        verification_token: str,
    ) -> bool:
        """Email de verificação de conta"""
        try:
            verify_url = f"{settings.APP_URL}/verify?token={verification_token}"
            template = jinja_env.get_template("verify.html")
            html = template.render(
                user_name=user_name,
                verify_url=verify_url,
            )
            return await self.send(
                to_email=user_email,
                subject="Confirme seu email - Auxílio Farmácia",
                html_content=html,
            )
        except Exception as e:
            logger.error(f"Erro no template verify: {e}")
            return False

    async def send_password_reset(
        self,
        user_name: str,
        user_email: str,
        reset_token: str,
    ) -> bool:
        """Email de reset de senha"""
        try:
            reset_url = f"{settings.APP_URL}/reset-password?token={reset_token}"
            template = jinja_env.get_template("reset_password.html")
            html = template.render(
                user_name=user_name,
                reset_url=reset_url,
            )
            return await self.send(
                to_email=user_email,
                subject="🔒 Recuperação de senha - Auxílio Farmácia",
                html_content=html,
            )
        except Exception as e:
            logger.error(f"Erro no template reset: {e}")
            return False

    async def send_license_activated(
        self,
        user_name: str,
        user_email: str,
        license_key: str,
        tier: str,
        days: int,
    ) -> bool:
        """Email com chave de licença ativada"""
        try:
            template = jinja_env.get_template("license_activated.html")
            html = template.render(
                user_name=user_name,
                license_key=license_key,
                tier=tier.upper(),
                days=days,
            )
            return await self.send(
                to_email=user_email,
                subject=f"🎉 Sua licença Auxílio Farmácia {tier.upper()} está ativa!",
                html_content=html,
            )
        except Exception as e:
            logger.error(f"Erro no template license_activated: {e}")
            return False

    async def send_payment_receipt(
        self,
        user_name: str,
        user_email: str,
        plan: str,
        value: float,
        method: str,
        payment_id: str,
    ) -> bool:
        """Email de confirmação de pagamento"""
        try:
            template = jinja_env.get_template("payment_receipt.html")
            html = template.render(
                user_name=user_name,
                plan=plan.upper(),
                value=f"R$ {value:.2f}",
                method=method,
                payment_id=payment_id,
            )
            return await self.send(
                to_email=user_email,
                subject="✅ Pagamento confirmado - Auxílio Farmácia",
                html_content=html,
            )
        except Exception as e:
            logger.error(f"Erro no template payment_receipt: {e}")
            return False

    async def send_license_expiring_soon(
        self,
        user_name: str,
        user_email: str,
        days_remaining: int,
        license_key: str,
    ) -> bool:
        """Email de aviso de licença expirando"""
        try:
            template = jinja_env.get_template("license_expiring.html")
            html = template.render(
                user_name=user_name,
                days_remaining=days_remaining,
                license_key=license_key,
                renew_url=f"{settings.APP_URL}/renew",
            )
            return await self.send(
                to_email=user_email,
                subject=f"⚠️ Sua licença Auxílio Farmácia expira em {days_remaining} dias",
                html_content=html,
            )
        except Exception as e:
            logger.error(f"Erro no template license_expiring: {e}")
            return False

    # ========== ENVIO SMTP ==========
    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
    ) -> bool:
        """Envia via SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP não configurado - email não enviado")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg["Reply-To"] = self.reply_to

        if text_content:
            part1 = MIMEText(text_content, "plain")
            msg.attach(part1)

        part2 = MIMEText(html_content, "html")
        msg.attach(part2)

        # Anexos
        if attachments:
            for att in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(att["content"])
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={att['filename']}",
                )
                msg.attach(part)

        # Envia
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            logger.info(f"✅ Email enviado para {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Erro SMTP: {e}")
            return False

    # ========== ENVIO SENDGRID ==========
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
    ) -> bool:
        """Envia via SendGrid API (HTTP)"""
        import httpx

        payload = {
            "personalizations": [{
                "to": [{"email": to_email}],
                "subject": subject,
            }],
            "from": {"email": self.from_email, "name": self.from_name},
            "reply_to": {"email": self.reply_to},
            "content": [
                {
                    "type": "text/plain",
                    "value": text_content or html_content[:500],
                },
                {
                    "type": "text/html",
                    "value": html_content,
                },
            ],
        }

        if attachments:
            payload["attachments"] = [
                {
                    "content": a["content_b64"],
                    "filename": a["filename"],
                    "type": a.get("type", "application/octet-stream"),
                }
                for a in attachments
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.sendgrid_key}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code in (200, 202):
                logger.info(f"✅ Email enviado via SendGrid para {to_email}")
                return True
            logger.error(f"Erro SendGrid {response.status_code}: {response.text}")
            return False
