import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer


QUEUE = asyncio.Queue(maxsize=1)


class FrameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            pass
        if bytes_data:
            if QUEUE.full():
                await QUEUE.get()
            await QUEUE.put(bytes_data)


# daphne -b 172.27.1.14 -p 8888 config.asgi:application
# daphne -b 172.27.1.14 -p 8888 config.asgi:application --verbosity 2
