import os

import asyncio

import cv2
from django.apps import AppConfig
from django.conf import settings


class JPEGBytesQueue():

    def __init__(self):
        self._event = asyncio.Event()
        self._queue = asyncio.Queue(maxsize=1)
        self._blank = self._get_blank()

    @property
    def event(self):
        return self._event

    async def put(self, jpeg_bytes):
        if not self._event.is_set():
            self._event.set()
        if self._queue.full():
            await self._queue.get()
        await self._queue.put(jpeg_bytes)

    async def get(self):
        if not self._event.is_set():
            await asyncio.sleep(0.1)
            jpeg_bytes = self._blank
        else:
            jpeg_bytes = await self._queue.get()
            if jpeg_bytes is None:
                await asyncio.sleep(0.1)
                jpeg_bytes = self._blank
                self._event.clear()
        return jpeg_bytes

    def _get_blank(self):
        blank_img = 'static/apps/ai/vision/img/no_cam.jpg'
        blank_img = os.path.join(settings.BASE_DIR, blank_img)
        blank_img = cv2.imread(blank_img)
        blank_img = cv2.resize(blank_img, (640, 360))
        _, blank_img = cv2.imencode('.jpeg', blank_img)
        blank_img = blank_img.tobytes()
        return blank_img


class VisionConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai.vision'

    stream_queue = JPEGBytesQueue()

    def ready(self):
        pass
