# mochafolk_backend/routing.py
from django.urls import re_path
from shops import consumers

websocket_urlpatterns = [
    re_path(r'ws/queue/(?P<shop_pk>\d+)/$', consumers.QueueConsumer.as_asgi()),
]