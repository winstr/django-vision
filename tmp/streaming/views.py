import logging
import traceback

from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2

from .src.video import VideoCaptureThread, Resolution


logging.basicConfig(
    format='[%(levelname)s:%(filename)s:%(funcName)s] %(message)s',
    level=logging.DEBUG
)


def sample(request):
    return render(request, 'streaming/sample.html')


def stream(request):
    def generate_image():
        stream_source = 'rtsp://192.168.1.101:554/profile2/media.smp'
        target_size = Resolution(width=640, height=360)
        cap_thread = VideoCaptureThread(stream_source, target_size)
        
        logging.debug('started capture thread.')
        cap_thread.start()

        try:
            while True:
                frame = cap_thread.read()
                if frame is None:
                    continue
                is_encoded, jpeg = cv2.imencode('.jpeg', frame)
                if not is_encoded:
                    raise RuntimeError('jpeg encode error.')
                jpeg = jpeg.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n'
                       + jpeg + b'\r\n')
        except:
            traceback.print_exc()
        finally:
            cap_thread.stop()

    return StreamingHttpResponse(
        generate_image(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )