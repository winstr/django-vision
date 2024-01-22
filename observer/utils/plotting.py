from typing import Tuple, List

import cv2
import numpy as np


def plot_text(img: np.ndarray,
              text: str,
              text_origin: Tuple[int, int],
              text_color: Tuple[int, int, int],
              text_scale: float = 0.5,
              text_style: int = cv2.FONT_HERSHEY_SIMPLEX,
              text_thickness: int = 1,
              background_color: Tuple[int, int, int] = None
    ) -> None:
    """ 입력 이미지에 텍스트를 그린다.

        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            text (str): 텍스트 내용.
            text_origin (Tuple[int, int]): 텍스트 원점 x, y 좌표(좌상단).
            text_color (Tuple[int, int, int]): 텍스트 컬러.
            text_scale (float): 텍스트 스케일.
            text_style (int): 텍스트 스타일(fontFace).
            text_thickness (int): 텍스트 두께.
            background_color (Tuple[int, int, int]): 배경 컬러.

        Returns:
            None
    """
    # 텍스트의 가로 세로 사이즈를 계산한다.
    (text_width, text_height), _ = cv2.getTextSize(text,
                                                   text_style,
                                                   text_scale,
                                                   text_thickness)

    # 배경 컬러가 주어졌을 경우, 배경(박스)을 채워넣는다.
    if background_color is not None:
        pt1 = text_origin
        pt2 = (pt1[0] + text_width, pt1[1] + text_height)
        cv2.rectangle(img, pt1, pt2, background_color, cv2.FILLED)

    # 텍스트를 띄운다(그린다).
    text_origin = (pt1[0], pt1[1] + text_height)
    cv2.putText(img,
                text,
                text_origin,
                text_style,
                text_scale,
                text_color,
                text_thickness)
