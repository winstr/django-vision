import cv2
import numpy as np

from lib.plot.skeleton import EDGE_MAP


def plot_box(img, box, color, thickness=1):
    """
    입력 이미지 img에 바운딩 박스 box를 그린다. box shape은 
    (7,)이며 데이터는 x_min, y_min, x_max, y_max, box_id, 
    category_id, conf 순으로 구성된다.
    Args:
        img (numpy.ndarray): 입력 이미지.
        box (numpy.ndarray): 바운딩 박스.
        color (Tuple[int, int, int]): RGB 컬러 코드.
        thickness (int=1): 바운딩 박스 경계선의 두께.

    Returns:
        없음
    """
    xyxy = tuple(box[:4].astype(np.int32))
    #box_id = int(box[4])
    #category_id = int(box[5])
    #conf = box[6]
    cv2.rectangle(img, xyxy[:2], xyxy[2:], color, thickness)


def plot_kpts(img, kpts, color, thickness=1, conf_thres=0.5):
    """
    입력 이미지 img에 관절 묶음 kpts를 그린다. kpts shape은 
    (17, 3)이며, 행은 코, 왼쪽눈, 오른쪽눈, ... 등 17가지 신체 
    부위에 대한 데이터 포인트를, 열은 x, y, conf 순으로 구성된다.
    어떤 관절의 conf 값이 컨피던스 임계값 conf_thres 미만일 때,
    제대로 탐지되지 않은 것으로 판단하여 해당 관절은 그리지 않는다.

    Args:
        img (numpy.ndarray): 입력 이미지.
        kpts (numpy.ndarray): 관절(키포인트) 묶음.
        color (Tuple[int, int, int]): RGB 컬러 코드.
        thickness (int=1): 관절 및 뼈대(엣지) 경계선의 두께.
        threshold (float=0.5): 컨피던스 임계값.

    Returns:
        없음
    """
    kpts_xy = kpts[:, :2].astype(np.int32)
    kpts_conf = kpts[:, 2]
    for i in range(len(kpts)):
        if kpts_conf[i] < conf_thres:
            continue
        i_xy = tuple(kpts_xy[i])
        for j in EDGE_MAP[i]:
            if kpts_conf[j] < conf_thres:
                continue
            j_xy = tuple(kpts_xy[j])
            cv2.line(img, i_xy, j_xy, color, thickness)
        cv2.circle(img, i_xy, thickness, color, -1)


def plot_textbox(img, text, text_org, box_color, font_color):
    """
    입력 이미지 img에 텍스트 박스를 그린다. 폰트 스케일, 두께, 스타일은
    임의로 하드코딩 되어 있다. (추후 수정 필요)

    Args:
        img (numpy.ndarray): 입력 이미지.
        text (str): 텍스트.
        text_org (Tuple[int, int]): 텍스트가 위치할 좌표.
        box_color (Tuple[int, int, int]): 박스 RGB 컬러 코드.
        font_color (Tuple[int, int, int]): 폰트 RGB 컬러 코드.

    Returns:
        없음
    """
    scale = 0.5                         # 폰트 스케일
    thick = 1                           # 폰트 두께
    style = cv2.FONT_HERSHEY_SIMPLEX    # 폰트 스타일
    (width, height), _ = cv2.getTextSize(text, style, scale, thick)

    x, y = text_org
    x_, y_ = x + width, y + height

    cv2.rectangle(img, (x, y), (x_, y_), box_color, cv2.FILLED)
    cv2.putText(img, text, (x, y_), style, scale, font_color, thick)
