#from typing import Tuple, Dict, List
#import cv2
#import numpy as np
#from utils.plotting import plot_text
DEAFAULT_SCHEMA = {
    0: [1, 2,],
    1: [3,],
    2: [4,],
    3: [],
    4: [],
    5: [6, 7, 11,],
    6: [8, 12,],
    7: [9,],
    8: [10,],
    9: [],
    10: [],
    11: [12, 13,],
    12: [14,],
    13: [15,],
    14: [16,],
    15: [],
    16: [],
}
'''
def plot_bounding_box(
        img: np.ndarray,
        xyxy: np.ndarray,
        color: Tuple[int, int, int],
        border_thick: int = 1,
        label: str = None
    ) -> None:

    xyxy = tuple(xyxy.astype(int))
    pt1, pt2 = xyxy[:2], xyxy[2:]
    cv2.rectangle(img,
                  pt1,
                  pt2,
                  color,
                  border_thick)

    if label is not None:
        plot_text(img,
                  label,
                  pt1,
                  bgcolor=color)

def plot_skeleton(
        img: np.ndarray,
        kpts: np.ndarray,
        color: Tuple[int, int, int],
        schema: Dict[int, List[int]] = DEAFAULT_SCHEMA,
        conf_thres: float = 0.5,
        limb_thick: int = 1
    ) -> None:

    pt = kpts[:, :2].astype(int)
    conf = kpts[:, 2]

    for i in range(len(kpts)):
        if conf[i] < conf_thres:
            continue
        pt1 = tuple(pt[i])

        for j in schema[i]:
            if conf[j] < conf_thres:
                continue
            pt2 = tuple(pt[j])

            cv2.line(img,
                     pt1,
                     pt2,
                     color,
                     limb_thick)
'''