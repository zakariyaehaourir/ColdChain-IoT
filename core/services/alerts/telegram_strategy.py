import logging
import requests
from django.conf import settings

from .alert_strategy import AlertStrategy
from core.Exceptions import AlertDispatchError

logger = logging.getLogger(__name__)

class TelegramAlertStrategy(AlertStrategy):
    def sendAlert(self, temperature: float) -> None:
        try:
            token = settings.TELEGRAM_BOT_TOKEN
            chat_id = settings.TELEGRAM_CHAT_ID
            
            message = f"⚠️ <b>ESP Alert</b> : Abnormal temperature detected ({temperature}°C)"
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            
            logger.info(f"Telegram alert successfully sent for {temperature}°C.")
            
        except requests.exceptions.RequestException as e:
            # 2. EXTRAIRE LE VRAI MESSAGE D'ERREUR DE TELEGRAM
            error_details = e.response.text if e.response is not None else str(e)
            logger.error(f"Failed to send Telegram alert: {error_details}")
            raise AlertDispatchError(f"Telegram Dispatch Error: {error_details}") from e