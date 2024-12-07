class LRUCache:

    def __init__(self, capacity: int):
        self._cache = dict()
        self._capacity = capacity

    def get(self, key: int) -> int:
        if key in self._cache:
            v = self._cache.pop(key)
            self._cache[key] = v
            return v
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self._cache:
            self._cache.pop(key)
        self._cache[key] = value
        
        if len(self._cache.keys()) > self._capacity:
            ks = list(self._cache.keys())
            self._cache.pop(ks[0])

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)