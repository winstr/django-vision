from typing import Tuple, Dict, List

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from utils.plotting import plot_text


CATEGORY_MAP = {0: 'Person'}
KEYPOINT_MAP = {
    0: ('nose', (1, 2,)),
    1: ('l_eye', (3,)),
    2: ('r_eye', (4,)),
    3: ('l_ear', ()),
    4: ('r_ear', ()),
    5: ('l_shoulder', (6, 7, 11,)),
    6: ('r_shoulder', (8, 12,)),
    7: ('l_elbow', (9,)),
    8: ('r_elbow', (10,)),
    9: ('l_wrist', ()),
    10: ('r_wrist', ()),
    11: ('l_hip', (12, 13,)),
    12: ('r_hip', (14,)),
    13: ('l_knee', (15,)),
    14: ('r_knee', (16,)),
    15: ('l_ankle', ()),
    16: ('r_ankle', ()),}


def plot_pose(
        img: np.ndarray,
        preds: List[Results],
        shade: int = 500,
        category_map: Dict[int, str] = CATEGORY_MAP,
        keypoint_map: Dict[int, Tuple[str, List[int]]] = KEYPOINT_MAP,
        box_conf_thres: float = 0.5,
        box_border_thick: int = 1,
        kpts_conf_thres: float = 0.5,
        kpts_radius: int = 2,
        kpts_limbs_thick: int = 1,
    ) -> None:

    def plot_bounding_box(box, color):
        conf = box[5] if len(box) == 7 else box[4]
        if conf < box_conf_thres:
            return
        xyxy = tuple(box[:4].astype(int))
        pt1, pt2 = xyxy[:2], xyxy[2:]
        cv2.rectangle(img, pt1, pt2, color, box_border_thick)
        category = category_map[box[-1]]
        annot = f'{category}, {(conf * 100):.2f}%'
        plot_text(img, annot, pt1, bgcolor=color)

    def plot_keypoints(kpts, color):
        xy = kpts[:, :2].astype(int)
        conf = kpts[:, 2]
        for i in range(len(kpts)):
            if conf[i] < kpts_conf_thres:
                continue
            pt1 = tuple(xy[i])
            for j in keypoint_map[i][1]:
                if conf[j] < kpts_conf_thres:
                    continue
                pt2 = tuple(xy[j])
                cv2.line(img, pt1, pt2, color, kpts_limbs_thick)
            cv2.circle(img, pt1, kpts_radius, color, cv2.FILLED)

    from utils.color import GREEN, ALL_COLORS, hex_to_bgr

    results = preds[0]
    boxes = results.boxes.data.cpu().numpy()
    kptss = results.keypoints.data.cpu().numpy()

    track_on = True if boxes.shape[-1] == 7 else False

    if track_on:
        colors = [hex_to_bgr(color[shade]) for color in ALL_COLORS]
    else:
        colors = [hex_to_bgr(GREEN[shade])]

    for i, (box, kpts) in enumerate(zip(boxes, kptss)):
        color = colors[i % len(colors)] if track_on else colors[0]
        plot_bounding_box(box, color)
        plot_keypoints(kpts, color)


class PoseEstimator(YOLO):

    def __init__(self, model: str = 'yolov8n-pose.pt'):
        super().__init__(model, task=None)

    def estimate(self, img: np.ndarray, track_on: bool = True, **kwargs):
        if track_on:
            return super().track(img, persist=True, **kwargs)
        else:
            return super().predict(img, **kwargs)
