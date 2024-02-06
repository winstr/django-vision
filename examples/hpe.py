import sys
import traceback
from pathlib import Path
from typing import Dict

import cv2
import flask
import numpy as np
from ultralytics import YOLO

sys.path.append(str(Path(__file__).absolute().parents[1]))
from lib.pose import DEAFAULT_SCHEMA
from utils.video import FrameCapture, FrameSkipper
from utils.color import ALL_COLORS, hex2bgr
from utils.plotting import plot_bounding_box, plot_keypoints


def plot_pose(
        img: np.ndarray,
        boxes: np.ndarray,
        kptss: np.ndarray,
        names: Dict[int, str],
        bbox_conf_thres: float = 0.5,
        kpts_conf_thres: float = 0.5,
        label_on: bool = False,
    ) -> None:

    color = [hex2bgr(c[500]) for c in ALL_COLORS]

    for bbox, kpts in zip(boxes, kptss):
        if len(bbox) == 7:
            bbox_id, bbox_conf = int(bbox[4]), bbox[5]
        else:
            bbox_id, bbox_conf = 0, bbox[4]

        if bbox_conf < bbox_conf_thres:
            continue

        if label_on:
            label = f'{names[bbox[-1]]} {bbox_conf:.3f}'
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
                    # TODO: tracking.
                    preds = model.track(frame,
                                        persist=True,
                                        verbose=False)
                    # TODO: non-tracking.
                    #preds = model.predict(frame,
                    #                      verbose=False)

                if not preds is None:
                    results = preds[0]
                    boxes = results.boxes.data.cpu().numpy()
                    kptss = results.keypoints.data.cpu().numpy()
                    plot_pose(frame,
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
