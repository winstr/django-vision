import sys
import time
import traceback
from pathlib import Path
from typing import Iterable

import cv2
import flask

sys.path.append(str(Path(__file__).parents[1]))
from observer.utils.color import ALL_COLORS, hex_to_bgr
from observer.utils.video import SkipFlags, VideoCapture
from observer.utils.plotting import plot_text
from observer.engine.yolov8.pose import PoseEstimator


app = flask.Flask(__name__)


def to_jpeg(frame):
    is_encoded, jpeg = cv2.imencode('.jpeg', frame)
    if not is_encoded:
        msg = 'Failed to encode the frame.'
        raise RuntimeError(msg)
    return jpeg.tobytes()


def to_http_multipart(jpeg: bytes):
    return (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n'
        + jpeg +
        b'\r\n')


class Timer():

    prev_timer_ids = set()
    curr_timer_ids = set()
    timers = {}

    @staticmethod
    def syncronize(object_ids: Iterable[int]):
        object_ids = set(object_ids)
        for object_id in Timer.prev_timer_ids - object_ids:
            del Timer.timers[object_id]
        for object_id in object_ids - Timer.prev_timer_ids:
            Timer.timers[object_id] = Timer()
        Timer.prev_timer_ids = object_ids

    def __init__(self):
        self.start_time = time.time()

    def get_elapsed_time(self) -> str:
        elapsed_time = time.time() - self.start_time
        h, r = divmod(elapsed_time, 3600)
        m, s = divmod(r, 60)
        return f'{int(h):02}:{int(m):02}:{int(s):02}'


def main():
    video_source = 'rtsp://192.168.1.101:554/profile2/media.smp'
    target_size = (640, 480)
    skip_interval = 3

    try:
        estimator = PoseEstimator()
        skip_flags = SkipFlags(skip_interval)
        boxes = None

        colors = [hex_to_bgr(hex_color[500])
                  for hex_color in ALL_COLORS]

        cap = VideoCapture(video_source)
        while True:
            frame = next(cap)
            frame = cv2.resize(frame, target_size)

            skip_on = next(skip_flags)
            if not skip_on:
                preds = estimator.estimate(frame, verbose=False)
                boxes = preds[0].boxes.data.cpu().numpy()
                box_ids = boxes[:, 4].astype(int)
                Timer.syncronize(box_ids)

            for i, box in enumerate(boxes):
                color = colors[i % len(colors)]
                xyxy = tuple(box[:4].astype(int))
                pt1, pt2 = xyxy[:2], xyxy[2:]
                cv2.rectangle(frame, pt1, pt2, color, thickness=1)

                box_id = int(box[4])
                box_conf = f'{(box[5] * 100):.2f}%'
                box_time = Timer.timers[box_id].get_elapsed_time()
                plot_text(frame,
                          f'Person, {box_conf}, {box_time}',
                          pt1,
                          bgcolor=color)

            jpeg = to_jpeg(frame)
            data = to_http_multipart(jpeg)
            yield data

    except:
        traceback.print_exc()

    cap.release()


@app.route('/video')
def video():
    return flask.Response(
        main(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
