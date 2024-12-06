import heapq


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.storage = {}
        self.time_to_key = {}
        self.key_to_time = {}
        self.latest = 0

    def update_times(self, key):
        if key in self.key_to_time:
            old_time = self.key_to_time[key]
            del self.key_to_time[key]
            del self.time_to_key[old_time]
        self.key_to_time[key] = self.latest
        self.time_to_key[self.latest] = key
        self.latest += 1

    def get(self, key: int) -> int:
        if key in self.storage:
            self.update_times(key)
            return self.storage[key]
        return -1

    def put(self, key: int, value: int) -> None:
        self.storage[key] = value
        self.update_times(key)

        if len(self.storage) > self.capacity:
            oldest_time = min(self.time_to_key)
            oldest_key = self.time_to_key[oldest_time]
            del self.time_to_key[oldest_time]
            del self.key_to_time[oldest_key]
            del self.storage[oldest_key]
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)