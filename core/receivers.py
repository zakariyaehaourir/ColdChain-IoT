import logging
import threading
from django.dispatch import receiver

from .signals import high_temperature_detected
from core.services.alerts import AlertStrategyFactory
from core.Exceptions import AlertDispatchError

logger = logging.getLogger(__name__)

def background_alert_task(temperature: float):
    """
    Background task executed.
    """
    logger.info(f"[Intern Thread] Begining async task with {temperature}°C")
    
    strategies = AlertStrategyFactory.get_active_strategies()
    
    for strategy in strategies:
        try:
            strategy.sendAlert(temperature)
        except AlertDispatchError as e:
            logger.error(f"[Thread interne] Error strategie {e}")

@receiver(high_temperature_detected)
def handle_high_temperature_event(sender, temperature, **kwargs):
    """
    Subscriber : Listen and run thread to execute sending alerts event
    """

    thread = threading.Thread(
        target=background_alert_task, 
        args=(temperature,)
    )
    
    thread.start()