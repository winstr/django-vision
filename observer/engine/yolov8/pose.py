from typing import Tuple, List, Any

import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from observer.utils.plotting import plot_text


def plot_box(
        img: np.ndarray,
        box: np.ndarray,
        box_color: Tuple[int, int, int],
        box_thickness: int = 1,
        box_conf_thres: float = 0.5,
        category_map: dict = None,
        with_text: bool = True
    ) -> None:
    """ 입력 이미지에 바운딩 박스를 그린다.

        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            box (np.ndarray):
                numpy 배열 형태의 바운딩 박스. shape은 (7,)이며, 요소는
                [x_min, y_min, x_max, y_max, box_id, confidence,
                category_id]이다. 
            box_color (Tuple[int, int, int]): 바운딩 박스 컬러.
            box_thickness (int): 바운딩 박스 경계선 두께.
            box_conf_thres (float): 바운딩 박스 컨피던스 임계값.
            category_map (dict):
                카테고리 ID가 주어졌을 때, 해당 카테고리의 이름을 반환하는
                사전 객체. {key(id: int) : value(name: str), ...}
                형태로 제공되어야 함.
            with_text (bool):
                참일 경우, 텍스트를 추가한다. 텍스트는 카테고리 이름(만약에
                category_map이 주어지지 않았다면 카테고리 ID), 박스 ID,
                컨피던스 스코어(소수점 3자리까지)로 구성된다.

        Returns:
            None
    """
    conf = box[5]
    if conf < box_conf_thres:
        return

    xyxy = tuple(box[:4].astype(int))
    pt1, pt2 = xyxy[:2], xyxy[2:]
    cv2.rectangle(img, pt1, pt2, box_color, box_thickness)

    if with_text:
        bid, cid = int(box[4]), int(box[6])  # box id, category id.
        if category_map is not None:
            cid = category_map[cid]

        text = f'{cid}, {bid}, {conf:.3f}'
        text_color = (0, 0, 0)  # black.
        plot_text(img, text, pt1, text_color, bg_color=box_color)


def plot_pose(
        img: np.ndarray,
        kpts: np.ndarray,
        kpts_color: Tuple[int, int, int],
        kpts_connection_map: dict,
        connection_color: Tuple[int, int, int],
        connection_thickness: int = 1,
        kpts_radius: int = 2,
        kpts_conf_thres: float = 0.5,
    ) -> None:
    """ 입력 이미지에 자세를 그린다.

        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            kpts (np.ndarray):
                numpy 배열 형태의 키포인트 세트. shape은 (17, 3)이고,
                행은 키포인트 부위(nose, left_eye, right_eye 등)이며,
                열은 [x, y, confidence]이다.
            kpts_color (Tuple[int, int, int]): 키포인트 컬러.
            kpts_connection_map (dict):
                어떤 키포인트의 ID가 주어졌을 때, 이 키포인트와 상호 연결된
                키포인트들의 ID 목록을 반환하는 사전 객체. {key(id: int)
                : value(connections: list)} 형태로 제공되어야 함.
            connection_color (Tuple[int, int, int]): 연결선 컬러.
            connection_thickness (int): 연결선 두께.
            kpts_radius (int): 키포인트 반지름.
            kpts_conf_thres (float): 키포인트 컨피던스 임계값.

        Returns:
            None
    """
    xy = kpts[:, :2].astype(int)
    conf = kpts[:, 2]

    for i in range(len(kpts)):
        if conf[i] < kpts_conf_thres:
            continue
        pt1 = tuple(xy[i])

        for j in kpts_connection_map[i]:
            if conf[j] < kpts_conf_thres:
                continue
            pt2 = tuple(xy[j])

            # 모든 연결선(line)을 그린 후 키포인트(circle)를 그리는 순서로 진행한다.
            # 그렇지 않으면 키포인트 위에 연결선이 그려져 시각적으로 보기에 예쁘지 않다.
            cv2.line(img, pt1, pt2, connection_color, connection_thickness)
        cv2.circle(img, pt1, kpts_radius, kpts_color, cv2.FILLED)


class DefaultPose():

    """ Yolov8 자세 클래스. 만약 자세 구성이 다른, 새로운 자세 추정 모델을
        사용해야 한다면, 이 클래스를 상속받아 kpts_connection_map 사전만
        수정하거나, plot(...) 메소드에 다른 kpts_connection_map을 입력
        하면 됨. 인스턴스 생성 불가능.

        Static Attributes:
            kpts_connection_map (dict)

        Static Methods:
            plot(...) -> None
    """

    # 키포인트들의 ID 목록을 반환하는 사전 객체. key는 특정 키포인트 ID를,
    # value는 이 키포인트와 연결된, 다른 키포인트들의 ID 목록을 의미.
    kpts_connection_map = {
        0:  [1, 2],
        1:  [3],
        2:  [4],
        3:  [],
        4:  [],
        5:  [6, 7, 11],
        6:  [8, 12],
        7:  [9],
        8:  [10],
        9:  [],
        10: [],
        11: [12, 13],
        12: [14],
        13: [15],
        14: [16],
        15: [],
        16: []}

    def __init__(self):
        # 인스턴스 생성 불가능.
        raise RuntimeError('instance cannot be created.')

    @staticmethod
    def plot(
            img: np.ndarray,
            preds: List[Results],
            enable_tracking: bool = False,
            color_shade: int = 500,
            kpts_connection_map: dict = kpts_connection_map,
        ) -> None:
        """ 입력 이미지에 모든 객체들의 바운딩 박스와 자세를 그린다.

            Args:
                img (np.ndarray): numpy 배열 형태의 입력 이미지.
                preds (List[Results]): 자세 추정 결과.
                enable_tracking (bool):
                    참일 경우, 바운딩 박스 ID를 이용하여 개별 추적 객체들의 색상을
                    결정한다. 거짓일 경우, 모든 객체들의 색상은 동일한 색으로 통일.
                color_shade (int):
                    컬러 음영값. 낮을 수록 밝은 색. 이 값은 임의로 지정될 수 없고,
                    observer.utils.color.Colors에 정의된 값들만 사용해야 함.
                    [50, 100, 200, 300, 400, 500, 600, 700, 800, 900].
                kpts_connection_map (dict): 키포인트 연결맵.

            Returns:
                None
        """
        from observer.utils.color import Colors

        results = preds[0]
        boxes = results.boxes.data.cpu().numpy()
        kptss = results.keypoints.data.cpu().numpy()

        colors = Colors.to_bgr(Colors.green[color_shade])
        if enable_tracking:
            colors = [color[color_shade] for color in Colors.all_colors]
            colors = [Colors.to_bgr(color) for color in colors]

        for i, (box, kpts) in enumerate(zip(boxes, kptss)):
            color = colors[i % len(colors)] if enable_tracking else colors
            plot_box(img, box, color)
            plot_pose(img, kpts, kpts_connection_map, color, color)


class PoseEstimator(YOLO):

    """ Yolov8 자세 추정기 클래스. """

    def __init__(self, model: str = 'yolov8n-pose.pt'):
        super().__init__(model, task=None)

    def predict(self,
                img: np.ndarray,
                enable_tracking: bool = False,
                **kwargs: List[Any]
        )-> List[Results]:
        """ 입력 이미지에 대하여 자세 추정을 수행.

            Args:
                img (np.ndarray): numpy 배열 형태의 입력 이미지.
                enalbe_tracking (bool): 참일 경우, 추적 활성화.
                **kwargs (List[Any]):
                    키워드 인자값들. 세부 내용은 부모 클래스 소스코드
                    참조. e.g. verbose=False, etc.
            Returns:
                preds (List[Results]): 자세 추정 결과.
        """
        if enable_tracking:
            preds = super().track(img, persist=True, **kwargs)
        else:
            preds = super().predict(img, **kwargs)
        return preds
