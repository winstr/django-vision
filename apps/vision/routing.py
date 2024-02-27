from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/stream/', consumers.FrameConsumer.as_asgi()),
]