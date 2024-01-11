from typing import List

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from lib.plot.plot import plot_box, plot_kpts
from lib.plot.colors import COLORS


class PoseEstimator(YOLO):

    def __init__(self, model='yolov8n-pose.pt'):
        super().__init__(model, task=None)

    def estimate(self, img:np.ndarray, enable_tracking:bool=False, **kwargs) -> List[Results]:
        if enable_tracking:
            results = super().track(img, persist=True, **kwargs)
        else:
            results = super().predict(img, **kwargs)
        return results

    @staticmethod
    def visualize(results: List[Results]) -> np.ndarray:
        img = results[0].orig_img
        boxes = results[0].boxes.data.cpu().numpy()
        kptss = results[0].keypoints.data.cpu().numpy()
        for i, (box, kpts) in enumerate(zip(boxes, kptss)):
            color = COLORS[len(kpts)%(i+1)]
            plot_box(img, box, color, 1)
            plot_kpts(img, kpts, color, 1)
        return img