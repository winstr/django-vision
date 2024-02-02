import sys
import time
import traceback
from pathlib import Path
from typing import Dict

import cv2
import flask
import numpy as np
from ultralytics import YOLO

sys.path.append(str(Path(__file__).parents[1]))
from lib.timer import TimerManager
from utils.video import FrameCapture, FrameSkipper
from utils.color import ALL_COLORS, hex2bgr
from utils.plotting import plot_bounding_box


def plot_boxes_in_redzone(
        img: np.ndarray,
        boxes: np.ndarray,
        names: Dict[int, str],
        timer_manager: TimerManager,
        redzone_mask: np.ndarray,
        bbox_conf_thres: float = 0.5,
        label_on: bool = False,
    ) -> None:

    # --- DIRTY CODE ---
    # boxes shape is (n, 7)
    # box in boxes is (x_min, y_min, x_max, y_max, box_id, conf, class_id)
    boxes = boxes[boxes[:, 5] >= bbox_conf_thres]
    boxes_xyxy = boxes[:, :4].astype(int)
    boxes_cxcy = np.empty(shape=(len(boxes), 2), dtype=int)
    boxes_cxcy[:, 0] = (boxes_xyxy[:, 0] + boxes_xyxy[:, 2]) >> 1  # = int((x1 + x2) / 2)
    boxes_cxcy[:, 1] = (boxes_xyxy[:, 1] + boxes_xyxy[:, 3]) >> 1  # = int((y1 + y2) / 2)
    # dtype of redzone_mask is uint8, ndim is 2, value is either 0 or 255.
    boxes = boxes[redzone_mask[boxes_cxcy[:, 1], boxes_cxcy[:, 0]] == 255]
    # --- ---

    boxes_ids = boxes[:, 4].astype(int)
    timer_manager.syncronize(boxes_ids)

    color = [hex2bgr(c[500]) for c in ALL_COLORS]

    for bbox in boxes:
        bbox_id, bbox_conf = int(bbox[4]), bbox[5]
        xyxy = bbox[:4].astype(int)

        if label_on:
            bbox_name = names[bbox[-1]]
            bbox_conf = f'{bbox_conf:.3f}'
            bbox_time = timer_manager.timers[bbox_id].get_elapsed_time()
            label = f'{bbox_name} {bbox_conf} {bbox_time}'
        else:
            label = None

        color_id = bbox_id % len(color)
        plot_bounding_box(img,
                          xyxy,
                          color[color_id],
                          label=label)


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
    redzone = ((10, 10),
               (20, 350),
               (300, 340),
               (240, 20))

    model = YOLO('yolov8n.pt')
    skipper = FrameSkipper(skip_interval)
    manager = TimerManager()
    names = model.names

    redzone = np.array(redzone)
    redzone = redzone.reshape(1, -1, 2)
    redzone_mask = np.zeros(shape=target_size[::-1], dtype=np.uint8)
    cv2.fillPoly(redzone_mask, [redzone], 255)

    try:
        with FrameCapture(video_source) as cap:
            preds = None
            for frame in cap:
                frame = cv2.resize(frame, target_size)
                cv2.polylines(frame,
                              [redzone],
                              True,
                              (0, 0, 255),
                              2)

                if not skipper.is_skip():
                    # TODO: only possible tracking mode.
                    preds = model.track(frame,
                                        persist=True,
                                        verbose=False,
                                        classes=[0],)

                if not preds is None:
                    results = preds[0]
                    boxes = results.boxes.data.cpu().numpy()
                    plot_boxes_in_redzone(frame,
                                          boxes,
                                          names,
                                          manager,
                                          redzone_mask=redzone_mask,
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
