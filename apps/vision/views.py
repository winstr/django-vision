import json
import logging
import traceback
from typing import Dict, Any

from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import numpy as np

from .src.colors import ALL_COLORS, hex2bgr
from .src.plotting import plot_bounding_box, plot_keypoints
from .src.timer import TimerManager
from .consumers import QUEUE


def vision(request):
    return render(request, 'vision/vision.html')


async def stream(request):
    async def generate_image(delimiter: str=b'\xFF\xFE\xFF\xFE'):
        try:
            while True:
                bytes_data = await QUEUE.get()

                delimiter_index = bytes_data.find(delimiter)
                frame = bytes_data[:delimiter_index]
                preds = bytes_data[delimiter_index + len(delimiter):]

                frame = np.frombuffer(bytes_data, dtype=np.uint8)
                frame = cv2.imdecode(frame, cv2.IMREAD_ANYCOLOR)
                preds = json.loads(preds.decode('utf-8'))

                # -------- START --------
                # args: frame, preds
                #boxes = np.array(preds['boxes'], dtype=np.float32)
                #kptss = np.array(preds['kptss'], dtype=np.float32)

                #for box in boxes:
                #    p1 = tuple(box[:2].astype(int))
                #    p2 = tuple(box[2:4].astype(int))
                #    cv2.rectangle(frame, p1, p2, (0, 255, 0), 1)
                # out: frame
                # --------- END ---------

                frame = plot(frame, preds)

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


# --- HARDCODE ---
COLORS = color = [hex2bgr(c[500]) for c in ALL_COLORS]
POSE_SCHEMA = {
    0: [1, 2,], 1: [3,], 2: [4,], 3: [], 4: [],
    5: [6, 7, 11,], 6: [8, 12,], 7: [9,], 8: [10,], 9: [],
    10: [], 11: [12, 13,], 12: [14,], 13: [15,], 14: [16,],
    15: [], 16: []}
REDZONE = np.array(
    [(10, 10), (20, 350), (300, 340), (240, 20)], dtype=int
).reshape(1, -1, 2)
REDZONE_MASK = np.zeros(
    shape=(360, 640),
    dtype=np.uint8)
cv2.fillPoly(REDZONE_MASK, [REDZONE], 255)
MANAGER = TimerManager()
# ----------------


def plot(
        frame: np.ndarray,
        preds: Dict[str, Any],
        bbox_conf_thres: float = 0.5,
        kpts_conf_thres: float = 0.5,
    ) -> np.ndarray:

    boxes = np.array(preds['boxes'], dtype=np.float32)
    kptss = np.array(preds['kptss'], dtype=np.float32)
    frame_hpe = np.copy(frame)
    if boxes.size != 0:
        for bbox, kpts in zip(boxes, kptss):
            bbox_id, bbox_conf = int(bbox[4]), bbox[5]
            if bbox_conf < bbox_conf_thres:
                continue
            color_id = bbox_id % len(COLORS)
            label = f'Person {bbox_conf:.3f}'
            plot_bounding_box(
                frame_hpe, bbox[:4], COLORS[color_id], label=label)
            plot_keypoints(
                frame_hpe, kpts, COLORS[color_id], POSE_SCHEMA, kpts_conf_thres)

    frame_ids = np.copy(frame)
    cv2.polylines(frame_ids, [REDZONE], True, (0, 0, 255), 2)
    if boxes.size != 0:
        # --- DIRTY CODE ---
        # boxes shape is (n, 7)
        # box in boxes is (x_min, y_min, x_max, y_max, box_id, conf, class_id)
        boxes = boxes[boxes[:, 5] >= bbox_conf_thres]
        boxes_xyxy = boxes[:, :4].astype(int)
        boxes_cxcy = np.empty(shape=(len(boxes), 2), dtype=int)
        boxes_cxcy[:, 0] = (boxes_xyxy[:, 0] + boxes_xyxy[:, 2]) >> 1  # = int((x1 + x2) / 2)
        boxes_cxcy[:, 1] = (boxes_xyxy[:, 1] + boxes_xyxy[:, 3]) >> 1  # = int((y1 + y2) / 2)
        # dtype of redzone_mask is uint8, ndim is 2, value is either 0 or 255.
        boxes = boxes[REDZONE_MASK[boxes_cxcy[:, 1], boxes_cxcy[:, 0]] == 255]
        # --- ---
        boxes_ids = boxes[:, 4].astype(int)
        MANAGER.syncronize(boxes_ids)
        for bbox in boxes:
            bbox_id, bbox_conf = int(bbox[4]), bbox[5]
            xyxy = bbox[:4].astype(int)
            bbox_name = 'Person'
            bbox_conf = f'{bbox_conf:.3f}'
            bbox_time = MANAGER.timers[bbox_id].get_elapsed_time()
            label = f'{bbox_name} {bbox_conf} {bbox_time}'
            color_id = bbox_id % len(COLORS)
            plot_bounding_box(
                frame_ids, xyxy, COLORS[color_id], label=label)

    return np.hstack([frame_hpe, frame_ids])
