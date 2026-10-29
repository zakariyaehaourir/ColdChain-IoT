from django.shortcuts import render
from django.http import JsonResponse


def test_json_view(request):
    return JsonResponse("Yoooooo GIGI!", safe=False)
