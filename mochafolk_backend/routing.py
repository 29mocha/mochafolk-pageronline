# mochafolk_backend/routing.py
from django.urls import re_path, path
from shops import consumers

websocket_urlpatterns = [
    # PERBAIKAN: Gunakan path yang lebih spesifik
    re_path(r'^ws/queue/(?P<shop_pk>\d+)/$', consumers.QueueConsumer.as_asgi()),
    # TAMBAHAN: Route untuk testing
    re_path(r'^ws/test/$', consumers.QueueConsumer.as_asgi()),
]