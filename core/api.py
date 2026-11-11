import logging
from .models import FridgeSensor
from config.serializers import DHT11serialize
from django.conf import settings
from core.Exceptions import AlertDispatchError
from core.services.alerts import AlertStrategyFactory
from rest_framework import generics


logger = logging.getLogger(__name__)

class SensorListCreateView(generics.ListCreateAPIView):
    """
    Endpoint RESTful :
    - GET
    - POST 
    """
    queryset = FridgeSensor.objects.all()
    serializer_class = DHT11serialize

    def perform_create(self, serializer):
        instance = serializer.save()
        temperature = float(instance.temp)
        

        if temperature <= settings.CRITICAL_TEMPERATURE_THRESHOLD:
            logger.warning(f"Critical temp detected ({temperature}°C). sending alerts...")
            
            strategies = AlertStrategyFactory.get_active_strategies()
            
            for strategy in strategies:
                try:
                    strategy.sendAlert(temperature)
                except AlertDispatchError as e:
                    logger.error(f"Error while sending alerts: {e}")