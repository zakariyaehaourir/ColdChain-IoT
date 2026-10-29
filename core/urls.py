from django.urls import path
from core.views import *
from core.api import Dlist , Dhtviews
urlpatterns = [
    path('', test_json_view, name='test_json'),
    path('sensor/', Dlist, name='sensor-list'),
    path('sensor/create/', Dhtviews.as_view(), name='sensor-create')
]