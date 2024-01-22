from typing import Tuple, List, Any

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results


class PoseEstimator(YOLO):

    def __init__(self, model: str = 'yolov8n-pose.pt'):
        """ 초기화.
        ----------
        Args:
            model (str): `yolov8*.pt` 파일의 경로 또는 이름.
        """
        super().__init__(model, task=None)

    def predict(self,
                img: np.ndarray,
                enable_tracking: bool = False,
                **kwargs: List[Any]
        )-> List[Results]:
        """ 입력 이미지에 대하여 자세 추정을 수행.
        -----------------------------------
        Args:
            img (np.ndarray): numpy 배열 형태의 입력 이미지.
            enalbe_tracking (bool): 참일 경우, 추적 활성화.
            **kwargs (List[Any]): 키워드 인자값들.
        Returns:
            preds (List[Results]): 예측 결과.
        """
        if enable_tracking:
            preds = super().track(img, persist=True, **kwargs)
        else:
            preds = super().predict(img, **kwargs)
        return preds
