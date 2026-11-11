from typing import List

from .alert_strategy import AlertStrategy
from .email_strategy import EmailAlertStrategy
from .telegram_strategy import TelegramAlertStrategy
from .email_recipient_provider import MockOperatorEmailProvider

class AlertStrategyFactory:
    """
    Factory responsible for instantiating and wiring alert strategies.
    """
    
    @staticmethod
    def get_active_strategies() -> List[AlertStrategy]:
        """
        Builds and returns all active alert strategies.
        """

        email_provider = MockOperatorEmailProvider()
        

        email_strategy = EmailAlertStrategy(email_provider=email_provider)
        telegram_strategy = TelegramAlertStrategy()

        return [email_strategy, telegram_strategy]