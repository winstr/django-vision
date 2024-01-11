from typing import Union, Callable

import cv2
import numpy as np


class VideoStreamer():

    def __init__(self, video_source: Union[int, str], preproc_func: Callable):
        self._src = video_source
        self._cap = None
        self._fps = None

        self._preproc_func = preproc_func
        self._grabbed = False

        self.build()

    def build(self):
        self._cap = cv2.VideoCapture(self._src)
        if not self._cap.isOpened():
            raise RuntimeError('Failed to open the video source.')
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)

    def release(self):
        self._cap.release()

    def grab(self):
        self._grabbed = self._cap.grab()

    def _preproc(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            frame = func(*args, **kwargs)
            frame = self._preproc_func(frame)
            return frame
        return wrapper

    @_preproc
    def retrieve(self) -> np.ndarray:
        if not self._grabbed:
            raise RuntimeError(f'Failed to grab the next frame.')
        self._grabbed = False
        captured, frame = self._cap.retrieve()
        if not captured:
            raise RuntimeError(f'Failed to read the next frame.')
        return frame

    @_preproc
    def read(self) -> np.ndarray:
        captured, frame = self._cap.read()
        if not captured:
            raise RuntimeError(f'Failed to read the next frame.')
        return frame
