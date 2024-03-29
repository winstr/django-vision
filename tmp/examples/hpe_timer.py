import sys
import time
import traceback
from pathlib import Path
from typing import Iterable, Dict

import cv2
import flask
import numpy as np
from ultralytics import YOLO

sys.path.append(str(Path(__file__).absolute().parents[1]))
from lib.pose import DEAFAULT_SCHEMA
from utils.video import FrameCapture, FrameSkipper
from utils.color import ALL_COLORS, hex2bgr
from utils.plotting import plot_bounding_box, plot_keypoints


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

    def __init__(self) -> None:
        self.start_time = time.time()

    def get_elapsed_time(self) -> str:
        elapsed_time = time.time() - self.start_time
        h, r = divmod(elapsed_time, 3600)
        m, s = divmod(r, 60)
        return f'{int(h):02}:{int(m):02}:{int(s):02}'


def plot_pose_with_timer(
        img: np.ndarray,
        boxes: np.ndarray,
        kptss: np.ndarray,
        names: Dict[int, str],
        bbox_conf_thres: float = 0.5,
        kpts_conf_thres: float = 0.5,
        label_on: bool = False,
    ) -> None:

    boxes_ids = boxes[:, 4].astype(int)
    Timer.syncronize(boxes_ids)

    color = [hex2bgr(c[500]) for c in ALL_COLORS]

    for bbox, kpts in zip(boxes, kptss):
        bbox_id, bbox_conf = int(bbox[4]), bbox[5]
        if bbox_conf < bbox_conf_thres:
            continue

        if label_on:
            bbox_name = names[bbox[-1]]
            bbox_conf = f'{bbox_conf:.3f}'
            bbox_time = Timer.timers[bbox_id].get_elapsed_time()
            label = f'{bbox_name} {bbox_conf} {bbox_time}'
        else:
            label = None

        color_id = bbox_id % len(color)
        plot_bounding_box(img,
                          bbox[:4],
                          color[color_id],
                          label=label)
        plot_keypoints(img,
                       kpts,
                       color[color_id],
                       schema=DEAFAULT_SCHEMA,
                       conf_thres=kpts_conf_thres)


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


app = flask.Flask(__name__)


def main():
    video_source = 'rtsp://192.168.1.101:554/profile2/media.smp'
    target_size = (640, 360)
    skip_interval = 3

    model = YOLO('yolov8n-pose.pt')
    skipper = FrameSkipper(skip_interval)
    names = model.names

    try:
        with FrameCapture(video_source) as cap:
            preds = None
            for frame in cap:
                frame = cv2.resize(frame, target_size)

                if not skipper.is_skip():
                    # TODO: only possible tracking mode.
                    preds = model.track(frame,
                                        persist=True,
                                        verbose=False)

                if not preds is None:
                    results = preds[0]
                    boxes = results.boxes.data.cpu().numpy()
                    kptss = results.keypoints.data.cpu().numpy()
                    plot_pose_with_timer(frame,
                                         boxes,
                                         kptss,
                                         names,
                                         label_on=True)

                jpeg = to_jpeg(frame)
                data = to_http_multipart(jpeg)
                yield data

    except:
        traceback.print_exc()


@app.route('/video')
def video():
    return flask.Response(
        main(),
        mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
