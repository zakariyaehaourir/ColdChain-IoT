from email.mime.image import MIMEImage
from pathlib import Path

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from .alert_strategy import AlertStrategy
from django.conf import settings
import logging
from .email_recipient_provider import OperatorEmailProvider
from core.Exceptions import AlertDispatchError
logger = logging.getLogger(__name__)

class EmailAlertStrategy(AlertStrategy):
    def __init__(self, email_provider: OperatorEmailProvider):
        self.email_provider = email_provider
    
    def sendAlert(self, temperature: float) -> None:
        recipients = self.email_provider.get_operator_emails()
        
        if not recipients:
            logger.warning("No operator emails found. Skipping email alert.")
            return

        try:
            context = {
                "temperature": temperature,
                "threshold": settings.CRITICAL_TEMPERATURE_THRESHOLD,
                "timestamp": timezone.localtime(),
                "device_name": getattr(settings, "TEMPERATURE_SENSOR_NAME", "ColdChain sensor"),
                "location": getattr(settings, "TEMPERATURE_SENSOR_LOCATION", ""),
                "recipient_name": "",
                "dashboard_url": getattr(settings, "DASHBOARD_URL", ""),
                "settings_url": getattr(settings, "ALERT_SETTINGS_URL", ""),
            }
            html_message = render_to_string("temperature_alert.html", context)
            text_message = strip_tags(html_message)
            message = EmailMultiAlternatives(
                subject="Critical Alert: High Temperature Detected!",
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
            )
            message.attach_alternative(html_message, "text/html")
            banner_path = (
                Path(settings.BASE_DIR)
                / "core"
                / "static"
                / "core"
                / "img"
                / "banner-1200x320.png"
            )
            banner = MIMEImage(banner_path.read_bytes(), _subtype="png")
            banner.add_header("Content-ID", "<coldchain-banner>")
            banner.add_header(
                "Content-Disposition",
                "inline",
                filename="coldchain-banner.png",
            )
            message.attach(banner)
            message.send(fail_silently=False)
            logger.info(f"Email alert successfully sent to {len(recipients)} operators.")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            raise AlertDispatchError(f"Email Dispatch Error: {str(e)}") from e