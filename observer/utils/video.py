import cv2


class VideoFrameSkipper():

    """ 비디오 프레임 스킵 클래스. 설정된 스킵 간격을 기준으로, 스킵 상태 관리를
        위한 불리언 튜플을 만들고, 현재 프레임 위치에 따라 그 값을 반환한다.

        예를 들어, skip_interval=3은 스킵 간격을 3으로 설정하겠다는 의미이며,
        3의 배수에 해당하는 프레임이 아닌 나머지 프레임은 모두 무시한다는 뜻이다.
        즉, 스킵 상태 튜플은 [True, True, False]가 된다.
        
        비디오 프레임 스킵 인스턴스는 내장 함수 __next__가 호출될 때마다 자동으로
        1씩 증가하는 self._position 을 통해 현재 프레임의 스킵 상태를 탐색하고,
        그 값을 반환한다.

        비전 AI 분야에서, 프레임 스킵은 연산 자원 절감 및 최적화에 반드시 필요하다.
        cv2.VideoCapture(...)와 pytorch model과 함께, 아래와 같이 사용할 수
        있다.

        Usage:

            예시 1)
            ----------------------------------------------
            cap = cv2.VideoCapture(video_source)
            assert cap.isOpened(), 'open error.'
            skipper = VideoFrameSkipper(3)  # 간격 초기화

            while True:
                is_captured, frame = cap.read()
                assert is_captured, 'read error.'
                is_skip = next(skipper)  # 스킵 여부 가져오기
                if not is_skip:
                    preds = torch_model.predict(frame, ...)
                ...

            cap.release()
    """

    def __init__(self, skip_interval: int):
        """
        Args:
            skip_interval (int): 스킵 간격
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
            # StopIteration을 발생시키지 않고 현재 프레임 위치를 0으로 되돌려 놓음.
            self._position = 0
        is_skip = self._skip_states[self._position]
        self._position += 1
        return is_skip

    def __iter__(self):
        return self

    def __repr__(self):
        return f'FrameSkipper(skip_interval={self._skip_interval})'


class VideoCapture(cv2.VideoCapture):

    """ 비디오 캡처 클래스. with 구문을 통해 release() 호출을 보장하며,
        반복자 형태로 재구성하여 편의성을 높였다.

        Usage:

            예시 1)
            -------------------------------------------------
            with VideoCapture(video_source) as cap:
                for frame in cap:
                    preds = pytorch_model.predict(frame, ...)
            ...

            예시 2) VideoFrameSkipper(...)와 함께 사용
            -----------------------------------------------------
            with VideoCapture(video_source) as cap:
                skipper = VideoFrameSkipper(3)
                for frame in cap:
                    is_skip = next(skipper)
                    if not is_skip:
                        preds = pytorch_model.predict(frame, ...)
            ...
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
