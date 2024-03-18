from django.apps import apps
from channels.generic.websocket import AsyncWebsocketConsumer


class VideoStreamConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = apps.get_app_config('vision').stream_queue

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.queue.put(None)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            pass
        if bytes_data:
            await self.queue.put(bytes_data)


# daphne -b 172.27.1.14 -p 8888 config.asgi:application
# daphne -b 172.27.1.14 -p 8888 config.asgi:application --verbosity 2
