import time
from typing import Tuple, Dict, List

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from observer.utils.plotting import plot_text


DEFAULT_CNMAP = {
    0: [1, 2],
    1: [3],
    2: [4],
    3: [],
    4: [],
    5: [6, 7, 11],
    6: [8, 12],
    7: [9],
    8: [10],
    9: [],
    10: [],
    11: [12, 13],
    12: [14],
    13: [15],
    14: [16],
    15: [],
    16: []
}

DEFAULT_LBMAP = {
    0: 'Person'
}


def _plot_box(
        img: np.ndarray,
        box: np.ndarray,
        color: Tuple[int, int, int],
        thick: int = 1,
        thres: float = 0.5,
        lbmap: Dict[int, str] = None,
        annot_on: bool = True,
    ) -> None:

    conf = box[5] if len(box) == 7 else box[4]
    if conf < thres:
        return

    xyxy = tuple(box[:4].astype(int))
    pt1, pt2 = xyxy[:2], xyxy[2:]
    cv2.rectangle(img, pt1, pt2, color, thick)

    if not annot_on:
        return

    box_id = box[4] if len(box) == 7 else 0

    label_id = box[-1]
    if lbmap is not None:
        label_id = lbmap[label_id]

    annot = f'{label_id}, {box_id}, {conf:.2f}'
    plot_text(img, annot, pt1, (0, 0, 0), bgcolor=color)


def _plot_kpts(
        img: np.ndarray,
        kpts: np.ndarray,
        color: Tuple[int, int, int],
        cnmap: Dict[int, List[int]],
        thick: int = 1,
        radius: int = 2,
        thres: float = 0.5,
    ) -> None:

    xy = kpts[:, :2].astype(int)
    conf = kpts[:, 2]

    for i in range(len(kpts)):
        if conf[i] < thres:
            continue
        pt1 = tuple(xy[i])

        for j in cnmap[i]:
            if conf[j] < thres:
                continue
            pt2 = tuple(xy[j])

            cv2.line(img, pt1, pt2, color, thick)
        cv2.circle(img, pt1, radius, color, cv2.FILLED)


def plot_pose(
        img: np.ndarray,
        preds: List[Results],
        cnmap: dict = DEFAULT_CNMAP,
        lbmap: dict = DEFAULT_LBMAP,
        shade: int = 500,
        box_thres: float = 0.5,
        kpts_thres: float = 0.5
    ) -> None:

    from observer.utils.color import Colors

    results = preds[0]
    boxes = results.boxes.data.cpu().numpy()
    kptss = results.keypoints.data.cpu().numpy()

    n_cols = boxes.shape[-1]
    if n_cols == 7:
        track_on = True
    elif n_cols == 6:
        track_on = False
    else:
        raise RuntimeError()

    colors = [Colors.to_bgr(Colors.green[shade])]
    if track_on:
        colors = [color[shade] for color in Colors.all_colors]
        colors = [Colors.to_bgr(color) for color in colors]

    for i, (box, kpts) in enumerate(zip(boxes, kptss)):
        color = colors[i % len(colors)] if track_on else colors
        _plot_box(img, box, color, thres=box_thres, lbmap=lbmap)
        _plot_kpts(img, kpts, color, cnmap, thres=kpts_thres)


class PoseEstimator(YOLO):

    def __init__(self, model: str = 'yolov8n-pose.pt'):
        super().__init__(model, task=None)

    def estimate(self, img: np.ndarray, track_on: bool, **kwargs):
        if track_on:
            return super().track(img, persist=True, **kwargs)
        else:
            return super().predict(img, **kwargs)
