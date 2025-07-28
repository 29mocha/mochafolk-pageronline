# mochafolk_backend/asgi.py
import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import mochafolk_backend.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mochafolk_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            mochafolk_backend.routing.websocket_urlpatterns
        )
    ),
})