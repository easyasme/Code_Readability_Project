import time


class LRUCache:

    def __init__(self, capacity: int):
        self.lru_cache = {} # key: value, timestamp
        self.capacity = capacity
        # self.oldest = float("+infinity")
        self.lru_times = {} # timestamp: key

    def get(self, key: int) -> int:
        epoch_time = time.time()
        if key in self.lru_cache:
            val, ts = self.lru_cache[key]
            self.lru_cache[key] = (val, epoch_time)
            self.lru_times[epoch_time] = key
            del self.lru_times[ts]
            return self.lru_cache[key][0]
        return -1

    def put(self, key: int, value: int) -> None:
        epoch_time = time.time()
        if key in self.lru_cache:
            old_time = self.lru_cache[key][1]
            del self.lru_times[old_time]
        self.lru_cache[key] = (value, epoch_time)
        self.lru_times[epoch_time] = key
        if len(self.lru_cache) > self.capacity:
            oldest_time = min(self.lru_times.keys())
            oldest_key = self.lru_times[oldest_time]
            del self.lru_times[oldest_time]
            del self.lru_cache[oldest_key]
