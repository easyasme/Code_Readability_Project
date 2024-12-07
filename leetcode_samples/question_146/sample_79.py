from collections import deque

class LRUCache:

    def __init__(self, capacity: int):
        self.cache = {}
        self.capacity = capacity
        self.lru = deque([])

    def get(self, key: int) -> int:
        if key in self.cache:
            self.lru.remove(key)
            self.lru.append(key)
            return self.cache[key]
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.lru.remove(key)
        self.cache[key] = value
        self.lru.append(key)

        if len(self.cache) > self.capacity:
            lru_key = self.lru.popleft()
            del self.cache[lru_key]
        # print(self.cache)
        # print(self.lru)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)