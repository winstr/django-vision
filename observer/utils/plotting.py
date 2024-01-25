from typing import Tuple, List

import cv2
import numpy as np


def plot_text(img: np.ndarray,
              txt: str,
              org: Tuple[int, int],
              color: Tuple[int, int, int],
              scale: float = 0.5,
              style: int = cv2.FONT_HERSHEY_SIMPLEX,
              thick: int = 1,
              bgcolor: Tuple[int, int, int] = None
    ) -> None:

    """ 입력 이미지에 텍스트를 그린다.

        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            txt (str): 텍스트 내용.
            org (Tuple[int, int]): 텍스트 원점 x, y 좌표(좌상단).
            color (Tuple[int, int, int]): 텍스트 컬러.
            scale (float): 텍스트 스케일.
            style (int): 텍스트 스타일(fontFace).
            thick (int): 텍스트 두께.
            bgcolor (Tuple[int, int, int]): 배경 컬러.

        Returns:
            None
    """

    # 텍스트의 가로 세로 사이즈를 계산한다.
    (text_width, text_height), _ = cv2.getTextSize(txt, style, scale, thick)

    # 배경 컬러가 주어졌을 경우, 배경(박스)을 채워넣는다.
    if bgcolor is not None:
        pt1 = org
        pt2 = (pt1[0] + text_width, pt1[1] + text_height)
        cv2.rectangle(img, pt1, pt2, bgcolor, cv2.FILLED)

    # 텍스트를 띄운다(그린다).
    org = (org[0], org[1] + text_height)
    cv2.putText(img, txt, org, style, scale, color, thick)
