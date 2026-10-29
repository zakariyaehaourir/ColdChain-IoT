from rest_framework import serializers
from core import models

class DHT11serialize(serializers.ModelSerializer):
    class Meta:
        model = models.FridgeSensor
        fields = '__all__'
