class StepSkipper():

    """ 반복적 작업에 대하여, 단위 간격을 기준으로 현재 동작의 스킵
        여부를 결정합니다. 예를 들어 단위 간격이 3일 때 다음과 같은
        스킵 시퀀스를 떠올릴 수 있습니다.

        >>> skip_sequence = [False, True, True]

        이 시퀀스는 매 반복마다 다음과 같이 현재 동작의 스킵 여부를
        결정합니다.

        >>> for item in items:
        >>>     skip = next(skip_sequence)
        >>>     if skip:
        >>>         continue
        >>>     task(item)

        이 때 단위 간격의 첫 번째 요소는 스킵하지 않으며, 그 이외의
        요소들은 스킵한다는 점에 주목하세요. 만약 단위 간격이 5라면,
        skip_sequence는 아래와 같을 것입니다.

        >>> skip_sequence = [False, True, True, True, True]

        사실 skip_sequence는, 이 클래스의 메커니즘을 설명하기 위한,
        가상의 자료입니다. 실제로 인스턴스는 스킵 플래그를 관리하는
        명시적인 자료를 선언하지 않습니다. 이는 단위 간격이 매우 클
        경우 시퀀스가 차지하는 메모리 또한 커진다는 문제를 해결하기
        위함입니다. 대신, 인스턴스는 아래와 같이 스킵 플래그를 반환
        합니다.

        >>> return bool(self._position % self._step)

        여기서 self._position은 가상의 skip_sequence 안의 현재 스킵
        플래그의 위치를 가리키는 인덱스입니다. 이 인덱스는 0을 포함
        하는 양의 정수이며, 범위는 0 ~ (단위간격 - 1) 입니다. 만약,
        단위 간격이 5라면 인덱스가 가질 수 있는 범위는 0 ~ 4 입니다.
        self._step은 단위 간격의 크기입니다. 결과적으로 위 반환문은
        나머지가 0인 경우 False, 그 이외의 경우 True를 반환합니다.

        self._position은 인스턴스 메서드 move_position()을 호출하여
        1씩 명시적으로 증가시킬수 있습니다. 이 함수는 Iterable 객체
        의 next()를 호출하는 효과와 유사한 동작을 수행하지만 마지막
        인덱스에서 StopIteration 예외를 발생시키지는 않습니다. 대신
        self._position을 0으로 초기화시켜, 다시 처음으로 돌아가도록
        만듭니다. 이는 반복 횟수를 알 수 없는 작업에서, 스킵 로직이
        필요한 상황에 유용합니다.

        >>> skipper = StepSkipper(step=5)
        >>> while True:
        >>>     skip = skipper.is_skip()
        >>>     skipper.move_position()
        >>>     if skip:
        >>>         continue
        >>>     # Todo
        >>>     ....

        예를 들어, 카메라로부터 전송되는 연속된 프레임에 대해, 지능
        모델 기반 실시간 처리를 위해 아래와 같이 사용될 수 있습니다.

        >>> import cv2
        >>> ...
        >>> cap = cv2.VideoCapture(...)
        >>> if not cap.isOpened():
        >>>     raise ...
        >>> ...
        >>> try:
        >>>     model = ...
        >>>     skipper = StepSkipper(step=3)
        >>>     while True:
        >>>         cap.grab()
        >>>         ...
        >>>         skip = skipper.is_skip()
        >>>         skipper.move_position()
        >>>         if skip:
        >>>             continue
        >>>         ...
        >>>         is_grab, frame = cap.retrieve()
        >>>         if not is_grab:
        >>>             raise ...
        >>>         preds = model.predict(frame)
        >>>         ...
        >>> except:
        >>>     ...
        >>> cap.release()
    """

    def __init__(self, step: int) -> None:
        self._step = step
        self._position = 0

    @property
    def step(self) -> int:
        return self._step

    @step.setter
    def step(self, step: int) -> None:
        if step < 2 or not isinstance(step, int):
            msg = "The 'step' must be a positive interger greater than 1."
            raise ValueError(msg)
        self._step = step

    def move_position(self) -> None:
        if self._position >= self._step:
            self._position = 0
        else:
            self._position = self._position + 1

    def is_skip(self) -> bool:
        return bool(self._position % self._step)
