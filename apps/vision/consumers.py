import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
#import cv2
#import numpy as np

QUEUE = asyncio.Queue(maxsize=1)


class FrameConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            #frame = np.frombuffer(bytes_data, dtype=np.uint8)
            #frame = cv2.imdecode(frame, cv2.IMREAD_ANYCOLOR)
            #cv2.rectangle(frame, (10, 10), (100, 100), (0, 255, 0), 1)
            if QUEUE.full():
                await QUEUE.get()
            #await QUEUE.put(frame)
            await QUEUE.put(bytes_data)
