from django.shortcuts import render
from django.http import JsonResponse
from core.models import FridgeSensor


def test_json_view(request):
    return JsonResponse("Yoooooo GIGI!", safe=False)


def home_view(request):
    sensors = FridgeSensor.objects.all().order_by("-dt")
    context = {
        "title": "Fridge Data",
        "sensors": sensors,
        "latest_sensor": sensors.first(),
    }
    return render(request, "index.html", context)
