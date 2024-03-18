from typing import Iterable, Tuple, Dict, List

import cv2
import numpy as np


def plot_text(
        img: np.ndarray,
        txt: str,
        org: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 255),
        scale: float = 0.5,
        style: int = cv2.FONT_HERSHEY_SIMPLEX,
        thick: int = 1,
        bgcolor: Tuple[int, int, int] = None
    ) -> None:
    """
    입력 이미지에 텍스트를 표시한다.

    Args:
        - img: 텍스트가 표시될 이미지.
        - txt: 텍스트 내용.
        - org: 2차원 평면에서의 텍스트 좌하단 좌표.

               예시)
               ┌──────────────┐
               │ text content │
               x──────────────┘
               ↑ org

        - color: 텍스트 색상. RGB(or BGR)888.
        - scale: 텍스트 스케일.
        - style: 텍스트 스타일.
        - thick: 텍스트 두께.
        - bgcolor: 텍스트 백그라운드 색상. RGB(or BGR)888.        
    """

    (txt_width, txt_height), _ = cv2.getTextSize(txt,
                                                 style,
                                                 scale,
                                                 thick)

    if bgcolor is not None:
        x, y = org
        pt1 = (x, y - txt_height) 
        pt2 = (x + txt_width, y)
        cv2.rectangle(img, pt1, pt2, bgcolor, cv2.FILLED)

    cv2.putText(
        img,
        txt,
        org,
        style,
        scale,
        color,
        thick)


def plot_bounding_box(
        img: np.ndarray,
        xyxy: Tuple[int, int, int, int],
        color: Tuple[int, int, int],
        border_thick: int = 1,
        label: str = None
    ) -> None:

    """
    입력 이미지에 바운딩 박스를 표시한다.

    Args:
        - img: 바운딩 박스가 표시될 입력 이미지.
        - xyxy: 바운딩 박스 좌상단, 우하단 좌표.
                (min_x, min_y, max_x, max_y)

                예시)
                ↓ min_x, min_y                
                x──────────────┐
                │ bounding box │
                └──────────────x
                  max_x, max_y ↑

        - color: 바운딩 박스 색상. RGB(or BGR)888.
        - border_thick: 바운딩 박스의 경계선 두께.
        - label: 바운딩 박스 상단에 표시될 텍스트. 만약
                 이 값이 None 이라면 텍스트를 표시하지
                 않는다.

                 예시)
                ┌────────────┐
                │ label text │
                ├────────────┴─┐
                │ bounding box │
                └──────────────┘
    """

    if not isinstance(xyxy, np.ndarray):
        xyxy = np.array(xyxy)

    if xyxy.shape[-1] != 4:
        msg = ('Expected colums of the xyxy is 4,'
               ' but a different value was provided.'
               f':{xyxy.shape[-1]}')
        raise ValueError(msg)
    
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


def plot_keypoints(
        img: np.ndarray,
        kpts: Iterable[Tuple[int, int, float]],
        color: Tuple[int, int, int],
        schema: Dict[int, List[int]],
        conf_thres: float = 0.5,
        limb_thick: int = 1
    ) -> None:

    """
    입력 이미지에 키포인트들을 표시한다. 각 키포인트는
    스키마에 표현된 연결 관계에 따라 다른 키포인트들과
    서로 연결된다.

    Args:
        - img: 키포인트들이 표시될 입력 이미지.
        - kpts: 키포인트 정보를 담은 배열. 키포인트
                정보는 2차원 평명에서의 좌표 x, y,
                그리고 confidence 점수로 구성됨.

                예시)
                kpts = [
                    (120, 150, 0.758..),
                    (110, 175, 0.952..),
                    (101, 122, 0.876..),
                    ...
                ]

        - color: 키포인트 색상. RGB(or BGR)888.
        - schema: 키포인트들의 연결 관계를 표현하는
                  사전. 연결은 점과 점을 잇는 선분
                  을 의미하며, 키(key)는 시작점의
                  키포인트 index를, 값(value)은
                  끝점 키포인트들의  index 배열을
                  의미.

                  예시)
                  schema = {
                      0: [1, 2,],
                      1: [3,],
                      2: [4,],
                      3: [],
                      4: [],
                      5: [6, 7, 11,],
                      ...
                  }

        - conf_thres: confidence 점수 하한선.
        - limb_thick: 연결선의 두께.
    """

    if not isinstance(kpts, np.ndarray):
        kpts = np.array(kpts, dtype=float)

    if kpts.ndim != 2:
        msg = ('Expected dimension of the kpts is 2,'
               ' but a different value was provided.'
               f':{kpts.ndim}')
        raise ValueError(msg)

    if kpts.shape[-1] != 3:
        msg = ('Expected colums of the kpts is 3,'
               ' but a different value was provided.'
               f':{kpts.shape[-1]}')
        raise ValueError(msg)
    
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
