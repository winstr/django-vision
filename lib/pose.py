from pathlib import Path
from typing import Union, Tuple, List

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from lib.skeleton import connections


def plot_box(img:np.ndarray, box:np.ndarray):
    # Expected box shape: (7,)
    box_xyxy = tuple(box[:4].astype(np.int32))
    box_id = int(box[4])
    box_category_id = int(box[5])
    box_conf = box[6]
    cv2.rectangle(img, box_xyxy[:2], box_xyxy[2:], (0, 255, 0), 1)
    plot_textbox(img, 'Person', box_xyxy[:2], (0, 255, 0), (0, 0, 0))


def plot_kpts(img:np.ndarray, kpts:np.ndarray, thres:float=0.5):
    # Expected kpts shape: (17, 3)
    kpts_xy = kpts[:, :2].astype(np.int32)
    kpts_conf = kpts[:, 2]
    for stt_i in range(len(kpts)):
        stt_xy = tuple(kpts_xy[stt_i])
        if kpts_conf[stt_i] < thres:
            continue
        for end_i in connections[stt_i]:
            if kpts_conf[end_i] < thres:
                continue
            end_xy = tuple(kpts_xy[end_i])
            cv2.line(img, stt_xy, end_xy, (0, 255, 0), 1)
        cv2.circle(img, stt_xy, 1, (0, 255, 0), 1)


def plot_textbox(img:np.ndarray,
                 text:str,
                 text_org:Tuple[int, int],
                 box_color:Tuple[int, int, int],
                 font_color:Tuple[int, int, int]):

    scale = 0.5                         # font scale
    thick = 1                           # font thickness
    style = cv2.FONT_HERSHEY_SIMPLEX    # font style

    (width, height), _ = cv2.getTextSize(text, style, scale, thick)
    x, y = text_org
    x_, y_ = x + width, y + height
    cv2.rectangle(img, (x, y), (x_, y_), box_color, cv2.FILLED)
    cv2.putText(img, text, (x, y_), style, scale, font_color, thick)


class Pose(YOLO):

    def __init__(self, model: Union[str, Path]='yolov8n-pose.pt', task=None):
        super().__init__(model, task)

    def estimate(self, img:np.ndarray, enable_tracking=False, **kwargs) -> List[Results]:
        if enable_tracking:
            return super().track(img, persist=True, **kwargs)
        else:
            return super().predict(img, **kwargs)

    @staticmethod
    def visualize(results:List[Results]) -> np.ndarray:
        img = results[0].orig_img                        # original image
        boxes = results[0].boxes.data.cpu().numpy()      # bounding boxes
        kptss = results[0].keypoints.data.cpu().numpy()  # keypoints array
        for box, kpts in zip(boxes, kptss):
            plot_box(img, box)
            plot_kpts(img, kpts)
        return img
