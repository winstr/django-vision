import asyncio
import logging
import traceback

from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2

from .consumers import FRAME_QUEUE


logging.basicConfig(
    format='[%(levelname)s:%(filename)s:%(funcName)s] %(message)s',
    level=logging.DEBUG
)


def vision(request):
    return render(request, 'vision/vision.html')


async def stream(request):
    async def generate_image():
        try:
            while True:
                frame = await FRAME_QUEUE.get()
                is_encoded, jpeg = cv2.imencode('.jpeg', frame)
                if not is_encoded:
                    raise RuntimeError('jpeg encode error.')
                jpeg = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + jpeg + b'\r\n')
        except:
            traceback.print_exc()

    return StreamingHttpResponse(
        generate_image(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )