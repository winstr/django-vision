import cv2


class VideoFrameSkipper():

    """ 스킵 간격에 따라 프레임의 스킵 여부를 판단/반환하는 반복자(iterable) 클래스.
        ---------------------------------------------------------------
        스킵 간격이 3일 경우, 인스턴스는 이 길이 만큼의 튜플[True, True, False]을
        생성하고, 현재 프레임의 위치에 따라 스킵 여부를 반환한다.

        현재 프레임 위치는 next()가 호출될 때마다 자동으로 1씩 증가하며, 프레임 스킵
        특성(반복적)상 next()는 StopIteration 예외를 발생시키지 않는다.
    """

    def __init__(self, skip_interval: int):
        """ 초기화.
        ----------
        Args:
            skip_interval (int): 스킵 간격 -> unsigned int.
        """
        if not isinstance(skip_interval, int) or skip_interval <= 0:
            msg = 'The skip_interval must be a positive integer.'
            raise ValueError(msg)
        self._skip_interval = skip_interval
        self._skip_states = tuple([False] + [True] * (skip_interval - 1))
        self._position = 0

    def __len__(self):
        return len(self._skip_states)

    def __next__(self):
        if self._position >= len(self):
            # StopIteration을 발생시키지 않는 대신, 현재 프레임
            # 위치를 0으로 되돌려 놓는다.
            self._position = 0
        is_skip = self._skip_states[self._position]
        self._position += 1
        return is_skip

    def __iter__(self):
        return self

    def __repr__(self):
        return f'FrameSkipper(skip_interval={self._skip_interval})'


class VideoCapture(cv2.VideoCapture):

    """ 비디오 캡처 클래스.
        ---------------
        반복자(iterable)로 동작하며, with 구문과 함께 사용할 수 있도록 하였다.
    """

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
            msg = 'VideoCapture source does not support random access.'
            raise TypeError(msg)
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
