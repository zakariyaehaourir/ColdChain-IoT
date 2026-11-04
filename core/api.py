from .models import FridgeSensor
from config.serializers import DHT11serialize
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response


@api_view(['GET'])
def Dlist(request):
    all_data = FridgeSensor.objects.all()
    data = DHT11serialize(all_data, many=True).data
    return Response({'data': data})


class Dhtviews(generics.CreateAPIView):

    queryset = FridgeSensor.objects.all()
    serializer_class = DHT11serialize


class SensorListCreateView(generics.ListCreateAPIView):
    queryset = FridgeSensor.objects.all()
    serializer_class = DHT11serialize