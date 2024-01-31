from typing import Tuple, Dict, List

import cv2
import numpy as np


def plot_text(
        img: np.ndarray,
        text: str,
        text_org: Tuple[int, int],
        text_color: Tuple[int, int, int] = (255, 255, 255),
        text_scale: float = 0.5,
        text_style: int = cv2.FONT_HERSHEY_SIMPLEX,
        text_thickness: int = 1,
        bgcolor: Tuple[int, int, int] = None
    ) -> None:

    (text_width, text_height), _ = cv2.getTextSize(
        text, text_style, text_scale, text_thickness)

    if bgcolor is not None:
        x, y = text_org
        pt1 = (x, y - text_height) 
        pt2 = (x + text_width, y)
        cv2.rectangle(img, pt1, pt2, bgcolor, cv2.FILLED)

    cv2.putText(
        img,
        text,
        text_org,
        text_style,
        text_scale,
        text_color,
        text_thickness)
