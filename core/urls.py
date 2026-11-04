from django.urls import path
from core.views import *
from core.api import Dlist, Dhtviews, SensorListCreateView
urlpatterns = [
    path('', test_json_view, name='test_json'),
    path('sensors/', SensorListCreateView.as_view(), name='sensor-list-create'),

]