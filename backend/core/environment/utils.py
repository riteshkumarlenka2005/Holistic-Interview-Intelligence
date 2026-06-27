from collections import deque
import statistics
import time

class RollingAverage:
    def __init__(self, window_size_seconds: float = 30.0):
        self.window_size_seconds = window_size_seconds
        # Stores tuples of (timestamp, value)
        self.data = deque()
        
    def add(self, value: float):
        now = time.time()
        self.data.append((now, value))
        self._prune(now)
        
    def get_average(self) -> float:
        now = time.time()
        self._prune(now)
        if not self.data:
            return 0.0
        return statistics.mean(v for _, v in self.data)
        
    def _prune(self, current_time: float):
        while self.data and current_time - self.data[0][0] > self.window_size_seconds:
            self.data.popleft()
