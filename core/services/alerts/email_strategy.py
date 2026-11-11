from django.core.mail import send_mail
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
            subject = "Critical Alert: High Temperature Detected!"
            message = f"The ESP sensor has recorded an abnormal temperature of {temperature}°C."
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            logger.info(f"Email alert successfully sent to {len(recipients)} operators.")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            raise AlertDispatchError(f"Email Dispatch Error: {str(e)}") from e