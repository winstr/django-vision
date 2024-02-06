import cv2


class FrameSkipper():

    def __init__(self, interval: int):
        if not isinstance(interval, int) or interval <= 1:
            err = ('The interval value must be a positive integer '
                  f'greater than 1, but input is {interval}.')
            raise ValueError(err)

        self._interval = interval
        self._pos = 0

    def is_skip(self) -> bool:
        skip = bool(self._pos % self._interval)
        if self._pos >= self._interval - 1:
            self._pos = 0
        else:
            self._pos = self._pos + 1
        return skip


class FrameCapture(cv2.VideoCapture):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stopped_iteration = False

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def __len__(self):
        if self.frame_count < 0:
            raise TypeError(
                'Video source does not support random access.')
        return int(self.frame_count)

    def __getitem__(self, i):
        if 0 <= i < len(self):
            self.set(cv2.CAP_PROP_POS_FRAMES, i)
        elif -len(self) <= i < 0:
            self.set(cv2.CAP_PROP_POS_FRAMES, len(self)+i)
        else:
            msg = f'Index {i} out of range.'
            raise IndexError(msg)

        is_captured, frame = self.read()
        if not is_captured:
            msg = f'Could not read frame {i}.'
            raise RuntimeError(msg)
        return frame

    def __iter__(self):
        return self

    def __next__(self):
        def stop_iteration():
            self._stopped_iteration = True
            raise StopIteration

        if not self.isOpened():
            stop_iteration()

        is_captured, frame = self.read()
        if is_captured and not self._stopped_iteration:
            return frame
        else:
            stop_iteration()
