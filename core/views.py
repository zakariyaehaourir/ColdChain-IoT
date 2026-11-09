from django.shortcuts import render
from django.http import JsonResponse
from core.models import FridgeSensor


def test_json_view(request):
    return JsonResponse("Yoooooo GIGI!", safe=False)


def home_view(request):
    latest_sensor = FridgeSensor.objects.order_by("-dt").first()
    context = {
        "latest_sensor": latest_sensor,
        "active_page": "dashboard",
    }
    return render(request, "index.html", context)


def history_view(request):
    sensors = FridgeSensor.objects.order_by("-dt")
    context = {
        "sensors": sensors,
        "active_page": "history",
    }
    return render(request, "history.html", context)
