class LRUCache:

    def __init__(self, capacity: int):
        self.cache = {}
        self.recently_used = []
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key in self.cache:
            self.recently_used.pop(self.recently_used.index(key))
            self.recently_used.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.recently_used.pop(self.recently_used.index(key))
        else:
            if len(self.recently_used) == self.capacity:
                oldest_key = self.recently_used.pop(0)
                del self.cache[oldest_key]
        self.recently_used.append(key)
        self.cache[key] = value


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)