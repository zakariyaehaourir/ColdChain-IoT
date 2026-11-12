import logging
from .models import FridgeSensor
from config.serializers import DHT11serialize
from django.conf import settings
from rest_framework import generics
from .signals import high_temperature_detected

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
        
        if temperature > settings.CRITICAL_TEMPERATURE_THRESHOLD:
            high_temperature_detected.send(sender=self.__class__, temperature=temperature)