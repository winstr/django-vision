import time
from typing import Iterable


class Timer():

    def __init__(self) -> None:
        self.start_time = time.time()

    def get_elapsed_time(self) -> str:
        elapsed_time = time.time() - self.start_time
        h, r = divmod(elapsed_time, 3600)  # hours, remainders
        m, s = divmod(r, 60)               # minutes, seconds
        return f'{int(h):02}:{int(m):02}:{int(s):02}'


class TimerManager():

    def __init__(self):
        self.timers_id = set()
        self.timers = {}

    def syncronize(self, timers_id: Iterable[int]):
        timers_id = set(timers_id)
        for timer_id in self.timers_id - timers_id:
            del self.timers[timer_id]
        for timer_id in timers_id - self.timers_id:
            self.timers[timer_id] = Timer()
        self.timers_id = timers_id
