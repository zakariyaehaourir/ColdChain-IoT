from django.urls import path
from django.http import JsonResponse
def test_json_view(request):
    return JsonResponse("Yoooooo GIGI!", safe=False)

urlpatterns = [
    path('', test_json_view, name='test_json'),
]