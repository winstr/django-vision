import cv2


class SkipFlags():

    def __init__(self, interval: int):
        if not isinstance(interval, int) or interval <= 1:
            raise ValueError(
                'Interval must be an interger and greater than 1.')
        self._interval = interval
        self._flags = tuple([False] + [True] * (interval - 1))
        self._pos = 0

    def __len__(self):
        return len(self._flags)

    def __next__(self):
        if self._pos >= len(self):
            self._pos = 0
        is_skip = self._flags[self._pos]
        self._pos += 1
        return is_skip

    def __iter__(self):
        return self

    def __repr__(self):
        return f'SkipFlags(interval={self._interval})'


class VideoCapture(cv2.VideoCapture):

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
