class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.values = {}

    def get(self, key: int) -> int:
        if key in self.values:
            value = self.values[key]
            del self.values[key]
            self.values[key] = value
            return value
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.values:
            del self.values[key]
        if len(self.values.keys()) >= self.capacity:
            if self.values:
                del self.values[list(self.values.keys())[0]]
        self.values[key] = value

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)