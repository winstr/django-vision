from typing import Tuple, Dict, List, Any

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from observer.utils.plotting import plot_text


def plot_box(
        img: np.ndarray,
        box: np.ndarray,
        color: Tuple[int, int, int],
        thick: int = 1,
        thres: float = 0.5,
        lbmap: Dict[int, str] = None,
        annot_on: bool = True,
    ) -> None:

    """ 입력 이미지에 바운딩 박스를 그린다.

    Args:
        img (np.ndarray): numpy 배열 입력 이미지.
        box (np.ndarray): numpy 배열 바운딩 박스.
            아래 두 가지 box 구성 중 하나를 반드시 만족해야 함(차이: box_id의 유무).
            1) [x_min, y_min, x_max, y_max, box_id, confidence, label_id]
            2) [x_min, y_min, x_max, y_max, confidence, label_id]
        color (Tuple[int, int, int]): 바운딩 박스 BGR 색상 코드.
        thick (int): 바운딩 박스 경계선 두께.
        thres (float): 바운딩 박스 컨피던스 임계값. 임계값 미만의 박스는 그리지 않음.
        lbmap (Dict[int, str]): 레이블 맵. 키는 레이블 ID, 값은 레이블 이름.
        annot_on (bool): 참인 경우, 텍스트(카테고리, 컨피던스 등)를 박스위에 추가함.

    Returns:
        None
    """

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


def plot_pose(
        img: np.ndarray,
        kpts: np.ndarray,
        color: Tuple[int, int, int],
        cnmap: Dict[int, List[int]],
        thick: int = 1,
        radius: int = 2,
        thres: float = 0.5,
    ) -> None:

    """ 입력 이미지에 자세(pose)를 그린다.

    Args:
        img (np.ndarray): numpy 배열 형태의 입력 이미지.
        kpts (np.ndarray): numpy 배열 형태의 키포인트 세트.
            행은 키포인트 부위(nose, left_eye, right_eye 등)이며,
            열은 [x, y, confidence]임. 열 구성은 반드시 지켜야 함.
        color (Tuple[int, int, int]): 자세 BGR 색상 코드.
        cnmap (Dict[int, List[int]]): 키포인트 연결맵.
            키는 시작점 키포인트 ID, 값은 끝점 키포인트들의 ID 목록.
        thick (int): 키포인트 연결선 두께.
        radius (int): 키포인트 반지름.
        thres (float): 키포인트 컨피던스 임계값.

    Returns:
        None
    """

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


class DefaultPose():

    """ Yolov8 자세 클래스. """

    default_cnmap = {
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

    default_lbmap = {
        0: 'Person'
    }

    def __init__(self):
        # 인스턴스 생성 불가능.
        raise RuntimeError('instance cannot be created.')

    @staticmethod
    def plot(
            img: np.ndarray,
            preds: List[Results],
            cnmap: dict = default_cnmap,
            lbmap: dict = default_lbmap,
            shade: int = 500,
            track_on: bool = False,
            box_thres: float = 0.5,
            kpts_thres: float = 0.5
        ) -> None:

        """ 입력 이미지에 모든 객체들의 바운딩 박스와 자세를 그림.

        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            preds (List[Results]): 자세 추정 결과.
            cnmap (Dict[int, List[int]]): 키포인트 연결맵.
                키는 시작점 키포인트 ID, 값은 끝점 키포인트들의 ID 목록.
            lbmap (Dict[int, str]): 레이블 맵.
                키는 레이블 ID, 값은 레이블 이름.
            shade (int):
                색상 음영값. 낮을수록 밝은 색. 이 값은 임의로 지정될 수 없고,
                observer.utils.color.Colors에 정의된 값들만 사용 가능.
                [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
            track_on (bool): 참일 경우, 객체들의 색상 표현이 달라짐.

        Returns:
            None
        """

        from observer.utils.color import Colors

        results = preds[0]
        boxes = results.boxes.data.cpu().numpy()
        kptss = results.keypoints.data.cpu().numpy()

        colors = Colors.to_bgr(Colors.green[shade])
        if track_on:
            colors = [color[shade] for color in Colors.all_colors]
            colors = [Colors.to_bgr(color) for color in colors]

        for i, (box, kpts) in enumerate(zip(boxes, kptss)):
            color = colors[i % len(colors)] if track_on else colors
            plot_box(img, box, color, thres=box_thres, lbmap=lbmap)
            plot_pose(img, kpts, color, cnmap, thres=kpts_thres)


class PoseEstimator(YOLO):

    """ Yolov8 자세 추정기 클래스. """

    def __init__(self, model: str = 'yolov8n-pose.pt'):
        super().__init__(model, task=None)

    # TODO
